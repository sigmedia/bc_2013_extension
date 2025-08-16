{% extends get_template('base.tpl') %}

{% block content %}

<h2 class="bd-content-title">Test completed!</h2>

<p>
    Thank you for completing the test.
</p>
<p>
    If you want to have more information about the results or any enquiry concerning your participation, you can contact the authors of the test.
    <b>To do so, you need to communicate the following identifier:</b>
</p>


<p style="font-size: large; font-weight: bold; text-align: center; background-color: #DDD; border: 2px;">
    {%block userintel%}
    {% if auth.validates_connection("connected")[0] %}
    {{ auth.user.id }}
    {% endif %}
    {%endblock%}
</p>


{%block prolific%}
{% if auth.validates_connection("connected")[0] and auth.user.id.endswith("@prolific.com") %}
The <b>completion code required by prolific</b> is:

<p style="font-size: large; font-weight: bold; text-align: center; background-color: #DDD; border: 2px;">
    <a href="https://app.prolific.co/submissions/complete?cc=7F6F57CA">7F6F57CA</a>
</p>
{% endif %}
{%endblock%}

<br />
<br />

<h3>The contacts of the authors are the following:</h3>
<p>
    <b>Sébastien Le Maguer</b> - Email: lemagues@tcd.ie <br />
    SIGMEDIA / ADAPT Centre, Electronic and Electrical Engineering.  <br />
    Aras an Phiarsaigh, Trinity College Dublin <br />
    College Green, Dublin 2, <br />
    Ireland  <br />
</p>

{% endblock %}
