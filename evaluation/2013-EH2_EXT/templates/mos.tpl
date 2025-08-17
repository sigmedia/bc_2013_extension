{% extends 'base.tpl' %}

{% block content %}

  <h2 class="bd-content-title">
    {{subtitle}}
    <div class="progress" style="height: 20px; width:50%; float:right;" >
      <div id="progress-bar" class="progress-bar" role="progressbar"
           style="width: {{(step-1)/max_steps*100}}%;"
           aria-valuenow="{{step-1}}"
           aria-valuemin="0"
           aria-valuemax="{{max_steps}}">
           [{{step-1}} / {{max_steps}}]
      </div>
  </h2>

<form action="./save" method="post" enctype="multipart/form-data" class="form-example">
  <fieldset class="form-group">
    <legend class="col-form-label">
        Listen to the example below:
    </legend>

    {% set sample = list_samples()[0] %}
    <div class="form-group" style="margin-bottom:10px;">
      {% set name_field = sample | generate_field_name(basename="MOS_score") %}
      {% set content,mimetype = sample.get("audio")  %}

      <center>
          <label for="score@{{sample.ID}}">
              {% if mimetype == "text" %}
                {{content}}
              {% elif mimetype == "image" %}
                <img class="img-fluid" src="{{content}}" />
              {% elif mimetype == "audio" %}
                <audio id="sample" controls readall>
                    <source src="{{content}}">
                    Your browser does not support the <code>audio</code> element.
                </audio>
              {% elif mimetype == "video" %}
                <video controls readall>
                    <source src="{{content}}">
                    Your browser does not support the <code>video</code> element.
                </video>
              {% else %}
                {{content}}
              {% endif %}
          </label>
      </center>

      <legend class="col-form-label">
          Now choose a score for how <b>natural</b> or <b>unnatural</b> the sentence <b><i>sounded</i></b>.
          The scale is from <b>1 [Completely Unnatural] to 5 [Completely Natural]</b>.
    </legend>
    <select id="mos_score@{{sample.ID}}" name="{{name_field}}" class="form-control" required>
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
