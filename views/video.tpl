% if len(out['tags']) < 100:
% _config['META_KEYWORDS'] = out['tags'] + ' ' + out['title'].title()
% else:
% _config['META_KEYWORDS'] = out['tags']
% end
% _config['META_KEYWORDS'] = _config['META_KEYWORDS'].replace(' ',', ').replace(';',', ').title()
% _config['META_DESCRIPTION'] = out['title'].title()
% title_extra = out['title'].replace('-',' ') + ' ' + out['tags'].replace(';',' ').title() # ' 
% include('_header.tpl', title_extra=title_extra)
% include('navbar.tpl')
<div class="container col-lg-12">
<div class="row-fluid">
<div class="span9">
<div class="_vidscontainer">
<div class="_videoplayer col-xs-6" itemscope itemtype="http://schema.org/MediaObject">
{{!out['embedLink']}}
<script>$('video').mediaelementplayer();</script>
<div class="_video_caption"><div class="_video_title" itemprop="name"><span class="_icon"><i class="_icon fa fa-film">&nbsp;</i></span><span class="_video_title_text"><i class="fa">{{out['title']}}</i></span></div>
% if "tags" in out:
% tags = out['tags'].replace(';',' ').title()
<div class="_video_tags" itemprop="about"><span class="_icon"><i class="_icon fa fa-file-text-o">&nbsp;</i></span><span class="_video_tags_text"><i class="fa">{{tags}}</i></span></div>
% end
% if "duration" in out and int(out['duration']) > 0:
<div class="_video_duration" itemprop="duration"><span class="_icon"><i class="_icon fa fa-clock-o">&nbsp;</i></span><span class="_video_duration_text"><i class="fa">{{out['duration']}} minutes</i></span></div>
% end
% if "_viewcount" in out:
<div class="_video_viewcount"><span class="_icon"><i class="_icon fa fa-eye">&nbsp;</i></span><span class="_video_viewcount_text">{{out['_viewcount']}} views</i></span><meta itemprop="interactionCount" content="UserDownloads:{{out['_viewcount']}}" /></div>
</div>
</div>
</div>
</div>
<div class="span3" id="iframe_sidebar"></div>
</div>
% include('_footer.tpl')
