#!/bin/bash

PHDUMP=http://www.pornhub.com/pornhub.com-db.zip

wget -O phdump.zip ${PHDUMP}
unzip phdump.zip
grep "//2014" pornhub.com-db.csv > 2014.csv
rm pornhub.com-db.csv
python initial.py 2014.csv

