% include('_header.tpl', title_extra=_config['META_KEYWORDS'])
% include('navbar.tpl')
<div class="jumbotron">
<div class="container">
<h1>About {{_config['_site_title']}}</h1>
<p>We are an automated adult aggregator.  Our goal is to provide fast, simple access to free adult content.  We will pull down the data from various sources and render it here in an intuitive manner.</p>
<p>Speed is paramount.  We're always looking for better ways to provide you with blazing fast access to adult content.</p>
<p>Many adult sites today are slow and bloated with useless features.  We're focusing only on speed and content.</p>
</div>
</div>
<div class="container">
<div class="row">
<div class="col-md-4">
<h2>FOSS</h2>
<p>We are proudly using the following:</p>
<p><a href='http://www.mongodb.org/'>MongoDB</a></p>
<p><a href='https://www.python.org/'>Python</a></p>
<p><a href='http://bottlepy.org/'>Bottle</a></p>
<p><a href='http://nginx.org/'>nginx</a></p>
<p><a href='http://projects.unbit.it/uwsgi/'>uWSGI</a></p>
</div>
<div class="col-md-4">
<h2>Free</h2>
<p>We're providing this to you free of charge.  If you wish to say thanks, consider donating BTC to:</p>
<p><h4>{{_config['_btc_donate']}}</h4></p>
</div>
<div class="col-md-4">
<h2>Our Technology</h2>
<p>Want to leverage our technology yourself?</p>
<p>Have job offers?</p>
<p>Other?</p>
<p>Contact us:  <a href="mailto:{{_config['_email']}}">{{_config['_email']}}</a></p>
</div>
<div class="col-md-4">
<h2>Twitter</h2>
<p>Follow us on Twitter: <a href="https://twitter.com/{{_config['_twitter']}}">@{{_config['_twitter']}}</a><p>
<p>Check our updates via <a href="https://twitter.com/search?q=%23hashfast&src=typd">#{{_config['_twitter']}}_updates</a></p>
</div>
<hr>
</div>
% include('_footer.tpl')
