{% extends get_template('base.tpl') %}

{% block content %}

<h2 class="bd-content-title"> <img src="{{get_asset('/img/svg_icon/chevron-right.svg','flexeval')}}" alt=">" /> Who are you ?</h2>
<form action="./save" method="post" class="form-example">

    <h3>General Information</h3>
    <div class="form-group required">
        <label for="gender">What is your sex?</label>

        <select id="gender" name="sex" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
        </select>
    </div>

    <div class="form-group required">
        <label for="age">What is your age?</label>

        <select id="age" name="age" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="under20">Under 20</option>
            <option value="20to29">20 - 29</option>
            <option value="30to39">30 - 39</option>
            <option value="40to49">40 - 49</option>
            <option value="50to59">50 - 59</option>
            <option value="60to69">60 - 69</option>
            <option value="70to79">70 - 79</option>
            <option value="80up">80 or over</option>
        </select>
    </div>

    <h3>Language related information</h3>
    <div class="form-group required">
        <label for="english_native">Is English your native langue?</label>
        <select id="english_native" name="english_native" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="Y">Yes</option>
            <option value="N">No</option>
        </select>
    </div>

    <div id="english_dialect_div" class="form-group required">
        <label for="english_dialect">Please select your dialect:</label>
        <select id="english_dialect" name="english_dialect" class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="AU">Australian</option>
            <option value="IN">Indian/Pakistani</option>
            <option value="UK">UK</option>
            <option value="US">US</option>
            <option value="Other">Other</option>
        </select>
    </div>

    <div id="native_language_div" class="form-group required">
        <label for="native_language">Please specify your native language:</label>
        <input type="text" name="native_language" id="native_language" class="form-control" required/>
    </div>

    <div id="english_level_div" class="form-group required">
        <label for="english_level">Please specify your level of English:</label>
        <select id="english_level" name="english_level"  class="form-control" required>
            <option value="" selected disabled hidden>Choose here</option>
            <option value="bilingual">Bilingual</option>
            <option value="advanced">Advanced</option>
            <option value="intermediate">Intermediate</option>
            <option value="elementary">Elementary</option>
        </select>
    </div>

    <h3>Listening conditions related information</h3>
    <div class="form-group required">
        <label for="using_headphones">
            Are you using headphones? <b>(Headphones are strongly recommended)</b>
        </label>
        <br />
        <div class="answers">
            <input type="radio" id="using_headphones" name="using_headphones" value="yes">
            <label for="yes">Yes</label>
            <input type="radio" id="no_headphones" name="using_headphones" value="no">
            <label for="no">No</label>
        </div>
    </div>

    <div class="form-group required">
        <label for="headphones_model">What is the model of your headphones/speakers?</label>
        <input type="text" name="headphones_model" id="headphones_model" class="form-control" required />
    </div>

    <button type="submit" id="submit" class="btn btn-primary">Submit</button>
</form>

{% endblock %}
