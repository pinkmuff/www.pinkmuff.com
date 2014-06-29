% _config['META_DESCRIPTION'] = _config['META_DESCRIPTION'] + ", category " + _config['active_category']
% include('_header.tpl', title_extra=_config['META_KEYWORDS'])
% include('navbar.tpl')
<div class="row text-center">
{{!_config['main_page_ad']}}
</div>
<div class="container">
<h1 class="small"><b><i>{{_config['_site_title']}}</b></i> - {{_config['_by_line']}}</h1>
<h2 class="small"><strong><i>Category:</i> {{_config["active_category"]}}</strong></h2>
</div>
<div class="container col-lg-12">
% count = 0
<div class="row">
% for i,video in out.iteritems():
<div class="col-lg-4 text-center"><a href='/video/{{video['_id']}}/{{video['uri']}}'><img id="video{{i}}" src='{{video['thumbLink']}}' alt='{{video['title']}}' class="img-thumbnail"></a>
<div class="caption text-left"><h3 class="small"><b>Title: {{video['title']}}</b></h3></div>
% if "tags" in video:
% tags = video['tags'].replace(';',' ').title()
<div class="caption text-left"><h4 class="small"><b>Tags: {{tags}}</b></h4></div>
% end
% if "duration" in video and int(video['duration']) > 0:
<div class="caption text-left"><h5 class="small"><b>Duration: {{video['duration']}} seconds</b></h5></div>
% end
</div>
% if count == 2:
</div>
<div class="row">
% count = 0
% else:
% count += 1
% end 
% end
</div>
</div>
<div class="container">
<div class="row text-center">
<ul class="pagination">
% if _config['page'] == 1:
<!--<li class="disabled"><a href="#">&laquo;</a></li>-->
% else:
% if _config['page'] < 10:
% target = 1
% else:
% target = _config['page'] - 10
% end
<li><a href="{{_config['uri_prefix']}}page/{{target}}/">&laquo;</a></li>
% end
% if (_config['page'] + 10) > _config['pages']:
% _start = (_config['page'] - 10)
% else:
% _start = _config['page']
% end 
% if _config['pages'] < 10:
% _start = _config['page']
% _numPaginator = _config['pages']
% else:
% _numPaginator = 10
% end
% for i in xrange(_start,_start + _numPaginator):
% if _config['page'] == i:
<li class="active"><a href="{{_config['uri_prefix']}}page/{{i}}/">{{i}}</a></li>
% else:
<li><a href="{{_config['uri_prefix']}}page/{{i}}/">{{i}}</a></li>
% end
% end
% if _config['page'] + 10 > _config['pages']:
% target = '#'
<!--<a href="{{_config['uri_prefix']}}page/{{target}}/">&raquo;</a></li>-->
% else:
% target = _config['page'] + 10
<li><a href="{{_config['uri_prefix']}}page/{{target}}/">&raquo;</a></li>
% end
</ul>
</div>
</div>
% include('_footer.tpl')
