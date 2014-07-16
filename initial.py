import os
import sys
import csv
import json
from config import _config
from pymongo import MongoClient

if len(sys.argv) != 2:
 print "Usage: " + str(sys.argv[0]) + " <filename>.csv"
 sys.exit()

csvfile = open(sys.argv[1],'r')
c = csv.DictReader(csvfile,_config["_fields"],delimiter=_config["_csvDelimiter"])
_m = MongoClient(_config["_mongoServer"]["host"],_config["_mongoServer"]["port"])
_db = _m[_config["_mongoDb"]["name"]]
links = _db[_config["_mongoDb"]["links"]]

for row in c:
 try:
  links.insert(row)
 except:
  print row
  pass

_m.close()
