# First

## Install pre-requisites
apt-get install nginx uwsgi memcached
pip install python-pymongo 
pip install python-pylibmc 
pip install python-bottle 
pip install elasticsearch

## Elasticsearch
We're using elasticsearch & elasticseach + mongodb river

https://github.com/richardwilly98/elasticsearch-river-mongodb

Mind your version compatibilities. 

# Second

## create uwsgi config:

Your uwsgi ##PATH_TO_YOUR_PYTHON_CODE## should live outside of nginx's root.

This ensures that only static files on ##YOUR_DOMAIN## are served and all other requests filter in to USWGI.

     cat > /etc/uwsgi/apps-enabled/porn.ini << EOF
     [uwsgi]
     chdir = /var/www/pornsite
     master = true
     plugins = python
     file = app.py
     uid = www-data
     chmod-socket = 640
     chown-socket = www-data
     vacuum = true
     processes = 4
     threads = 2
     offload-threads = 1
     harakiri = 30
     logto2 = /var/www/www.pornsite.com/logs/uwsgi/pornsite.log
     env = _DOCROOT=/var/www/www.pornsite.com
     stats = /run/uwsgi/porn.stats
     socket = /run/uwsgi/porn.socket

     ## If you use graphite/carbon
     carbon = 127.0.0.1:2003
     EOF

# Third

## create nginx config:
     cat > /etc/nginx/sites-enabled/porn.com.conf << EOF
     upstream porn {
       server unix:/run/uwsgi/app/porn/socket;
     }
     server {
       listen *:80;
       listen [::]:80; ## For IPv6
       server_name static.##YOUR_DOMAIN##;
       root ##MAIN_DOCROOT##;
       index index.html;
       expires 168h;
     } 
    
     server {
       listen *:80;
       listen [::]:80;
       root ##MAIN_DOCROOT##;
       server_name ##LIST_OF_301_DOMAINS##;
       return 301 http://##YOUR_PRIMARY_DOMAIN##;
     }

     server {
       listen *:80;
       listen [::]:80;
       server_name ##YOUR_DOMAIN##
       root ##MAIN_DOCROOT##;
       index index.html;

       location /server-status {
        stub_status on;
        access_log off;
        allow 127.0.0.1/32;
        allow 173.177.75.104;
       }

       access_log ##PATH_TO_NGINX_LOG_DIR_FOR_SITE##/access.log main;
       error_log ##PATH_TO_NGINX_LOG_DIR_FOR_SITE##/error.log;
     
       try_files $uri @uwsgi;
       location @uwsgi {
        include uwsgi_params;
        uwsgi_pass porn;
      }
     }
     EOF

# Fourth

## create a web structure

     mkdir /var/www/pornsite
     git clone git@bitbucket.org:routehero/pornsite.git
    
     mkdir -p /var/www/www.pornsite.com/logs/app
     mkdir -p /var/www/www.pornsite.com/logs/nginx
     mkdir -p /var/www/www.pornsite.com/logs/uwsgi
     mkdir -p /var/www/www.pornsite.com/htdocs
     mkdir -p /var/www/www.pornsite.com/config
     ln -sf /var/www/pornsite /var/www/www.pornsite.com/code

# Fifth

## create cronjob to pull rss feed

     */30 * * * * (cd /var/www/pornsite; python pornhub-rss.py; python flush_cache.py)
