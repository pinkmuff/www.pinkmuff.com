import os
import re
import sys
import urllib
import bottle
import random
import logging
import datetime
import pylibmc
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
logging.basicConfig(filename=_logfile,level=_loglevel)

_mc = pylibmc.Client(_config['_memcachedServer'], behaviors={"tcp_nodelay": True, "no_block": True})
_m = MongoClient(_config['_mongoServer']['host'],_config['_mongoServer']['port'])
_db = _m[_config['_mongoDb']['name']]
_links = _db[_config['_mongoDb']['links']]

def _detectMobile(_ua):
 for _mua in _config['_mobile_ua']:
  if _mua in _ua:
   return True

 return False

def _genRegex(_isMobile,_categoryField='',_categoryFilter=''):
 if _isMobile:
  _regex = re.compile('^<video',re.IGNORECASE)

  if _categoryField and _categoryFilter:
   _debug("_genRegex(): mobile regex, _categoryField = " + str(_categoryField) + ", _categoryFilter = " + str(_categoryFilter))
   _catregex = re.compile(_categoryFilter,re.IGNORECASE)
   _filter = {'embedLink':_regex,_categoryField:_catregex}
  else:
   _debug("_genRegex(): mobile regex, no category")
   _filter = {'embedLink':_regex} 

 else:
  if _categoryField and _categoryFilter:
   _debug("_genRegex(): _categoryField = " + str(_categoryField) + ", _categoryFilter = " + str(_categoryFilter))
   _catregex = re.compile(_categoryFilter,re.IGNORECASE)
   _filter = {_categoryField:_catregex}
  else:
   _debug("_genRegex(): generating empty set.")
   _filter = {}

 return _filter 

def _sanitize(video):
 _debug("_sanitize(): input object: " + str(video))
 uri = re.sub(r'[^\x00-\x7F]+',' ', video['title'])
 uri = ' '.join(uri.split())
 uri = uri.replace(' ','-').replace('%','').replace('?','').replace('/','').lower()
 uri = urllib.quote(uri.encode('utf-8'))
 video['uri'] = uri + '/'
 video['_id'] = str(video['_id'])
 video['title'] = video['title'].encode('utf-8').title()
 video['tags'] = video['tags'].encode('utf-8')
 _debug("_sanitize(): output object: " + str(video))
 return video

def _cache_set(_key,_value,_timeout):
 if _config['_memcachedEnabled']:
  _debug("_cache_set(): setting memcached key: " + str(_key) + ", timeout: " + str(_timeout) + ", value: " + str(_value))
  out = _mc.set(_key,_value,_timeout)
  return out
 else:
  return True

def _cache_get(_key):
 if _config['_memcachedEnabled']:
  out = _mc.get(_key)
  _debug("_cache_get(): getting memcached key: " + str(_key) + ", value: " + str(out))
  return out
 else:
  return None

def _debug(_logstring):
 if _config['_debug']:
  logging.debug(str(datetime.datetime.now()) + ": " + _logstring)

@app.error(404)
def error404(error):
 _debug("error404: " + str(error))
 bottle.response.status = 303
 bottle.response.set_header(_config['_error404'][0],_config['_error404'][1])

def generateVideos(_regex = {},offset = 1,category = 'none',mobile=False):
 i = 0

 _pages_key = _config['_memcachedPrefix'] + '_pages_' + str(category)
 if mobile:
  _pages_key = _pages_key + '_mobile'

 pages = _cache_get(_pages_key)
 if not pages:
  _debug("generateVideos(): memcached empty: " + str(_pages_key) + ", pages = " + str(pages))
  pages = (_links.find(_regex).count()) / _config['_numVidsTiled']
  _debug("generateVideos(): _regex = " + str(_regex) + ", pages = " + str(pages))
  _cache_set(_pages_key,pages,_config['_memcachedPagesTimeout'])

 _debug("generateVideos(): pages = " + str(pages))
 if offset > pages:
  _debug("generateVideos(): supplied offset more than available pages.  offset = " + str(offset))
  bottle.redirect('/')

 if offset > 1:
  skip = _config['_mongoOffset'] + (_config['_numVidsTiled'] * offset)
 else:
  skip = _config['_mongoOffset']

 _metadata_key = _config['_memcachedPrefix'] + '_' + str(category) + '_skip_' + str(skip) 
 if mobile:
  _metadata_key = _metadata_key + '_mobile'

 metadata = _cache_get(_metadata_key)
 if not metadata:
  _debug("generateVideos(): memcached empty: " + str(_metadata_key))
  metadata = dict()
  for video in _links.find(_regex).sort('_id',-1).skip(skip).limit(_config['_numVidsTiled']).hint([('_id',1)]):
   _debug("generateVideos(): video = " + str(video))
   video = _sanitize(video)
   metadata[i] = dict()
   metadata[i] = video
   i += 1

 _cache_set(_metadata_key,metadata,_config['_memcachedVideosTimeout'])
 
 return metadata,pages

def templateVars():
 _vars = dict()
 _vars['_config'] = dict()
 _vars['_config']['_site_title'] = _config['_site_title']
 _vars['_config']['_by_line'] = _config['_by_line']
 _vars['_config']['_staticHost'] = _config['_staticHost']
 _vars['_config']['_twitter'] = _config['_twitter']
 _vars['_config']['_email'] = _config['_email']
 _vars['_config']['_btc_donate'] = _config['_btc_donate']
 _vars['_config']['main_page_ad'] = _config['main_page_ad']
 _vars['_config']['video_page_ad'] = _config['video_page_ad']
 _vars['_config']['footer_ad'] = _config['footer_ad']
 _vars['_config']['footer_popunder'] = _config['footer_popunder']
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

 return _vars

@app.route('/about')
def aboutMissingSlash():
 _debug("aboutMissingSlash():  /about missing trailing /")
 bottle.redirect('/about/')

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
 try:
  out = _links.find_one({'_id': ObjectId(videoid)})
  _debug("videoMissingSlash(): mongo find_one = " + str(out))
 except:
  _debug("videoMissingSlash(): mongo find_one except")
  bottle.redirect('/')

 out = _sanitize(out)
 uri = '/video/' + str(videoid) + '/' + str(out['uri'])
 _debug("videoMissingSlash(): redirecting to: " + str(uri))
 bottle.redirect(uri)

@app.route('/video/<videoid>/<title>/')
def showvideo(videoid,title):
 _debug("showvideo(): videoid = " + str(videoid))
 _debug("showvideo(): title = " + str(title))
 try:
  out = _links.find_one({'_id': ObjectId(videoid)})
  _debug("showvideo(): mongo find_one = " + str(out))
 except:
  _debug("showvideo(): mongo find_one except")
  bottle.redirect('/')
 
 out = _sanitize(out)
 _vars = templateVars()
 
 return template(_config['video_template'],dict(out=out,_config=_vars['_config']))

@app.route('/categories/<category>/random/')
def randomCatPage(category):
 _ua = bottle.request.headers.get('User-Agent')
 _isMobile = _detectMobile(_ua)
 _pages_key = _config['_memcachedPrefix'] + '_pages_' + str(category)

 if _isMobile:
  _pages_key = _pages_key + '_mobile'

 _pages = _cache_get(_pages_key)
 if not _pages:
  _rand = 0
 else:
  _rand = random.randint(0,_pages) 
 
 try:
  c = _config["_categories"][category]
  _regex = re.compile(c[1],re.IGNORECASE)
  _debug("randomCatPage(): c = " + str(c))
 except:
  _debug("randomCatPage(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/')

 _debug("randomCatPage(): category = " + str(category))
 if _isMobile:
  _filter = _genRegex(True,c[0],c[1])
  out,pages = generateVideos(_filter,_rand,c[1],True)
 else:
  _filter = _genRegex(False,c[0],c[1])
  out,pages = generateVideos(_filter,_rand,c[1])

 _debug("randomCatPage(): out = " + str(out))

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 _vars['_config']['active_category'] = category
 _vars['_config']['pages'] = pages
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

@app.route('/categories/<category>/random')
@app.route('/categories/<category>')
def categoryMissingSlash(category):
 if category in _config['_categories']:
  uri = bottle.request.path + '/'
  _debug("categoryMissingSlash(): redirecting to: " + str(uri))
  bottle.redirect(uri)
 else:
  _debug("categoryMissingSlash(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/')

@app.route('/categories/<category>/page/<page>/')
@app.route('/categories/<category>/')
def category(category,page=0):
 try:
  page = int(page)
 except:
  _debug("category(): page is not an integer")
  bottle.redirect('/')

 try:
  c = _config["_categories"][category]
  _debug("category(): c = " + str(c))
 except:
  _debug("category(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/')

 if page < _config['_maxPage']:
  _debug("category(): category = " + str(category))
  _ua = bottle.request.headers.get('User-Agent')
  _isMobile = _detectMobile(_ua)
  if _isMobile:
   _debug("category(): detected mobile")
   _filter = _genRegex(True,c[0],c[1])
   out,pages = generateVideos(_filter,page,c[1],True)
  else:
   _debug("category(): desktop")
   _filter = _genRegex(False,c[0],c[1])
   out,pages = generateVideos(_filter,page,c[1])

  _debug("category(): out = " + str(out))
 else:
  _debug("category(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/')

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 _vars['_config']['active_category'] = category
 _vars['_config']['page'] = page
 _vars['_config']['pages'] = pages
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

@app.route('/page/<page>')
def pageMissingSlash(page):
 try:
  page = int(page)
 except:
  _debug("pageMissingSlash(): page is not integer")
  bottle.redirect('/')

 if page < _config['_maxPage']:
  uri = '/page/' + str(page) + '/'
  bottle.redirect(uri)
 else:
  _debug("pageMissingSlash(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/')

@app.route('/about/random/')
@app.route('/random')
def randomMissingSlash():
 bottle.redirect('/random/')

@app.route('/random/')
def randomPage():
 _ua = bottle.request.headers.get('User-Agent')
 _isMobile = _detectMobile(_ua)
 _pages_key = _config['_memcachedPrefix'] + '_pages_none'

 if _isMobile:
  _pages_key = _pages_key + '_mobile'

 _pages = _cache_get(_pages_key)
 if not _pages:
  _rand = 0
 else:
  _rand = random.randint(0,_pages)
 
 if _isMobile:
  out,pages = generateVideos({},_rand,'none',True)
 else:
  out,pages = generateVideos({},_rand)
  
 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/'
 _vars['_config']['pages'] = pages
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))
 
@app.route('/page/<page>/')
@app.route('/')
def home(page=0):
 try:
  page = int(page)
 except:
  _debug("home(): page is not an integer")
  bottle.redirect('/')

 _ua = bottle.request.headers.get('User-Agent')
 _isMobile = _detectMobile(_ua)
 if page < _config['_maxPage']:
  if _isMobile:
   _filter = _genRegex(True)
   out,pages = generateVideos(_filter,page,'none',True)
  else:
   _filter = _genRegex(False)
   out,pages = generateVideos(_filter,page)
 else:
  _debug("home(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/')

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
