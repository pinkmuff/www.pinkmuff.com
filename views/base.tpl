% _config['META_DESCRIPTION'] = _config['META_DESCRIPTION'] + ", category " + _config['active_category']
% include('_header.tpl', title_extra=_config['META_KEYWORDS'])
% include('navbar.tpl')
<div class="row text-center">
{{!_config['main_page_ad']}}
</div>
<div class="container">
<h1 class="small {{_config['text_color']}}"><b><i>{{_config['_site_title']}}</b> - {{_config['_by_line']}}</i></h1>
<h2 class="small {{_config['text_color']}}"><strong><i>Category:</i> {{_config["active_category"]}}</strong></h2>
</div>
<div class="container">
<div class="row">
% count = 0
% _ad_counter = 0
% for i,video in out.iteritems():
% if _ad_counter == 2:
<div class="thumbnail col-xs-4 rhthumb"><div class="customad">{{!_config['video_tile_ad']}} </div></div>
% _ad_counter += 1
% else:
% _ad_counter += 1
<div class="thumbnail col-xs-4 rhthumb"><a href='/video/{{video['_id']}}/{{video['uri']}}'><img id="video{{i}}" src='{{video['thumbLink']}}' alt='{{video['title']}}'></a>
<div class="caption {{_config['text_color']}}"><h3 class="small"><strong>Title:&nbsp;</strong>{{video['title']}}</h3>
% if "tags" in video:
% tags = video['tags'].replace(';',' ').title()
<h4 class="small"><strong>Tags:&nbsp;</strong> {{tags}}</h4>
% end
% if "duration" in video and int(video['duration']) > 0:
<h5 class="small"><strong>Duration:&nbsp;</strong> {{video['duration']}} seconds</h5>
% else:
<h5 class="small"><strong>Duration:&nbsp;</strong> --</h5>
% end
</div>
</div>
% end
% if count == 2:
</div>
<div class="row">
% count = 0
% else:
<!--</div>-->
% count += 1
% end 
% end
<!--</div>-->
</div>
<div class="container">
<div class="row text-center">
<ul class="pagination">
% if _config['page'] <= 1:
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
% _start = _config['page']
% _end = _config['pages']
% else:
% _start = _config['page']
% _end = _config['page'] + 10
% end 
% for i in xrange(_start,_end+1):
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
