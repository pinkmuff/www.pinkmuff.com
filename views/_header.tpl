<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>{{_config['_site_title']}} - {{title_extra}}</title>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<meta name="keywords" content="{{_config['META_KEYWORDS']}}" />
<meta name="description" content="{{_config['META_DESCRIPTION']}}" />
<meta name="google-site-verification" content="{{_config['GOOGLE_SITE_VERIFICATION']}}" />
<meta name="msvalidate.01" content="{{_config['MS_VALIDATE']}}" />
<meta name='yandex-verification' content='{{_config['YANDEX_VERIFICATION']}}' />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
<meta name="HandheldFriendly" content="true"/>
<link rel="schema.DC" href="http://purl.org/dc/elements/1.1/" />
<meta name="DC.title" content="{{_config['_site_title']}} - {{title_extra}}">
<meta name="DC.identifier" content="http://{{_config['_site_title']}}/" />
<meta name="DC.description" content="{{_config['META_DESCRIPTION']}}" />
<meta name="DC.subject" content="{{_config['META_KEYWORDS']}}">
<meta name="DC.language" scheme="ISO639-1" content="en">
<meta name="DC.creator" content="http://www.pinkmuff.com/">
<meta name="DC.contributor" content="http://{{_config['_site_title']}}/">
<meta name="DC.publisher" content="http://{{_config['_site_title']}}/">
<meta name="DC.license" content="http://{{_config['_site_title']}}/">
<script>function _search(e){if(e.keyCode == 13){window.location.href='/search/'+document.getElementById('search').value+'/';}}</script>
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', '{{_config['_ga_code']}}', '{{_config['_ga_site']}}');
  ga('require', 'displayfeatures');
  ga('send', 'pageview');
</script>
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/font-awesome/4.1.0/css/font-awesome.min.css">
<link rel="stylesheet" href="/css/{{_config['_site_css']}}.css">
<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
<script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
<script type="text/javascript"> window.onload = preloader; function preloader() { javascript:document.getElementById('iframe_sidebar').innerHTML = '<iframe src="{{_config["adbar"]}}" width="320" height="960" scrolling="no" frameborder="0" allowtransparency="true" marginheight="0" marginwidth="0"></iframe>'; } </script>
<script data-cfasync="false" type="text/javascript"> (function(s,o,l,v,e,d){if(s[o]==null&&s[l+e]){s[o]="loading";s[l+e](d,l=function(){s[o]="complete";s[v+e](d,l,!1)},!1)}})(document,"readyState","add","remove","EventListener","DOMContentLoaded"); (function() { var s = document.createElement("script"); s.type = "text/javascript"; s.async = true; s.src = "http://cdn.engine.phn.doublepimp.com/Scripts/infinity.js.aspx?guid=e038d6d9-51f8-47d3-b623-2ef4a375a535"; s.id = "infinity"; s.setAttribute("data-guid", "e038d6d9-51f8-47d3-b623-2ef4a375a535"); s.setAttribute("data-version", "async"); var e = document.getElementsByTagName('script')[0]; e.parentNode.insertBefore(s, e); })();
</script>
% if "/video/" in _config['_path']:
<link rel="stylesheet" href="/me/mediaelementplayer.css">
<script src="/me/mediaelement-and-player.min.js"></script>
% end
</head>
<body role="document" id="_body" itemscope itemtype="http://schema.org/WebPage">
