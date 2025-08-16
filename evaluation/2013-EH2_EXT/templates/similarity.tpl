{% extends get_template('base.tpl') %}

{% block content %}

  <h2 class="bd-content-title">
    {{get_variable("subtitle")}}
    <div class="progress" style="height: 20px; width:50%; float:right;" >
      <div id="progress-bar" class="progress-bar" role="progressbar"
           style="width: {{(get_variable("step")-1)/get_variable("max_steps")*100}}%;"
           aria-valuenow="{{get_variable("step")-1}}"
           aria-valuemin="0"
           aria-valuemax="{{get_variable("max_steps")}}">
           [{{get_variable("step")-1}} / {{get_variable("max_steps")}}]
      </div>
  </h2>

<div class="">
    Here are the same four reference samples that you heard before, you can listen to them again if you want to.
    <br />
    <center>
        <audio id="ref_A" controls>
            <source src="{{get_asset('/ref_samples/booksent_2013_0057.wav')}}">
            Your browser does not support the <code>audio</code> element.
        </audio>
        <br />
        <audio id="ref_B" controls>
            <source src="{{get_asset('/ref_samples/booksent_2013_0077.wav')}}">
            Your browser does not support the <code>audio</code> element.
        </audio>
        <br />
        <audio id="ref_C" controls>
            <source src="{{get_asset('/ref_samples/booksent_2013_0043.wav')}}">
            Your browser does not support the <code>audio</code> element.
        </audio>
        <br />
        <audio id="ref_D" controls>
            <source src="{{get_asset('/ref_samples/booksent_2013_0088.wav')}}">
            Your browser does not support the <code>audio</code> element.
        </audio>
    </center>
</div>

<br />
<br />
<form action="./save" method="post" enctype="multipart/form-data" class="form-example">
    <fieldset class="form-group">
        <legend class="col-form-label">
            <strong>Question: </strong> How do you judge the <strong>quality</strong> of the following sample?
        </legend>

        {% set syssample = get_variable("syssamples")[0] %}
        <div class="form-group" style="margin-bottom:10px;">
            {% set name_field = get_variable("field_name",name="MOS_score",syssamples=[syssample]) %}
            {% set content,mimetype = syssample.get("audio")  %}

            <center>
                <label for="score@{{syssample.ID}}">
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

            <select id="score@{{syssample.ID}}" name="{{name_field}}" class="form-control" required>
                <option value="" selected disabled hidden>Choose here</option>
                <option value="1">1 : Sounds like a totally different person</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5 : Sounds like exactly the same person</option>
            </select>
        </div>
    </fieldset>

    <button type="submit" id="submit" class="btn btn-primary">Submit</button>
</form>
{% endblock %}
