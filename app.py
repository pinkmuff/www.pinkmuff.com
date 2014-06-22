## http://www.pinkmuff.com/ code
import os
import re
import sys
import urllib
import bottle
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

_mc = pylibmc.Client(_config['_memcachedServer'])
_m = MongoClient(_config['_mongoServer']['host'],_config['_mongoServer']['port'])
_db = _m[_config['_mongoDb']['name']]
_links = _db[_config['_mongoDb']['links']]

def _debug(_logstring):
 if _config['_debug']:
  logging.debug(str(datetime.datetime.now()) + ": " + _logstring)

@app.error(404)
def error404(error):
 _debug("error404: " + str(error))
 bottle.response.status = 303
 bottle.response.set_header(_config['_error404'][0],_config['_error404'][1])

def generateVideos(_regex = {},offset = 1,category = 'none'):
 i = 0

 _pages_key = _config['_memcachedPrefix'] + '_pages'
 pages = _mc.get(_pages_key)
 if not pages:
  _debug("generateVideos(): memcached empty: " + str(_pages_key))
  pages = (_links.find(_regex).count()) / _config['_numVidsTiled']
  _mc.set(_pages_key,pages,_config['_memcachedPagesTimeout'])

 if offset > pages:
  _debug("generateVideos(): supplied offset more than available pages.")
  bottle.redirect('/')

 if offset > 1:
  skip = _config['_mongoOffset'] + (_config['_numVidsTiled'] * offset)
 else:
  skip = _config['_mongoOffset']

 _metadata_key = _config['_memcachedPrefix'] + '_' + str(category) + '_skip_' + str(skip) 
 metadata = _mc.get(_metadata_key)
 if not metadata:
  _debug("generateVideos(): memcached empty: " + str(_metadata_key))
  metadata = dict()
  for video in _links.find(_regex).sort('_id',-1).skip(skip).limit(_config['_numVidsTiled']):
   _debug("generateVideos(): video = " + str(video))
   video['_id'] = str(video['_id'])
   video['caption'] = video['title'].encode('utf-8').title()
   video['title'] = video['title'].encode('utf-8').replace(' ','-').replace('%','').lower()
   video['title'] = urllib.quote_plus(video['title']) + '/'
   metadata[i] = dict()
   metadata[i] = video
   i += 1

  _mc.set(_metadata_key,metadata,_config['_memcachedVideosTimeout'])

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
 _path = bottle.request.path
 _vars['_config']['_path'] = _path

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

 out['title'] = out['title'].encode('utf-8').replace(' ','-').lower()
 out['title'] = urllib.quote_plus(out['title'])
 uri = '/video/' + str(videoid) + '/' + str(out['title']) + '/'
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
 
 out['caption'] = out['title'].replace('%','').encode('utf-8').title()
 out['title'] = out['title'].replace('%','').encode('utf-8')
 out['tags'] = out['tags'].encode('utf-8').replace(';',' ')
 _vars = templateVars()
 return template(_config['video_template'],dict(out=out,_config=_vars['_config']))

@app.route('/categories/<category>/page/<page>')
def catpageMissingSlash(page):
 try:
  page = int(page)
 except:
  _debug("catpageMissingSlash(): page is not integer")
  bottle.redirect('/')

 if page < _config['_maxPage']:
  if category in _config['_categories']:
   uri = '/categories/' + str(category) + '/page/' + str(page) + '/'
   _debug("catpageMissingSlash(): redirecting to: " + str(uri))
   bottle.redirect(uri)
  else:
   _debug("catpageMissingSlash(): rediecting to /, bad category: " + str(category))
   bottle.redirect('/')
 else:
  _debug("catpageMissingSlash(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/')

@app.route('/categories/<category>/page/<page>/')
def categoryPage(category,page):
 out = dict()
 try:
  c = _config["_categories"][category]
  _regex = re.compile(c[1],re.IGNORECASE)
  _debug("category(): c = " + str(c))
 except:
  _debug("category(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/')

 try:
  page = int(page)
 except:
  _debug("categoryPage(): page is not integer")
  bottle.redirect('/')

 if page < _config['_maxPage']:
  _debug("category(): category = " + str(category))
  _filter = {c[0]:_regex}
  out,pages = generateVideos(_filter,page,c[1])
  _debug("category(): out = " + str(out))
 else:
  _debug("catpageMissingSlash(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/')

 _vars = templateVars()
 _vars['_config']['page'] = page
 _vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 _vars['_config']['active_category'] = category
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

@app.route('/categories/<category>')
def categoryMissingSlash(category):
 if category in _config['_categories']:
  uri = '/categories/' + category + '/'
  _debug("categoryMissingSlash(): redirecting to: " + str(uri))
  bottle.redirect(uri)
 else:
  _debug("categoryMissingSlash(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/')

@app.route('/categories/<category>/')
def category(category):
 out = dict()
 try:
  c = _config["_categories"][category]
  _regex = re.compile(c[1],re.IGNORECASE)
  _debug("category(): c = " + str(c))
 except:
  _debug("category(): _config['_categories'][category] for " + str(category) + " failed.")
  bottle.redirect('/')

 _debug("category(): category = " + str(category))
 _filter = {c[0]:_regex}
 out,pages = generateVideos(_filter,0,c[1])
 _debug("category(): out = " + str(out))

 _vars = templateVars()
 _vars['_config']['uri_prefix'] = '/categories/' + str(category) + '/'
 _vars['_config']['active_category'] = category
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

@app.route('/page/<page>/')
def page(page):
 try:
  page = int(page)
 except:
  _debug("page(): page is not integer")
  bottle.redirect('/')

 if page < _config['_maxPage']:
  out,pages = generateVideos({},page)
 else:
  _debug("page(): redirecting to /, out of bounds page: " + str(page))
  bottle.redirect('/')

 _vars = templateVars()
 _vars['_config']['page'] = page
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

@app.route('/')
def home():
 out,pages = generateVideos()

 _vars = templateVars()
 return template(_config['base_template'],dict(out=out,_config=_vars['_config']))

if __name__ == '__main__':
  _debug("-- Starting up from CLI")
  bottle.run(app=app, host=_config['_standaloneIP'], port=_config['_standalonePort'])
else:
  _debug("-- Starting up from UWSGI")
  app = bottle.default_app()
