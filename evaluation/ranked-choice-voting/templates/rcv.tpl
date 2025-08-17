{% extends 'base.tpl' %}

{% block head %}
<style>
    td {
        text-align: center;
  vertical-align: middle;
  padding-bottom: 20px;

    }
    #overlay {
        position: fixed;
        display: none;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 2;
        cursor: pointer;
    }
    #overlay-content {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #f8d7da;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: x-large;
    }

    .btn-solo .btn-solo.disabled, .btn-solo:disabled {
        background-color: #f3e621;
        border-color: #f3e621;
        color: #000;
        font-weight: bold;
    }

    .btn-mute, .btn-mute.disabled, .btn-mute:disabled {
        background-color: #4da4f3;
        border-color: #4da4f3;
    }
</style>
{% endblock %}

{% block content %}
  {# NOTE: one list to rule them all! (else we potentially generate the list) #}
  {% set samples = list_samples() %}

  {% if (intro_step | default(False, True)) %}
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
      <h4 class="alert-heading">This is the training step</h4>
      <p>Use it to familiarise yourself with the platform as your answers won't be taken into account</p>

      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  {% endif %}

  {% if not((intro_step | default(False, True))) and (step == 1) %}
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
      <h4 class="alert-heading">The test has now started and your answers will be taken into account</h4>

      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  {% endif %}


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

  <div style="font-size: x-large;">
    <form action="./save" id="the_form" method="post" enctype="multipart/form-data" class="form-example">
      <div style="font-size: large; background-color: #e8f4ea; color: #000; padding: 20px; margin-top: 20px; margin-bottom:20px; border-radius: 25px;">
        Listen to the following samples and <b>rank them on how natural you think these samples are</b>.
        Please, respect the following guidelines:
        <ul>
          <li>The most natural sample should be ranked at position "1", the second most natural at position "2" and so on</li>
          <li>If you consider two or more samples to be equivalent, give them the same rank.</li>
          <li>All the samples have to be listened in their entirety at least once and ranked before moving to the next step. When you will fully play a sample, a check icon will appear in the row "Fully played?". Therefore you should have a checked icon for all the samples before the submit button activates</li>
          <li>You won't be able to go back after you submitted your ranking</li>
          <li><b>One sample is degraded on purpose and should always be indicated as "Control Sample" </b></li>
        </ul>
      </div>

      <div class="form-group" style="margin-bottom:20px;">
        <center>
          <audio id="sample" controls>
            <source id="sample_src" src="">
            Your browser does not support the <code>audio</code> element.
          </audio>
        </center>
      </div>

      <div class="form-group" style="margin-bottom:20px;">
          <table width="100%">
              <tbody>
                  <tr>
                      <td><b>System</b></td>
                      {% for sample in samples%}
                      {% set name_field = sample | generate_field_name(basename="sample_%d" % loop.index) %}
                        <td>
                          {# <input type="hidden" name="{{name_field}}" value="{{loop.index}}"> #}
                          <button type="button" class="btn btn-primary btn-mute" id="audio_{{loop.index-1}}" onclick="selectSample({{loop.index - 1}})">Sample {{loop.index}}</button>
                        </td>
                      {% endfor %}
                  </tr>
                  <tr>
                      <td><b>Fully played?</b></td>
                      {% for sample in samples %}
                      <td>
                          <img id="checked_{{loop.index-1}}" src="{{get_asset('img/checked.svg')}}" height="20px" style="display: none;" />
                      </td>
                      {% endfor %}
                  </tr>


                  <tr>
                      <td><b>Rank</b></td>
                      {% for sample in samples %}
                      {% set name_field = sample | generate_field_name(basename="rank_score_%d" % loop.index) %}
                      <td>
                          <select id="score_{{loop.index}}" name="{{name_field}}" class="form-control" required>
                              <option value="" selected disabled hidden>Choose here</option>
                              {% for _ in samples %}
                                {% if (loop.index == 1) %}
                                  <option value="{{loop.index}}">{{loop.index}} - the most natural</option>
                                {% elif (loop.index != 6) %}
                                  <option value="{{loop.index}}">{{loop.index}}</option>
                                {% endif %}
                              {% endfor %}

                              <option value="-1">Control Sample</option>
                          </select>
                      </td>
                      {% endfor %}
                  </tr>
              </tbody>
          </table>
      </div>

      <center>
        <button type="submit" id="submit" class="btn btn-primary" title="You haven't played all the samples yet">Submit</button>
      </center>
    </form>
  </div>

  <div id="overlay" onclick="closeOverlay()">
      <div id="overlay-content">
          <p><b>At least one score must have a value of 1.</b></p>
          <button onclick="closeOverlay()">Close</button>
      </div>
  </div>

  <script>

      const list_audios = [
          {% for sample in samples %}
          {% set content,mimetype = sample.get("audio")  %}
          {% if mimetype.startswith("audio") %}
          ["{{sample}}", "{{content}}"],
          {% endif %}
          {% endfor %}
      ];


      var audio = document.getElementById("sample");
      var audio_source = document.getElementById("sample_src");
      var cur_sample_index = -1;
      var cur_selected_audio_btn = null;

      const URL_MONITOR =  window.location.href + "monitor";
      const monitor_handler = async (action, value, sample_id) => {
          const body = {
              "sample_id": sample_id,
              "info_type": action,
              "info_value": value
          }
          // FIXME: the URL needs to be generalised (both base part & stage part)
          const response = await fetch(URL_MONITOR, {
              method: 'POST',
              body: JSON.stringify(body),
              headers: {
                  'Content-Type': 'application/json'
              }
          });
      }

      audio.onpause = function() {
          if (audio.currentTime < audio.duration) {
              monitor_handler("pause", audio.currentTime, list_audios[cur_sample_index][0]);
          } else {
              monitor_handler("ended", audio.currentTime, list_audios[cur_sample_index][0]);
          }
      };

      audio.onplay = function() {
          monitor_handler("play", audio.currentTime, list_audios[cur_sample_index][0]);
      };


      function selectSample(index) {
          if (cur_sample_index >= 0) {
              monitor_handler("switch_sample", ["sampleid:" + list_audios[index][0], audio.duration], list_audios[cur_sample_index][0]);
          }

          audio_source.src = list_audios[index][1];
          audio.load();
          cur_sample_index = index;


          // Update button to reflect the new status
          if (cur_selected_audio_btn) {
              cur_selected_audio_btn.disabled = false;
              cur_selected_audio_btn.classList.replace("btn-solo", "btn-mute");
          }

          cur_selected_audio_btn = document.getElementById("audio_" + index);
          cur_selected_audio_btn.disabled = true;
          cur_selected_audio_btn.classList.replace("btn-mute", "btn-solo");
          audio.play()
      }


      function validateForm() {
          for (let i = 1; i <= 6; i++) { // NOTE: 6 is hardcoded
              let scoreValue = document.getElementById('score_' + i).value;
              if (scoreValue == '1') {
                  return true;
              }
          }
          showOverlay();
          return false;
      }

      function showOverlay() {
          document.getElementById('overlay').style.display = 'block';
      }

      function closeOverlay() {
          document.getElementById('overlay').style.display = 'none';
      }

      document.getElementById('the_form').onsubmit = function() {
          return validateForm();
      };

      var played_audios = new Set();

      audio.onended = function() {
          played_audios.add(audio_source.src);

          // Enable the submit button if all audios have been played
          if (played_audios.size === list_audios.length) {
              document.getElementById('submit').disabled = false;
          }

          // Show the fact that sample is
          var checked = document.getElementById("checked_" + cur_sample_index);
          checked.style.display = "";
      };
      // Initially disable the submit button
      document.getElementById('submit').disabled = true;
  </script>
{% endblock %}
