import os
import re
import sys
import math
import urllib
import bottle
import random
import logging
import pylibmc
import datetime
from elasticsearch import Elasticsearch
from bson.objectid import ObjectId
from pymongo import MongoClient
from bottle import template
from config import _config, _friends, _categories

def loadConfig(overridePath = ''):
 if not overridePath:
  _cfdir = str(_docroot) + '/config/'
  sys.path.append(_cfdir)
 else:
  if not os.path.isdir(overridePath):
   sys.exit()
  else:
   sys.path.append(overridePath)

 from local_config import _local_config, _local_friends, _local_categories
 _config.update(_local_config)
 _friends.update(_local_friends)
 _categories.update(_local_categories)
 _config['_categories'] = _categories
 _config['_links'] = _friends

_docroot = os.environ.get('_DOCROOT')
loadConfig()
app = application = bottle.Bottle()
_loglevel = logging.DEBUG
_logfile = _docroot + '/' + _config['_appLogFileName']
_logformat = '%(asctime)-15s %(levelname)s %(name)s - %(message)s'
logging.basicConfig(filename=_logfile,level=_loglevel,format=_logformat)
_log = logging.getLogger('pornsite')

_mc = pylibmc.Client(_config['_memcachedServer'], behaviors={"tcp_nodelay": True, "no_block": True})
_mcpool = pylibmc.ThreadMappedPool(_mc)
_m = MongoClient(_config['_mongoServer']['host'],_config['_mongoServer']['port'])
_db = _m[_config['_mongoDb']['name']]
_links = _db[_config['_mongoDb']['links']]
_es = Elasticsearch()

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
   _body = {"query":{"bool":{"should":[ {"match":{_categoryField:_categoryFilter}}, {"match":{'embedLink':'<video'}} ]}}}
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

def _debug(_logstring):
 if _config['_debug']:
  _log.debug(_logstring)

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
 _ua = bottle.request.headers.get('User-Agent')
 isMobile = _detectMobile(_ua)
 _vars = dict()
 _vars['_config'] = dict()
 _vars['_config']['_site_title'] = _config['_site_title']
 _vars['_config']['_by_line'] = _config['_by_line']
 _vars['_config']['_staticHost'] = _config['_staticHost']
 _vars['_config']['_twitter'] = _config['_twitter']
 _vars['_config']['_email'] = _config['_email']
 _vars['_config']['_btc_donate'] = _config['_btc_donate']

 _vars['_config']['footer_popunder'] = _config['footer_popunder']

 if not isMobile:
  _vars['_config']['main_page_ad'] = _config['main_page_ad']
  _vars['_config']['video_page_ad'] = _config['video_page_ad']
 else:
  _vars['_config']['main_page_ad'] = '<br>'
  _vars['_config']['video_page_ad'] = '<br>'
  
 _vars['_config']['_links'] = _config['_links']
 _vars['_config']['_categories'] = _config['_categories']
 _vars['_config']['META_KEYWORDS'] = _config['META_KEYWORDS']
 _vars['_config']['META_DESCRIPTION'] = _config['META_DESCRIPTION']
 _vars['_config']['MS_VALIDATE'] = _config['MS_VALIDATE']
 _vars['_config']['YANDEX_VERIFICATION'] = _config['YANDEX_VERIFICATION']
 _vars['_config']['GOOGLE_SITE_VERIFICATION'] = _config['GOOGLE_SITE_VERIFICATION']
 _vars['_config']['_ga_code'] = _config['_ga_code']
 _vars['_config']['_ga_site'] = _config['_ga_site']
 _vars['_config']['page'] = 1
 _vars['_config']['uri_prefix'] = '/'
 _vars['_config']['active_category'] = 'Home'
 _vars['_config']['_site_css'] = _config['_site_css']
 _path = bottle.request.path
 _vars['_config']['_path'] = _path
 _vars['_config']['marquee'] = _config['marquee']
 _vars['_config']['text_color'] = _config['text_color']
 _vars['_config']['search_placeholder'] = _config['search_placeholder']

 _vars['_config']['adbar'] = _config['main_page_ad']
 return _vars

@app.route('/about')
def aboutMissingSlash():
 _debug("aboutMissingSlash():  /about missing trailing /")
 bottle.redirect('/about/',code=301)

@app.route('/about/')
def about():
 _debug("about():  displaying about info")
 _vars = templateVars()
 return template(_config['about_template'],dict(_config=_vars['_config']))

@app.route('/video/<videoid>')
@app.route('/video/<videoid>/')
@app.route('/video/<videoid>/<title>')
def videoMissingSlash(videoid,title=''):
 _debug("videoMissingSlash(): videoid = " + str(videoid))
 _debug(type(videoid))
 out = _links.find_one({'_id': ObjectId(videoid)})
 _debug("videoMissingSlash(): mongo find_one = " + str(out))
 if not out:
  bottle.redirect('/',code=301)

 out = _sanitize(out)
 uri = '/video/' + str(videoid) + '/' + str(out['uri'])
 _debug("videoMissingSlash(): redirecting to: " + str(uri))
 bottle.redirect(uri,code=301)

@app.route('/video/<videoid>/<title>/')
def showvideo(videoid,title):
 _debug("showvideo(): videoid = " + str(videoid) + ".")
 videoid = unicode(videoid)
 _debug(type(videoid))
 _debug(videoid)
 out = _links.find_one({'_id': ObjectId(videoid)})
 if not out:
  _debug("showvideo(): mongo find_one out = " + str(out))
  
  bottle.redirect('/',code=301)
 
 if not '_viewcount' in out:
  out['_viewcount'] = 1
 else:
  out['_viewcount'] += 1

 _links.save(out)

 out = _sanitize(out)
 _vars = templateVars()
 _vars['_config']['adbar'] = _config['video_page_ad']
 
 return template(_config['video_template'],dict(out=out,_config=_vars['_config']))

@app.route('/categories/<category>/random/')
def randomCatPage(category):
 _pages_key = _config['_memcachedPrefix'] + '_pages_' + str(category)

 try:
  c = _config["_categories"][category]
  _debug("randomCatPage(): c = " + str(c))
 except:
  _debug("randomCatPage(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/',code=301)

 _debug("randomCatPage(): category = " + str(category))
 _filter = _genFilter(c[0],c[1])
 out,pages = generateVideos(_filter,"rand",c[1])
 _debug("randomCatPage(): out = " + str(out))

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 _vars['_config']['active_category'] = c[2]
 _vars['_config']['pages'] = pages

 try:
  _vars['_config']['footer_popunder'] = c[3]
 except:
  pass

 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

@app.route('/categories/<category>/random')
@app.route('/categories/<category>')
def categoryMissingSlash(category):
 if category in _config['_categories']:
  uri = bottle.request.path + '/'
  _debug("categoryMissingSlash(): redirecting to: " + str(uri))
  bottle.redirect(uri,code=301)
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
  c = _config["_categories"][category]
  _debug("category(): c = " + str(c))
 except:
  _debug("category(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/',code=301)

 if page < _config['_maxPage']:
  _debug("category(): category = " + str(category))
  _filter = _genFilter(c[0],c[1])
  out,pages = generateVideos(_filter,page,c[1])

  _debug("category(): out = " + str(out))
 else:
  _debug("category(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 _vars['_config']['active_category'] = c[2]
 _vars['_config']['page'] = page
 _vars['_config']['pages'] = pages
 try:
  _vars['_config']['footer_popunder'] = c[3]
 except:
  pass
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

@app.route('/page/<page>')
def pageMissingSlash(page):
 try:
  page = int(page)
 except:
  _debug("pageMissingSlash(): page is not integer")
  bottle.redirect('/',code=301)

 if page < _config['_maxPage']:
  uri = '/page/' + str(page) + '/'
  bottle.redirect(uri,code=301)
 else:
  _debug("pageMissingSlash(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

@app.route('/about/random/')
@app.route('/random')
def randomMissingSlash():
 bottle.redirect('/random/',code=301)

@app.route('/random/')
def randomPage():
 out,pages = generateVideos({},"rand")
  
 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/'
 _vars['_config']['pages'] = pages
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

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

 _strip = re.compile('([^\s\w]|_)+')
 term = _strip.sub('',term)

 if page < _config['_maxPage']:
  _filter = _genFilter("tags",term)
  _term = term.replace(' ','')
  _cat = "search_" + str(_term) 
  out,pages = generateVideos(_filter,page,_cat)
 else:
  _debug("search(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/search/' + str(term) + '/'
 _vars['_config']['page'] = page
 _vars['_config']['pages'] = pages
 _vars['_config']['search_placeholder'] = term
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))


@app.route('/page/<page>/')
@app.route('/')
def home(page=1):
 try:
  page = int(page)
 except:
  _debug("home(): page is not an integer")
  bottle.redirect('/',code=301)

 if page < _config['_maxPage']:
  _filter = _genFilter()
  out,pages = generateVideos(_filter,page,'none')
 else:
  _debug("home(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/',code=301)

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/'
 _vars['_config']['page'] = page
 _vars['_config']['pages'] = pages
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

if __name__ == '__main__':
  _debug("-- Starting up from CLI")
  bottle.run(app=app, host=_config['_standaloneIP'], port=_config['_standalonePort'])
else:
  _debug("-- Starting up from UWSGI")
  app = bottle.default_app()
