{% extends get_template('base.tpl') %}

{% block content %}
<form action="./register" method="post" class="form-example justified">
    <h3>Lead Researcher(s)</h3>
    <p>
        <b>Sébastien Le Maguer</b> - Email: lemagues@tcd.ie <br />
        SIGMEDIA / ADAPT Centre, Electronic and Electrical Engineering.  <br />
        Aras an Phiarsaigh, Trinity College Dublin <br />
        College Green, Dublin 2, <br />
        Ireland  <br />
    </p>

    <h3>Background of the research</h3>
    <p>
        During the last decade, the quality of synthetic speech reached unprecedented territories.
        Technologies such as google Tacotron/WaveNet can synthesise speech which is almost indistinguishable from human speech.
        However, explaining the decisions made by the models at the core of speech synthesis technology remains challenging.
    </p>

    <p>
        The present study aims to enrich an existing dataset by asking human listeners to evaluate synthetic speech samples.
        From this dataset, further experiments will be conducted.
        The end goal of these experiments is to better understand the behaviour and the limits of the models used in modern speech synthesis systems.
    </p>

    <h3>Procedure of the study</h3>
    <p>
        This study has three parts.

        First, you will be asked to fill out a questionnaire.
        It is composed of questions addressing the following topics:
        <ul>
            <li>your sex,</li>
            <li>your age,</li>
            <li>your English proficiency,</li>
            <li>your language background,</li>
            <li>the hardware you are using to listen to the speech samples.</li>
        </ul>
    </p>

    <p>

        After filling out the questionnaire, you will start the subjective evaluation.
        This part consists of the following 7 sections:
        <dl>
            <dt>Section 1</dt>
            <dd>
                In each step of this section, you will be able to listen to 4 sentences spoken by the same voice and also to one other new sentence.
                You will choose a score that expresses your opinion of <b>how similar the voice in the new sentence sounds to the voice in the 4 reference sentences.</b>
            </dd>

            <dt>Sections 2,3,4,5</dt>
            <dd>
                In these sections, after you listen to each sentence, you will choose a score for the audio file you've just heard.
                This score should reflect your opinion of how <b>natural</b> or <b>unnatural</b> the sentence sounded.
                You should not judge the grammar or content of the sentence, just how it <b><i>sounds</i></b>.
                The scale is from <b>1 [Completely Unnatural] to 5 [Completely Natural]</b>.
            </dd>

            <dt>Sections 6,7</dt>
            <dd>
                In these sections, you will be presented with one sample to evaluate.
                You will listen to a sentence and then type in what you heard.
                <b>The sentences in this section are not intended to make sense.</b>
            </dd>
        </dl>

        There are <b>no wrong answers for all these sections as you are not evaluated</b>, the systems you will listen to are!
    </p>

    <p>
        Finally, you will have to fill out a final questionnaire.
        It asks additional questions which help us to better understand the answers you gave during the subjective evaluation.

        You will also have the opportunity to provide any feedback in a freeform section.
    </p>

    <p>
        The last page of the test will summarize the information you need if you want to access your data after the campaign.
        If you have been recruited with Prolific, the completion code will be part of the communicated information.
    </p>

    <h3>Time required</h3>
    <p>
        The protocol is designed to last around 30 minutes but no more than 45 minutes.
    </p>

    <h3>Confidentiality</h3>
    <p>
        Your identity will be kept confidential.
        If signed by you, this consent form will be kept locked separately from the data we collect during the experiment.
        It will not be possible to link the data we collect to your name.
        The data we collect will constitute a dataset dedicated to the analysis of synthetic speech.
        Your data will be analysed with the data collected from other participants, and generalised results and conclusions drawn from these experiments will be submitted for publication at conferences and/or scientific journals.
        Your name will not be used in any report or article.
    </p>

    <h3>Declaration</h3>
    <ul>
        <li>I am 18 years or older and am competent to provide consent.</li>
        <li>I have read a document providing information about this research and this consent form. I have had the opportunity to ask questions, and all my questions have been answered to my satisfaction. I understand the description of the research that is being provided to me.</li>
        <li>I agree that my data is used for scientific purposes, and I have no objection that my data is published in scientific publications in a way that does not reveal my identity.</li>
        <!-- <li>I understand that if I make illicit activities known, these will be reported to appropriate authorities.</li> -->
        <li>I understand that I may withdraw at any time without penalty for <b>a period of 1 month</b>. After this period, it will no longer be possible to withdraw.</li>
        <li>I understand that the collected data can be shared in an open-source dataset</li>
        <li>I freely and voluntarily agree to be part of this research study, though without prejudice to my legal and ethical rights.</li>
        <li>I understand that my participation is fully anonymous and that no personal details about me will be recorded except the pieces of information mentioned earlier.</li>
        <!-- <li>I understand that if I or anyone in my family has a history of epilepsy, I am proceeding at my own risk.</li> -->
        <li>I have received a copy of this agreement.</li>
    </ul>

    <p>
        By proceeding to the next step, I consent to participate in this study.
        I also consent to the collection of the data.
        I also consent to the data processing necessary to enable my participation and achieve this study's research goals.
    </p>

    <h3>Statement of investigator’s responsibility</h3>
    <p>
        I have explained the nature and purpose of this research study, the procedures to be undertaken and any risks that may be involved.
        I have offered to answer any questions and fully answered such questions.
        I believe that the participant understands my explanation and has freely given informed consent.
    </p>

    <h3>Participants acceptance details</h3>

    <div class="form-group required">
        <label for="email">Enter your email <b>(if you have been recruited via prolific, the format of the email should be &lt;prolific_id&gt;@prolific.com)</b>: </label>
        <input type="email" name="email" id="email" class="form-control" required>
    </div>


    <div class="form-check required">
        <input type="checkbox" class="form-check-input" id="legalterms" required>
        <label class="form-check-label" for="legalterms">I acknowledge having read and accept the above conditions</a>.</label>
    </div>

    <br />
    <center>
        <button type="submit" id="submit" class="btn btn-primary">Start/Resume the test</button>
    </center>
</form>
{% endblock %}
