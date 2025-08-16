{% extends get_template('base.tpl') %}

{% block content %}

<h2 class="bd-content-title">
    Introduction to sections 2, 3, 4 and 5
</h2>

<form action="./save" method="post" enctype="multipart/form-data" class="form-example">
  <fieldset class="form-group">
      <legend class="col-form-label">
          <p>
              In the following sections, after you listen to each sentence, you will choose a score for the audio file you've just heard.
              This score should reflect your opinion of how <b>natural</b> or <b>unnatural</b> the sentence sounded.
              You should not judge the grammar or content of the sentence, just how it <b><i>sounds</i></b>.
          </p>
          <p>
              Listen to the example below:
          </p>
    </legend>

    <div class="form-group" style="margin-bottom:10px;">
      <center>
          <audio id="sample" controls readall>
              <source src="{{get_asset('/ref_samples/booksent_2013_0057.wav')}}">
              Your browser does not support the <code>audio</code> element.
          </audio>
      </center>

      <legend class="col-form-label">
          Now choose a score for how <b>natural</b> or <b>unnatural</b> the sentence <b><i>sounded</i></b>.
          The scale is from <b>1 [Completely Unnatural] to 5 [Completely Natural]</b>.
      </legend>

    <select id="mos_score" class="form-control" required>
          <option value="" selected disabled hidden>Choose here</option>
          <option value="1">1 : Completely Unnatural</option>
          <option value="2">2 : Mostly Unnatural</option>
          <option value="3">3 : Equally Natural and Unnatural</option>
          <option value="4">4 : Mostly Natural</option>
          <option value="5">5 : Completely Natural</option>
      </select>
    </div>
  </fieldset>

  <button type="submit" id="submit" class="btn btn-primary">Submit</button>
</form>
{% endblock %}
