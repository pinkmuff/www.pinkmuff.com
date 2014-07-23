% _config['META_DESCRIPTION'] = _config['META_DESCRIPTION'] + ", category " + _config['active_category']
% include('_header.tpl', title_extra=_config['META_KEYWORDS'])
% include('navbar.tpl')
<div class="container col-lg-12">
<div class="row-fluid">
<div class="span3 pull-right" id="iframe_sidebar"></div>
<div class="span9">
<div class="_vidscontainer">
% for i,video in out.iteritems():
<div class="_video col-xs-6">
% if "tags" in video:
% tags = video['tags'].replace(';',' ').title()
% else:
% tags = ''
% end
<div title="{{tags}}" class="_img" itemscope itemtype="http://schema.org/MediaObject"><a itemprop="contenturl" href="/video/{{video['_id']}}/{{video['uri']}}"><img itemprop="thumbnailUrl" class="_img" src="{{video['thumbLink']}}" alt="{{tags}}" /></a></div>
<div class="caption"><div class="_title" itemprop="name"><i class="_icon fa fa-film">&nbsp;</i><i class="fa">{{video['title']}}</i></div>
<div class="_tags" itemprop="about"><i class="_icon fa fa-file-text-o">&nbsp;</i><i class="fa">{{tags}}</i></div>
% if "duration" in video and int(video['duration']) > 0:
<div class="_duration" itemprop="duration"><i class="_icon fa fa-clock-o">&nbsp;</i><i class="fa">{{video['duration']}} minutes</i></div>
% end
% if "_viewcount" in video:
<div class="_viewcount"><i class="_icon fa fa-eye">&nbsp;</i><i class="fa">{{video['_viewcount']}} views</i><meta itemprop="interactionCount" content="UserDownloads:{{video['_viewcount']}}" /></div>
% end
</div></div>
% end
</div>
</div>
</div>
</div>
<div class="row-fluid text-center">
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
% include('_footer.tpl')
