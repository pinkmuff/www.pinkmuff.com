<div id="nav" class="navbar fullpage navbar-inverse" role="navigation">
<div class="container-fluid">
<div class="navbar-header">
<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
<span class="sr-only">Toggle navigation</span>
<span class="icon-bar"></span>
<span class="icon-bar"></span>
<span class="icon-bar"></span>
</button>
<a class="navbar-brand" href="/">{{_config['_site_title']}}</a>
</div>
<div class="navbar-collapse collapse">
<ul class="nav navbar-nav">
<li><a href="/">Home</a></li>
<li><a href="/about/">About</a></li>
<li class="dropdown">
<a href="#" class="dropdown-toggle" data-toggle="dropdown">Categories <b class="caret"></b></a>
<ul class="dropdown-menu">
% for c,v in sorted(_config['_categories'].iteritems()):
<li><a href="/categories/{{c}}/">{{v[2]}}</a></li>
% end
</ul>
</li>
<li class="dropdown">
<a href="#" class="dropdown-toggle" data-toggle="dropdown">Links <b class="caret"></b></a>
<ul class="dropdown-menu">
% for linktitle,link in sorted(_config['_links'].iteritems()):
<li><a href="{{link}}">{{linktitle}}</a></li>
% end
</ul>
</li>
</ul>
</div><!--/.nav-collapse -->
</div>
</div>
</div>
<script>
$( document ).ready(function() {
   $('#nav').affix({
   });
});
</script>
