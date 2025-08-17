{% extends 'base.tpl' %}

{% block content %}

  <h2 class="bd-content-title"> <img src="{{get_asset('/img/svg_icon/chevron-right.svg','flexeval')}}" alt=">" /> Test completed!</h2>

  <p style="font-size: large; font-weight: bold; text-align: center; background-color: #04AA6D; color: #FFF; padding: 10px; margin-top: 20px; margin-bottom:20px; border-radius: 25px;">
    Thank you for completing the test.
  </p>

  {%block prolific%}
    {% if auth.validates_connection("connected")[0] %}
      <center>
        <a href="https://app.prolific.com/submissions/complete?cc=C1GMFMWW">
  	  <p style="font-size: large; font-weight: bold; text-align: center;" class="btn btn-primary">
            Validate completion of the test
          </p>
        </a>
      </center>
    {% endif %}
  {%endblock%}
{% endblock %}
