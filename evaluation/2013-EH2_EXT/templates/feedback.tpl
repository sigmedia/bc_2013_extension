{% extends 'base.tpl' %}

{% block head %}
<script>
    $(document).ready(function(){
        $("input[type=range]").map(function() {
            var poper = $(this).popover();

            // Read value on change
            $(this).on("mouseleave change click",function(){
                $(this).popover('dispose');
                score = $(this).val()
                if (score == 5) {
                    label = "Difficult";
                } else if (score == 4) {
                    label = "Slightly difficult";
                } else if (score == 3) {
                    label = "Fair";
                } else if (score == 2) {
                    label = "Slightly easy";
                } else if (score == 1) {
                    label = "Easy";
                }

                $(this).attr("data-content", label + " (" + score + ")");
                $(this).popover('update');
                $(this).popover('toggle');

            });

        }).get().join();

    });

</script>
{% endblock %}


{% block content %}

<h2 class="bd-content-title">Free form</h2>

<form action="./save" method="post" class="form-example">
    <h3>Environment related information</h3>
    <div class="form-group required">
        <label for="same_environment">Did you listen to all samples in the same environment?</label>

        <select id="same_environment"  name="same_environment" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="Y">Yes</option>
            <option value="N">No</option>
        </select>
    </div>

    <div class="form-group required">
        <label for="environment">What kind of environment were you in when listening to the speech samples in this study?</label>

        <select id="environment" name="environment" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="quiet_all_time">Quiet all the time</option>
            <option value="quiet_mostly">Quiet most of the time</option>
            <option value="equal_quiet_noisy">Equally quiet and noisy</option>
            <option value="noisy_mostly">Noisy most of the time</option>
            <option value="noisy_all_time">Noisy all the time</option>
        </select>
    </div>

    <h3>Speech technology/science related information</h3>
    <div class="form-group required">
        <label for="tts_worker">Do you work in the field of speech technology?</label>
        <select id="tts_worker" name="tts_worker" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="Y">Yes</option>
            <option value="N">No</option>
        </select>
    </div>

    <div class="form-group required">
        <label for="speech_science_worker">Do you work in the field of speech science?</label>
        <select id="speech_science_worker" name="speech_science_worker" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="Y">Yes</option>
            <option value="N">No</option>
        </select>
    </div>

    <div class="form-group required">
        <label for="tts_familiarity">Before participating in this research study, how often did you listen to synthetic speech?</label>
        <select id="tts_familiarity" name="tts_familiarity" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="daily">Every day</option>
            <option value="weekly">Once a week</option>
            <option value="monthly">Once a month</option>
            <option value="yearly">A few times a year</option>
            <option value="rarely">A few times ever</option>
            <option value="never">Never</option>
            <option value="unsure">I'm not sure</option>
        </select>
    </div>


    <h3>Blizzard challenge related information</h3>
    <div class="form-group required">
        <label for="participated_blizzard">Have you previously participated in a listening test campaign of one of the previous editions of the blizzard challenge?</label>

        <select id="participated_blizzard" name="participated_blizzard" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="Y">Yes</option>
            <option value="N">No</option>
        </select>
    </div>

    <div id="previous_challenges_div" class="form-group" required>
        <label for="previous_challenges">Please indicate the year(s) of the challenge(s) (<b>separated by commas</b>)</label>
        <input type="text" name="previous_challenges" id="previous_challenges" class="form-control" />
    </div>

    <h3>Evaluation feedback</h3>
    <div class="form-group">
        <label for="freeform_feedback">Do you have any comments about the present study? Please feel free to provide them to us in the following freeform text area:</label>

        <textarea id="freeform_feedback" name="freeform_feedback" rows="4" cols="50">
        </textarea>
    </div>


    <button type="submit" id="submit" class="btn btn-primary">Submit</button>
</form>

{% endblock %}
