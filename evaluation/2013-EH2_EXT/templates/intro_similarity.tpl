{% extends get_template('base.tpl') %}

{% block content %}


<h2 class="bd-content-title">
    Introduction to section 1
</h2>

<form action="./save" method="post" enctype="multipart/form-data" class="form-example">

    <div class="">
        In each part of this section you will be able to listen to 4 sentences spoken by the same voice and also to one other new sentence.
        You will choose a score that expresses your opinion of <b>how similar the voice in the new sentence sounds to the voice in the 4 reference sentences.</b>
        <br /> <br />
    </div>

    Listen to the four reference sentences :
        <br />
        <center>
            <audio id="ref_A" controls> <!-- readall> -->
                <source src="{{get_asset('/ref_samples/booksent_2013_0057.wav')}}">
                Your browser does not support the <code>audio</code> element.
            </audio>
            <br />
            <audio id="ref_B" controls> <!-- readall> -->
                <source src="{{get_asset('/ref_samples/booksent_2013_0077.wav')}}">
                Your browser does not support the <code>audio</code> element.
            </audio>
            <br />
            <audio id="ref_C" controls> <!-- readall> -->
                <source src="{{get_asset('/ref_samples/booksent_2013_0043.wav')}}">
                Your browser does not support the <code>audio</code> element.
            </audio>
            <br />
            <audio id="ref_D" controls> <!-- readall> -->
                <source src="{{get_asset('/ref_samples/booksent_2013_0088.wav')}}">
                Your browser does not support the <code>audio</code> element.
            </audio>
        </center>
    </div>

    <br />
    <br />
    <fieldset class="form-group">
        <legend class="col-form-label">
            <strong>Question: </strong> How do you judge the <strong>quality</strong> of the following sample?
        </legend>

        <div class="form-group" style="margin-bottom:10px;">
            <center>
                <audio id="sample" controls readall>
                    <source src="{{get_asset('/ref_samples/booksent_2013_0088.wav')}}">
                    Your browser does not support the <code>audio</code> element.
                </audio>
            </center>

            <select id="sim_score"  class="form-control" required>
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
