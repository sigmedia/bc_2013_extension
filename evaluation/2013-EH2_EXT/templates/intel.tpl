{% extends get_template('base.tpl') %}

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
            <p>
                Please try to enter all of the words you hear, but <b>do not enter any comments.</b>
                If you cannot hear any sound coming out of the headphones, please make sure that your browser can handle embedded audio players (all current browsers do), and that you have not turned javascript off.
                If you can hear the audio, but you cannot understand ANY of the words, just write <b>"&lt;&gt;"</b> (without the quotes) and nothing else.
                If you can understand some, but not all of the words, just type in the ones you heard.
            </p>
            <p>
                <b>Listen to the audio file, and type what you hear into the text box.&nbsp; </b>
                <br><br>
            </p>
        </legend>


        {% for sample in list_samples() %}
          <div class="form-group" style="margin-bottom:10px;">
            {% set name_field = sample | generate_field_name(basename="transcription") %}
            {% set content,mimetype = sample.get("audio")  %}

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

            <div class="form-group required">
                <label for="transcription@{{sample.ID}}">Transcription:</label>
                <input type="text" id="transcription@{{sample.ID}}" name="{{ name_field }}" class="form-control" required />
            </div>
        </div>
        {% endfor %}
    </fieldset>

    <button type="submit" id="submit" class="btn btn-primary">Submit</button>
</form>
{% endblock %}
