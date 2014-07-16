#!/usr/bin/python

import os
import sys
import pprint
import urllib2
import twitter
import feedparser
from BeautifulSoup import BeautifulSoup
from pymongo import MongoClient

sys.path.append('/var/www/www.pinkmuff.com/config')
from config import _config

_phrss = 'http://www.pornhub.com/video/webmasterss'
_m = MongoClient(_config["_mongoServer"]["host"],_config["_mongoServer"]["port"])
_db = _m[_config["_mongoDb"]["name"]]
links = _db[_config["_mongoDb"]["links"]]

inserts = 0
try:
 _u = urllib2.urlopen(_phrss)
except:
 sys.exit()

try:
 _uc = _u.read()
except:
 sys.exit()

_feed = feedparser.parse(_uc)
_links = _feed['entries']

for _l in _links:
 _u = urllib2.urlopen(_l['link'])
 _uc = _u.read()
 _bs = BeautifulSoup(_uc)
 tmp = dict()
 for t in _bs.find('div', {'class': 'video-info-row'}):
  try:
   tag = t.contents[0]
  except:
   continue
  if len(tag) > 1 and len(tag) < 13:
   if not "tags" in tmp:
    tmp["tags"] = str(tag)
   else:
    tmp["tags"] = tmp["tags"] + ";" + tag
 if not "tags" in tmp:
  continue
 tmp["embedLink"] = _l["embed"]
 tmp["thumbLink"] = _l["thumb_large"]
 tmp["title"] = _l["title"]

 check = links.find_one({'title':tmp['title']})
 if not check:
  links.insert(tmp)
  inserts += 1

api = twitter.Api(
       consumer_key=_config['twitter_consumer_key'],
       consumer_secret=_config['twitter_consumer_secret'],
       access_token_key=_config['twitter_access_token_key'],
       access_token_secret=_config['twitter_access_token_secret'] )

if inserts > 0:
 _update = "Just updated http://" + str(_config['_site_title']) + "/ with "+ str(inserts) + " new cinematic adult adventures!!  #porn #xxx #pinkmuffcom_updates"
 _out = api.PostUpdate(_update)
 print "Twitter output: " + str(_out)
 print "Total new videos: " + str(inserts)
else:
 print "No updates."

_m.close()
