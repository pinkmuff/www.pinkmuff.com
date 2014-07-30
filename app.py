import os
import re
import sys
import json
import math
import urllib
import bottle
import random
import logging
import pylibmc
import datetime
from copy import deepcopy
from elasticsearch import Elasticsearch
from bson.objectid import ObjectId
from pymongo import MongoClient
from bottle import template
from config import _config

def _debug(_logstring):
 if _config['_debug']:
  _log.debug(_logstring)

def loadConfig(path = './conf.d/'):
 if not os.path.isdir(path):
  _debug("loadConfig(): path is not a directory: " + str(path))
 else:
  _configs = os.listdir(path)
  for _f in _configs:
   _p = path + '/' + _f
   _debug("loadConfig(): checking: " + str(_p))
   if os.path.isfile(_p):
    if ".json" in _p:
     _fh = open(_p,'r')
     _fc = _fh.read()
     _tmp = json.loads(_fc)
     _overrides[_tmp['vhost']] = _tmp
     _debug("loadConfig():  loaded vhost: " + str(_tmp['vhost']) + " with values: " + str(_tmp))

app = application = bottle.Bottle()
_loglevel = logging.DEBUG
_logfile = _config['_logroot'] + '/' + _config['_appLogFileName']
_logformat = '%(asctime)-15s %(levelname)s %(name)s - %(message)s'
logging.basicConfig(filename=_logfile,level=_loglevel,format=_logformat)
_log = logging.getLogger('pornsite')
_overrides = dict()
loadConfig(_config['_conf_d'])

_mc = pylibmc.Client(_config['_memcachedServer'], behaviors={"tcp_nodelay": True, "no_block": True})
_mcpool = pylibmc.ThreadMappedPool(_mc)
_m = MongoClient(_config['_mongoServer']['host'],_config['_mongoServer']['port'])
_db = _m[_config['_mongoDb']['name']]
_links = _db[_config['_mongoDb']['links']]
_es = Elasticsearch()
_strip = re.compile('([^\s\w]|_)+')

def _detectMobile(_ua):
 if not _ua:
  return False

 for _mua in _config['_mobile_ua']:
  if _mua in _ua:
   return True

 return False

def _genFilter(_categoryField='',_categoryFilter=''):
 _ua = bottle.request.headers.get('User-Agent')
 _isMobile = _detectMobile(_ua)
 if _isMobile:
  if _categoryField and _categoryFilter:
   _debug("_genFilter(): mobile regex, _categoryField = " + str(_categoryField) + ", _categoryFilter = " + str(_categoryFilter))
   _body = {"query":{"bool":{"must":{"term":{_categoryField:_categoryFilter}},"should":{"term":{"embedLink":"<video"}}}}}
  else:
   _debug("_genFilter(): mobile regex, no category")
   _body = {"query":{"match":{'embedLink':'<video'}}}

 else:
  if _categoryField and _categoryFilter:
   _debug("_genFilter(): _categoryField = " + str(_categoryField) + ", _categoryFilter = " + str(_categoryFilter))
   _body = {"query":{"match":{_categoryField:_categoryFilter}}}
  else:
   _debug("_genFilter(): generating empty set.")
   _body = {}

 return _body

def _sanitize(video):
 _debug("_sanitize(): input object: " + str(video))
 uri = re.sub(r'[^\x00-\x7F]+',' ', video['title'])
 uri = ' '.join(uri.split())
 uri = uri.replace(' ','-').replace('%','').replace('?','').replace('/','').lower()
 uri = urllib.quote(uri.encode('utf-8'))

 if not uri:
  video['uri'] = video['tags'].replace(';','-')
  video['uri'] = urllib.quote(video['uri'].encode('utf-8')) + '/'
 else:
  video['uri'] = uri + '/'

 video['_id'] = str(video['_id'])
 video['title'] = video['title'].encode('utf-8').title()
 video['tags'] = video['tags'].encode('utf-8')
 if 'duration' in video:
  video['duration'] = int(math.ceil(int(video['duration'])/60))

 _debug("_sanitize(): output object: " + str(video))
 return video

def _cache_set(_key,_value,_timeout):
 if _config['_memcachedEnabled']:
  if _mcpool != None:
   with _mcpool.reserve() as mc:
    _debug("_cache_set(): setting memcached key: " + str(_key) + ", timeout: " + str(_timeout) + ", value: " + str(_value))
    out = mc.set(_key,_value,_timeout)
  
  _mcpool.relinquish()
  return out
 else:
  return True

def _cache_get(_key):
 if _config['_memcachedEnabled']:
  if _mcpool != None:
   with _mcpool.reserve() as mc:
    out = mc.get(_key)
    _debug("_cache_get(): getting memcached key: " + str(_key) + ", value: " + str(out))
   
   _mcpool.relinquish()
   return out
  else:
   return None
 else:
  return None

@app.error(404)
def error404(error):
 _debug("error404: " + str(error))
 bottle.response.status = 301
 bottle.response.set_header(_config['_error404'][0],_config['_error404'][1])

def generateVideos(_find = {},offset = 1,category = 'none'):
 i = 0
 _ua = bottle.request.headers.get('User-Agent')
 mobile = _detectMobile(_ua)

 _pages_key = _config['_memcachedPrefix'] + '_pages_' + str(category)
 if mobile:
  _pages_key = _pages_key + '_mobile'

 pages = _cache_get(_pages_key)
 if not pages:
  pages = 1
  _page_cache_empty = True
 else:
  _page_cache_empty = False

 if offset == "rand":
  if pages > 1:
   skip = random.randint(0,int(pages))
  else:
   skip = 1
 elif offset > 1:
  skip = _config['_mongoOffset'] + (_config['_numVidsTiled'] * offset)
 else:
  skip = _config['_mongoOffset']

 _debug("generateVideos(): skip = " + str(skip))

 _esr_key = _config['_memcachedPrefix'] + '_' + str(category) + '_skip_' + str(skip)
 if mobile: 
  _esr_key = _esr_key + '_mobile'

 _esr = _cache_get(_esr_key)
 if not _esr:
  _esr = _es.search(index=_config['_esIndex'], size=_config['_numVidsTiled'], from_=skip, body=_find, sort='_uid:desc')
  if _page_cache_empty:
   _debug("generateVideos(): setting memcached key " + str(_pages_key) + " to " + str(_esr['hits']['total']))
   pages = int(_esr['hits']['total']) / int(_config['_numVidsTiled'])
   _cache_set(_pages_key,pages,_config['_memcachedPagesTimeout'])

  _cache_set(_esr_key,_esr,_config['_memcachedVideosTimeout'])

 metadata = dict()
 for _v in _esr['hits']['hits']:
  try:
   video = _v['_source']
  except:
   _debug("generateVideos(): failed: _v = " + str(_v['source']))
   continue

  _debug("generateVideos(): video = " + str(video))
  video = _sanitize(video)
  metadata[i] = dict()
  metadata[i] = video
  i += 1

 if pages == 1:
  pages = 10
 return metadata,pages

def templateVars():
 bottle.LocalRequest._vars = dict()
 bottle.LocalRequest._vars['_config'] = deepcopy(_config)
 _ua = bottle.request.headers.get('User-Agent')
 isMobile = _detectMobile(_ua)

 _hh = bottle.request.headers.get('Host')

 if _hh in _overrides:
  _debug("templateVars():  found override for host header: " + str(_hh))
  bottle.LocalRequest._vars['_config'].update(_overrides[_hh])

 bottle.LocalRequest._vars['_config']['_path'] = bottle.request.path
 bottle.LocalRequest._vars['_config']['active_category'] = 'Home'
 bottle.LocalRequest._vars['_config']['uri_prefix'] = 1
 bottle.LocalRequest._vars['_config']['page'] = 1
 bottle.LocalRequest._vars['_config']['adbar'] = _config['main_page_ad']
 return bottle.LocalRequest._vars

@app.route('/about')
def aboutMissingSlash():
 _debug("aboutMissingSlash():  /about missing trailing /")
 bottle.redirect('/about/',code=301)

@app.route('/about/')
def about():
 _debug("about():  displaying about info")
 bottle.LocalRequest._vars = templateVars()
 return template(bottle.LocalRequest._vars['_config']['about_template'],dict(_config=bottle.LocalRequest._vars['_config']))

@app.route('/video/<videoid>')
@app.route('/video/<videoid>/')
@app.route('/video/<videoid>/<title>')
def videoMissingSlash(videoid,title=''):
 _debug("videoMissingSlash(): videoid = " + str(videoid))
 _debug(type(videoid))
 bottle.LocalRequest.out = _links.find_one({'_id': ObjectId(videoid)})
 _debug("videoMissingSlash(): mongo find_one = " + str(bottle.LocalRequest.out))
 if not bottle.LocalRequest.out:
  bottle.redirect('/',code=301)

 bottle.LocalRequest.out = _sanitize(bottle.LocalRequest.out)
 bottle.LocalRequest.uri = '/video/' + str(videoid) + '/' + str(bottle.LocalRequest.out['uri'])
 _debug("videoMissingSlash(): redirecting to: " + str(bottle.LocalRequest.uri))
 bottle.redirect(uri,code=301)

@app.route('/video/<videoid>/<title>/')
def showvideo(videoid,title):
 _debug("showvideo(): videoid = " + str(videoid) + ".")
 bottle.LocalRequest.out = _links.find_one({'_id': ObjectId(videoid)})
 if not bottle.LocalRequest.out:
  _debug("showvideo(): mongo find_one out = " + str(bottle.LocalRequest.out))
  
  bottle.redirect('/',code=301)
 
 if not '_viewcount' in bottle.LocalRequest.out:
  bottle.LocalRequest.out['_viewcount'] = 1
 else:
  bottle.LocalRequest.out['_viewcount'] += 1

 _links.save(bottle.LocalRequest.out)

 bottle.LocalRequest.out = _sanitize(bottle.LocalRequest.out)
 bottle.LocalRequest._vars = templateVars()
 bottle.LocalRequest._vars['_config']['adbar'] = _config['video_page_ad']
 
 return template(bottle.LocalRequest._vars['_config']['video_template'],dict(out=bottle.LocalRequest.out,_config=bottle.LocalRequest._vars['_config']))

@app.route('/categories/<category>/random/')
def randomCatPage(category):
 bottle.LocalRequest._pages_key = _config['_memcachedPrefix'] + '_pages_' + str(category)

 try:
  bottle.LocalRequest.c = _config["_categories"][category]
  _debug("randomCatPage(): c = " + str(bottle.LocalRequest.c))
 except:
  _debug("randomCatPage(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/',code=301)

 _debug("randomCatPage(): category = " + str(category))
 bottle.LocalRequest._filter = _genFilter(bottle.LocalRequest.c[0],bottle.LocalRequest.c[1])
 bottle.LocalRequest.out,bottle.LocalRequest.pages = generateVideos(bottle.LocalRequest._filter,"rand",bottle.LocalRequest.c[1])
 _debug("randomCatPage(): out = " + str(bottle.LocalRequest.out))

 bottle.LocalRequest._vars = templateVars()
 bottle.LocalRequest._vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 bottle.LocalRequest._vars['_config']['active_category'] = bottle.LocalRequest.c[2]
 bottle.LocalRequest._vars['_config']['pages'] = bottle.LocalRequest.pages

 return template(bottle.LocalRequest._vars['_config']['base_template'],dict(out=bottle.LocalRequest.out,_config=bottle.LocalRequest._vars['_config']))

@app.route('/categories/<category>/random')
@app.route('/categories/<category>')
def categoryMissingSlash(category):
 if category in _config['_categories']:
  bottle.LocalRequest.uri = bottle.request.path + '/'
  _debug("categoryMissingSlash(): redirecting to: " + str(bottle.LocalRequest.uri))
  bottle.redirect(bottle.LocalRequest.uri,code=301)
 else:
  _debug("categoryMissingSlash(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/',code=301)

@app.route('/categories/<category>/page/<page>/')
@app.route('/categories/<category>/')
def category(category,page=1):
 try:
  page = int(page)
 except:
  _debug("category(): page is not an integer")
  bottle.redirect('/',code=301)

 try:
  bottle.LocalRequest.c = _config["_categories"][category]
  _debug("category(): c = " + str(bottle.LocalRequest.c))
 except:
  _debug("category(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/',code=301)

 if page < _config['_maxPage']:
  _debug("category(): category = " + str(category))
  bottle.LocalRequest._filter = _genFilter(bottle.LocalRequest.c[0],bottle.LocalRequest.c[1])
  bottle.LocalRequest.out,bottle.LocalRequest.pages = generateVideos(bottle.LocalRequest._filter,page,bottle.LocalRequest.c[1])

  _debug("category(): out = " + str(bottle.LocalRequest.out))
 else:
  _debug("category(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

 bottle.LocalRequest._vars = templateVars()
 bottle.LocalRequest._vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 bottle.LocalRequest._vars['_config']['active_category'] = bottle.LocalRequest.c[2]
 bottle.LocalRequest._vars['_config']['page'] = page
 bottle.LocalRequest._vars['_config']['pages'] = bottle.LocalRequest.pages
 return template(bottle.LocalRequest._vars['_config']['base_template'],dict(out=bottle.LocalRequest.out,_config=bottle.LocalRequest._vars['_config']))

@app.route('/page/<page>')
def pageMissingSlash(page):
 try:
  page = int(page)
 except:
  _debug("pageMissingSlash(): page is not integer")
  bottle.redirect('/',code=301)

 if page < _config['_maxPage']:
  bottle.LocalRequest.uri = '/page/' + str(page) + '/'
  bottle.redirect(bottle.LocalRequest.uri,code=301)
 else:
  _debug("pageMissingSlash(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

@app.route('/about/random/')
@app.route('/random')
def randomMissingSlash():
 bottle.redirect('/random/',code=301)

@app.route('/random/')
def randomPage():
 bottle.LocalRequest.out,bottle.LocalRequest.pages = generateVideos({},"rand")
  
 bottle.LocalRequest._vars = templateVars()
 bottle.LocalRequest._vars['_config']['uri_prefix'] = '/'
 bottle.LocalRequest._vars['_config']['pages'] = bottle.LocalRequest.pages
 return template(bottle.LocalRequest._vars['_config']['base_template'],dict(out=bottle.LocalRequest.out,_config=bottle.LocalRequest._vars['_config']))

@app.route('/search/<term>')
@app.route('/search/')
@app.route('/search')
def searchMissing(term=False):
 bottle.redirect('/',code=301)
 
@app.route('/search/<term>/page/<page>/')
@app.route('/search/<term>/')
def search(term,page=1):
 try:
  page = int(page)
 except:
  _debug("search(): page is not an integer")
  bottle.redirect('/',code=301)

 bottle.LocalRequest.term = _strip.sub('',term)

 if page < _config['_maxPage']:
  bottle.LocalRequest._filter = _genFilter("tags",bottle.LocalRequest.term)
  bottle.LocalRequest._term = bottle.LocalRequest.term.replace(' ','')
  bottle.LocalRequest._cat = "search_" + str(bottle.LocalRequest._term) 
  bottle.LocalRequest.out,bottle.LocalRequest.pages = generateVideos(bottle.LocalRequest._filter,page,bottle.LocalRequest._cat)
 else:
  _debug("search(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

 bottle.LocalRequest._vars = templateVars()
 bottle.LocalRequest._vars['_config']['uri_prefix'] = '/search/' + str(bottle.LocalRequest.term) + '/'
 bottle.LocalRequest._vars['_config']['page'] = page
 bottle.LocalRequest._vars['_config']['pages'] = bottle.LocalRequest.pages
 bottle.LocalRequest._vars['_config']['search_placeholder'] = bottle.LocalRequest.term
 return template(bottle.LocalRequest._vars['_config']['base_template'],dict(out=bottle.LocalRequest.out,_config=bottle.LocalRequest._vars['_config']))


@app.route('/page/<page>/')
@app.route('/')
def home(page=1):
 try:
  page = int(page)
 except:
  _debug("home(): page is not an integer")
  bottle.redirect('/',code=301)

 if page < _config['_maxPage']:
  bottle.LocalRequest._filter = _genFilter()
  bottle.LocalRequest.out,bottle.LocalRequest.pages = generateVideos(bottle.LocalRequest._filter,page,'none')
 else:
  _debug("home(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

 bottle.LocalRequest._vars = templateVars()
 bottle.LocalRequest._vars['_config']['uri_prefix'] = '/'
 bottle.LocalRequest._vars['_config']['page'] = page
 bottle.LocalRequest._vars['_config']['pages'] = bottle.LocalRequest.pages
 return template(bottle.LocalRequest._vars['_config']['base_template'],dict(out=bottle.LocalRequest.out,_config=bottle.LocalRequest._vars['_config']))

if __name__ == '__main__':
  _debug("-- Starting up from CLI")
  bottle.run(app=app, host=_config['_standaloneIP'], port=_config['_standalonePort'])
else:
  _debug("-- Starting up from UWSGI")
  app = bottle.default_app()
