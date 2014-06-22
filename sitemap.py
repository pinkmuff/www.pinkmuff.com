#!/usr/bin/python

import os
import sys
import math
from pymongo import MongoClient

sys.path.append(##PATH_TO_YOUR_CONFIG##)
from config import _config

_m = MongoClient(_config["_mongoServer"]["host"],_config["_mongoServer"]["port"])
_db = _m[_config["_mongoDb"]["name"]]
links = _db[_config["_mongoDb"]["links"]]
_split = 49000

if len(sys.argv) != 2:
 print "Usage: " + sys.argv[0] + " [www.domain.com] > sitemap.xml"
 sys.exit()

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
  _fh.write(out)

  for cat,v in _config['_categories'].iteritems():
   out = ''
   out += '  <url>\n'
   out += '   <loc>' + domain + 'categories/' + cat + '/</loc>\n'
   out += '   <priority>1.0</priority>\n'
   out += '   <changefreq>hourly</changefreq>\n'
   out += '  </url>\n'

   _fh.write(out)

 _fh.write(out)
 _skip = int(i) * int(_split)
 for video in links.find().sort('_id',-1).skip(_skip).limit(_split):
  out = ''
  videoid = str(video['_id'])
  title = video['title'].replace(' ','-').lower()
  title = title.replace('&','&amp;')
  title = title.replace("'","&apos;")
  title = title.replace('"','&quot;')
  out += '  <url>\n'
  out += '   <loc>' + domain + 'video/' + videoid + '/' + title + '/</loc>\n'
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

