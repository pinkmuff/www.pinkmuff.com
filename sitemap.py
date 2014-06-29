#!/usr/bin/python

import os
import re
import sys
import math
import urllib
from pymongo import MongoClient
from config import _config, _friends, _categories

if len(sys.argv) != 2:
 print "Usage: " + sys.argv[0] + " [www.domain.com] > sitemap.xml"
 sys.exit()

def _sanitize(video):
 uri = re.sub(r'[^\x00-\x7F]+',' ', video['title'])
 uri = ' '.join(uri.split())
 uri = uri.replace(' ','-').replace('%','').lower()
 uri = urllib.quote(uri.encode('utf-8'))
 video['uri'] = uri + '/'
 video['_id'] = str(video['_id'])
 video['title'] = video['title'].encode('utf-8').title()

 return video

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

_cfgdir = "/var/www/" + sys.argv[1] + "/config"

loadConfig(_cfgdir)

_m = MongoClient(_config["_mongoServer"]["host"],_config["_mongoServer"]["port"])
_db = _m[_config["_mongoDb"]["name"]]
links = _db[_config["_mongoDb"]["links"]]
_split = 49000
_dbcount = links.count()
_loops = int(math.ceil(float(_dbcount)/float(_split)))

for i in xrange(_loops):
 _sitemap = 'sitemap.' + str(i) + '.xml'
 _fh = open(_sitemap,'w')
 domain = 'http://' + str(sys.argv[1]) + '/'
 out = '<?xml version="1.0" encoding="UTF-8" ?>\n'
 out += ' <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 if i == 0:
  out += '  <url>\n'
  out += '   <loc>' + domain + '</loc>\n'
  out += '   <priority>1.0</priority>\n'
  out += '   <changefreq>hourly</changefreq>\n'
  out += '  </url>\n'
  out += '  <url>\n'
  out += '   <loc>' + domain + 'random/</loc>\n'
  out += '   <priority>1.0</priority>\n'
  out += '   <changefreq>hourly</changefreq>\n'
  out += '  </url>\n'
  _fh.write(out)

  for cat,v in _config['_categories'].iteritems():
   out = ''
   out += '  <url>\n'
   out += '   <loc>' + domain + 'categories/' + cat + '/</loc>\n'
   out += '   <priority>1.0</priority>\n'
   out += '   <changefreq>hourly</changefreq>\n'
   out += '  </url>\n'
   out += '  <url>\n'
   out += '   <loc>' + domain + 'categories/' + cat + '/random/</loc>\n'
   out += '   <priority>1.0</priority>\n'
   out += '   <changefreq>hourly</changefreq>\n'
   out += '  </url>\n'

   _fh.write(out)

 _fh.write(out)
 _skip = int(i) * int(_split)
 for video in links.find().sort('_id',-1).skip(_skip).limit(_split):
  out = ''
  video = _sanitize(video)
  out += '  <url>\n'
  out += '   <loc>' + domain + 'video/' + str(video['_id']) + '/' + video['uri'] + '</loc>\n'
  out += '   <changefreq>weekly</changefreq>\n'
  out += '  </url>\n'

  try:
   _fh.write(out)
  except: 
   continue

 out = ' </urlset>\n'
 
 _fh.write(out)
 _fh.close()


_fh = open('sitemap.index.xml','w')
out = '<?xml version="1.0" encoding="UTF-8"?>\n'
out += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for i in xrange(_loops):
 out += ' <sitemap>\n' 
 out += '  <loc>' + domain + 'sitemap.' + str(i) + '.xml</loc>\n'
 out += ' </sitemap>\n'
out += '</sitemapindex>\n'

_fh.write(out)
_fh.close()

