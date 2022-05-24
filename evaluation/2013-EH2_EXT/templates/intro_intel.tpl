{% extends get_template('base.tpl') %}

{% block content %}

<h2 class="bd-content-title">
    <img src="{{get_asset('/img/svg_icon/chevron-right.svg','flexeval')}}" alt=">" />
    Introduction to sections 6 and 7
</h2>

<form action="./save" method="post" enctype="multipart/form-data" class="form-example">

    <fieldset class="form-group">
        <legend class="col-form-label">
            <p>
                In the following two sections, we just wish to determine whether or not the words you hear are understandable.
                <b>In each part you will listen to a sentence and then type in what you heard.</b>
                The sentences in this section are not intended to make sense.
            </p>

            <p>
                Please complete all parts of these sections even if it is difficult to enter a response.
                Do not be concerned about &quot;right&quot; or &quot;wrong&quot; answers.
                Just type in what you hear.
                <br><br>
                Please try to enter all of the words you hear, but <b>do not enter any comment.</b>
                If you cannot hear any sound coming out of the headphones, please make sure that your browser can handle embedded audio players (all current browsers do), and that you have not turned javascript off.
                If you can hear the audio, but you cannot understand no words at all, just write <b>"&lt;&gt;"</b> (without the quotes) and nothing else.
                If you can understand some,but not all of the words, just type in the ones you heard.
            </p>
            <p>
                <b>Listen to the audio file below, and type what you hear into the text box.&nbsp;</b>
                <br><br>
            </p>
        </legend>

        <div class="form-group" style="margin-bottom:10px;">

            <audio id="sample" controls readall>
                <source src="{{get_asset('/ref_samples/booksent_2013_0057.wav')}}">
                Your browser does not support the <code>audio</code> element.
            </audio>

            <div class="form-group required">
                <label for="transcription">Transcription:</label>
                <input type="text" id="transcription" class="form-control" required />
            </div>
        </div>
    </fieldset>

    <button type="submit" id="submit" class="btn btn-primary">Submit</button>
</form>
{% endblock %}
