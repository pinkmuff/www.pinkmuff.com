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
<div class="_video_caption"><div class="_video_title" itemprop="name"><i class="fa fa-film">&nbsp;{{out['title']}}</i></p></div>
% if "tags" in out:
% tags = out['tags'].replace(';',' ').title()
<div class="_video_tags" itemprop="about"><p><i class="fa fa-file-text-o">&nbsp;{{tags}}</i></p></div>
% end
% if "duration" in out and int(out['duration']) > 0:
<div class="_video_duration" itemprop="duration"><p><i class="fa fa-clock-o">&nbsp;{{out['duration']}} minutes</i></p></div>
% end
% if "_viewcount" in out:
<div class="_video_viewcount"><p><i class="fa fa-eye">&nbsp;{{out['_viewcount']}} views</i></p><meta itemprop="interactionCount" content="UserDownloads:{{out['_viewcount']}}" /></div>
<div class="_video_caption"><p><a href="{{_config['_path']}}"><i class="fa fa-exclamation-circle">&nbsp;Having trouble showing the video?  Try refreshing the page!</i></a></p></div>
<div class="_video_caption"><p><i class="fa fa-exclamation-circle">&nbsp;Did you know?  On HTML5 players, you can Right Click and Save Video!</i></p></div>
</div>
</div>
</div>
</div>
<div class="span3"> {{!_config['video_page_ad']}} </div>
</div>
% include('_footer.tpl')
