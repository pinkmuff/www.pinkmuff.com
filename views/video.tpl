% if len(out['tags']) < 100:
% _config['META_KEYWORDS'] = out['tags'] + ' ' + out['title'][:50]
% else:
% _config['META_KEYWORDS'] = out['tags']
% end
% _config['META_KEYWORDS'] = _config['META_KEYWORDS'].replace(' ',', ').replace(';',', ').title()
% _config['META_DESCRIPTION'] = out['title'].title()
% title_extra = out['title'].replace('-',' ') + ' ' + out['tags'][:40].replace(';',' ').title()
% include('_header.tpl', title_extra=title_extra)
% include('navbar.tpl')
<div class="container">
<div class="row text-center" id="_top_ad">
{{!_config['video_page_ad']}}
</div>
</div>
<div class="container">
<div class="row text-center">{{!out['embedLink']}}
<div class="caption text-center"><h1 class="small">Title: {{out['title']}}</h1></div>
% if "tags" in out:
% tags = out['tags'].replace(';',' ').title()
<div class="caption text-center"><h2 class="small">Tags: {{tags}}</h2></div>
% end
% if "duration" in out and int(out['duration']) > 0:
<div class="caption text-center"><h3 class="small">Duration: {{out['duration']}} seconds</h3></div>
% end
<div class="caption text-center"><h4 class="small"><a href="{{_config['_path']}}">Having trouble showing the video?  Try refreshing the page!</a></h4></div>
</div>
</div>
% include('_footer.tpl')
