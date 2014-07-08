% if len(out['tags']) < 100:
% _config['META_KEYWORDS'] = out['tags'] + ' ' + out['title'].title()
% else:
% _config['META_KEYWORDS'] = out['tags']
% end
% _config['META_KEYWORDS'] = _config['META_KEYWORDS'].replace(' ',', ').replace(';',', ').title()
% _config['META_DESCRIPTION'] = out['title'].title()
% title_extra = out['title'].replace('-',' ') + ' ' + out['tags'].replace(';',' ').title()
% include('_header.tpl', title_extra=title_extra)
% include('navbar.tpl')
<div class="container">
<div class="row text-center" id="_top_ad">
{{!_config['video_page_ad']}}
</div>
<div class="row text-center {{_config['text_color']}}"><h1 class="small"><i class="fa">Did you know?  On HTML5 players, you can Right Click below and Save Video!</i></h1></div>
</div>
<div class="container">
<div class="row text-center">{{!out['embedLink']}}
<div class="caption text-center"><h1 class="small"><i class="fa">Title: {{out['title']}}</i></h1>
% if "tags" in out:
% tags = out['tags'].replace(';',' ').title()
<h2 class="small"><i class="fa">Tags: {{tags}}</i></h2>
% end
% if "duration" in out and int(out['duration']) > 0:
<h3 class="small"><i class="fa">Duration: {{out['duration']}} seconds</i></h3>
% else:
<h3 class="small"><i class="fa">Duration: --</i></h3>
% end
<div class="caption text-center"><h4 class="small"><a href="{{_config['_path']}}"><i class="fa">Having trouble showing the video?  Try refreshing the page!</i></a></h4></div>
</div>
</div>
% include('_footer.tpl')
