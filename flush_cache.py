#!/usr/bin/python

import os
import csv
import sys
import random
import pylibmc
from pymongo import MongoClient

sys.path.append('/var/www/pornsite')
from config import _config, _friends, _categories

_sites = dict()
_sites["pinkmuff"] = 0
_sites["stagepinkmuff"] = 0

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

loadConfig('/var/www/www.pinkmuff.com/config')

_mc = pylibmc.Client(_config['_memcachedServer'])
for _site in _sites.iteritems():
 for _cat in _config['_categories']:
  _flush = str(_site[0]) + "_pages_" + str(_cat)
  out = _mc.delete(_flush)
  _flush = str(_site[0]) + "_pages_" + str(_cat) + "_mobile"
  out = _mc.delete(_flush)
  _flush = str(_site[0]) + "_" + str(_cat) + "_skip_" + str(_site[1])
  out = _mc.delete(_flush)

 _flush = str(_site[0]) + "_pages_none"
 out = _mc.delete(_flush)
 _flush = str(_site[0]) + "_pages_none_mobile"
 out = _mc.delete(_flush)
 _flush = str(_site[0]) + "_none_skip_" + str(_site[1])
 out = _mc.delete(_flush)
 _flush = str(_site[0]) + "_none_skip_" + str(_site[1]) + "_mobile"
 out = _mc.delete(_flush)
