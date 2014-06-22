% _config['META_KEYWORDS'] = out['tags'].replace(' ',', ').title()
% _config['META_DESCRIPTION'] = out['caption'].title()
% title_extra = out['caption'] + out['tags'][:30].replace(';',' ').title()
% include('_header.tpl', title_extra=title_extra)
% include('navbar.tpl')
<div class="container">
<div class="row text-center" id="_top_ad">
{{!_config['video_page_ad']}}
</div>
</div>
<div class="container">
<div class="row text-center">{{!out['embedLink']}}
<div class="caption text-center"><h6>Title: {{out['caption']}}</h6></div>
% if "tags" in out:
% tags = out['tags'].replace(';',' ').title()
<div class="caption text-center"><h6>Tags: {{tags}}</h6></div>
% end
% if "duration" in out and int(out['duration']) > 0:
<div class="caption text-center"><h6>Duration: {{out['duration']}} seconds</h6></div>
% end
</div>
</div>
% include('_footer.tpl')
