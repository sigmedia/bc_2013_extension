{% extends 'mushra.tpl' %}
{% block instruction %}
<p>
    <strong>Moving to the next step:</strong>
    To be able to move to the next step, you will have to listen to each sample until its end at least once as well as scored all the samples.
    When you will have listen a sample until the end, it will be indicated as fully played in the corresponding column with a "<span style="color:green;" />✔</span>"
    You can listen to the samples multiple time as well as go back and forth between samples to refine your score.
</p>
<p>
    <strong>Control:</strong> One of the sample to evaluate is the same sample as the reference. <b>You should give a score of 100 to this sample.</b> If you fail this for too many steps, your participation won't be considered valid
</p>
<p>
  <strong><u>Question:</u></strong> How do you judge the <strong>naturalness</strong> of the following candidates against the reference?
</p>
{% endblock %}
