{% extends get_template('base.tpl') %}

{% block content %}

<h2 class="bd-content-title"> <img src="{{get_asset('/img/svg_icon/chevron-right.svg','flexeval')}}" alt=">" /> Test</h2>

<p>
    Information here
</p>

<a id="start_link" href="{{url_next}}">Start the test</a>
{% endblock %}
