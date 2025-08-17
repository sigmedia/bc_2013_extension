{% extends 'base.tpl' %}

{% block content %}

  <h2 class="bd-content-title">Instructions</h2>

  <form action="./save" method="post" class="form-example justified">
    <p>
      In the following test, you will listen a set of samples.
      At each step, the same text has been synthesized by multiple systems.
      Your task is to give a score to all the samples samples.
    </p>

    <p>
      <strong>Moving to the next step:</strong>
      To be able to move to the next step, you will have to listen to each sample until its end at least once as well as scored all the samples.
      When you will have listen a sample until the end, it will be indicated as fully played in the corresponding column with a "<span style="color:green;" />✔</span>"
      You can listen to the samples multiple time as well as go back and forth between samples to refine your score.
    </p>

    <p>
      <strong>Control:</strong>
      <ul>
	<li>One of the sample to evaluate is the reference. <b>You should give a score of 100 to this sample</b>. If you fail this for more than one step, your participation won't be considered valid.</li>
	<li>There is a clear difference in quality between some samples. If you give a score of 100 to all samples, your participation won't be considered as valid</li>
      </ul>
    </p>

    <p>
      <strong>Training:</strong>
      Before the evaluation itself, you will have an training step for you to get familiar with the controls.
      The training step is identical to the core of the evaluation itself but we don't record the information.
    </p>

    <p>
      <strong>Monitoring:</strong>
      The platform monitors the following actions:
      <ul>
        <li>when you play a sample</li>
        <li>when you score a sample</li>
      </ul>
      Our goal is to determine if there are some common strategies between the participants.
    </p>

    <p>
      Thank you for the participation,
    </p>

    <center>
      <button type="submit" id="submit" class="btn btn-primary">Start the test</button>
    </center>
  </form>
{% endblock %}
