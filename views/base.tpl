% _config['META_DESCRIPTION'] = "Category " + _config['active_category'] + ", " + _config['META_DESCRIPTION']
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
% alt = video['title'][:-1].replace('-',' ').title()
<div class="col-lg-4 text-center"><a  href='/video/{{video['_id']}}/{{video['title']}}'><img id="video{{i}}" src='{{video['thumbLink']}}' alt='{{alt}}' class="img-thumbnail"></a>
<div class="caption text-left"><h6><b>Title: {{video['caption']}}</b></h6></div>
% if "tags" in video:
% tags = video['tags'].replace(';',' ').title()
<div class="caption text-left"><h6><b>Tags: {{tags}}</b></h6></div>
% end
% if "duration" in video and int(video['duration']) > 0:
<div class="caption text-left"><h6><b>Duration: {{video['duration']}} seconds</b></h6></div>
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
% for i in xrange(_config['page'],_config['page'] + 10):
% if _config['page'] == i:
<li class="active"><a href="{{_config['uri_prefix']}}page/{{i}}/">{{i}}</a></li>
% else:
<li><a href="{{_config['uri_prefix']}}page/{{i}}/">{{i}}</a></li>
% end
% end
% target = _config['page'] + 10
<li><a href="{{_config['uri_prefix']}}page/{{target}}/">&raquo;</a></li>
</ul>
</div>
</div>
% include('_footer.tpl')
