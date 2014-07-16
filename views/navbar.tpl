<div id="nav" class="navbar fullpage navbar-inverse" role="navigation">
<div class="container-fluid">
<div class="navbar-header">
<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
<span class="sr-only">Toggle navigation</span>
<span class="icon-bar"></span>
<span class="icon-bar"></span>
<span class="icon-bar"></span>
</button>
<a class="navbar-brand" href="/"><i class="fa">{{_config['_site_title']}}</i></a>
</div>
<div class="navbar-collapse collapse">
<ul class="nav navbar-nav">
<li><a  href="/"><i class="fa fa-home">&nbsp;Home</i></a></li>
<li><a  href="/about/"><i class="fa fa-eye">&nbsp;About</i></a></li>
<li class="dropdown">
<a href="#" class="dropdown-toggle" data-toggle="dropdown"><i class="fa fa-book">&nbsp;Categories ({{_config["active_category"]}})</i>&nbsp;<b class="fa fa-caret-down"></b></a>
<ul class="dropdown-menu kolumny">
% for c,v in sorted(_config['_categories'].iteritems()):
<li><a href="/categories/{{c}}/">{{v[2]}}</a></li>
% end
</ul>
% if "/random/" in _config['_path']:
<li><a href="{{_config['_path']}}"><i class="fa fa-spinner fa-spin">&nbsp;</i><i class="random">&nbsp;Random</i></a></li>
% elif not "/video/" in _config['_path'] and not "/page/" in _config['_path']:
<li><a href="{{_config['_path']}}random/"><i class="fa fa-spinner fa-spin">&nbsp;</i><i class="fa">&nbsp;Random</i></a></li>
% else:
<li class="white"><a href="/random/"><i class="fa fa-spinner fa-spin">&nbsp;</i><i class="fa">&nbsp;Random</i></a><li>
% end
<li class="dropdown">
<a href="#" class="dropdown-toggle white" data-toggle="dropdown"><i class="fa">Links&nbsp;</i><b class="fa fa-caret-down"></b></a>
<ul class="dropdown-menu">
% for linktitle,link in sorted(_config['_links'].iteritems()):
<li><a href="{{link}}">{{linktitle}}</a></li>
% end
</ul>
</li>
<li class="navbar-form"><input id="search" type="text" class="form-control" placeholder="{{_config['search_placeholder']}}" onkeydown="_search(event)" /></li>
<li><a id="search_button" href="javascript:onclick(window.location.href='/search/' + document.getElementById('search').value + '/');"><i class="fa fa-search"></i></a></li>
</ul>
</div>
</div>
</div>
