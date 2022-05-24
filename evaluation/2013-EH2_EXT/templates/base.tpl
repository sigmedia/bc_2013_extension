<html>

  <head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{{get_asset('/img/favicon.ico','flexeval')}}" />

    <title> {{ get_variable("title",default_value="flexeval")}} </title>

    <!-- JQuery -->
    <script src="{{get_asset('/js/jquery-3.4.1.min.js','flexeval')}}"></script>
    <script src="{{get_asset('/js/jquery-ui.min.js','flexeval')}}"></script>
    <link href="{{get_asset('/css/jquery-ui.min.css','flexeval') }}" rel="stylesheet">

    <!-- Bootstrap Core CSS -->
    <script src="{{get_asset('/js/popper.min.js','flexeval')}}"></script>
    <link href="{{get_asset('/css/bootstrap-4.4.1/bootstrap.min.css','flexeval') }}" rel="stylesheet">
    <script src="{{get_asset('/js/bootstrap-4.4.1/bootstrap.min.js','flexeval') }}"></script>

    <!-- Additional libraries -->
    <script src="{{get_asset('/js/flexeval.js','flexeval')}}"></script>
    <link href="{{get_asset('/css/flexeval.css','flexeval')}}" rel="stylesheet">

    <!-- Current experience library -->
    <script src="{{get_asset('/js/blizzard.js')}}"></script>
    <link href="{{get_asset('/css/blizzard.css')}}" rel="stylesheet">

    {% block head %}
    {% endblock %}

  </head>

  <body>
    <div class="container">
      <div class="row">
        <div class="col">
        </div>
        <div class="col-18">
          <header class="row">
            {% block header %}
            <h1  class="display-1"><a href="/">{{get_variable("title", default_value="FlexEval")}}</a></h1>
            <div class="col-12 text-left">
              {% if get_variable("description") is not none %}
              <span>{{get_variable("description")}}</span>
              {% endif %}
              <span></span>
            </div>
            {% endblock %}

          <div class="col-12 text-right">
              <p class="text-muted" style="letter-spacing: 1px;"> &nbsp; {%block userintel%} {% if auth.validates_connection("connected")[0] %} Logged in as {{ auth.user.id}} (<a href="{{ auth.url_deco  }} "> Log out </a>) . {% endif %}{%endblock%}</p>
          </div>

          </header>


          <div class="row">
            <div class="container">
              <div class="row">
                <div class="col-1"></div>
                <section class="col-9">
                  <div class="container">
                    {% block content %}

                    {% endblock %}
                  </div>
                </section>
                <div class="col-2"></div>
              </div>
            </div>
          </div>

          <footer class="row" style="margin-top:20px;">
            <div class="col-12 text-center">
              {% block footer %}
              <img src="{{get_asset('/logos/Adapt.svg')}}"
                   class="img-responsive center-block"
                   height="100px" style="margin-right: 10px" />
              <img src="{{get_asset('/logos/TCD.svg')}}"
                   class="img-responsive center-block"
                   height="100px" style="margin-right: 10px" />
              {% endblock %}
            </div>

            <div class="col-12 text-center" style="margin-top:20px;">
              <p class="text-muted" style="letter-spacing: 2px;">
                {% if get_variable("authors") is not none %}
                Protocol designed by {{get_variable("authors")}} ({{get_variable("email")}}). <br />
                {% endif %}
                {% if get_variable("helpers") is not none %}
                Test implemented by {{get_variable("helpers")}}.  <br />
                {% endif %}

                <a href="{{make_url('/')}}">Privacy Policy & GCU.</a>
              </p>

              <p class="text-muted" style="letter-spacing: 2px;">
                Powered by <a href="https://gitlab.inria.fr/expression/tools/FlexEval">FlexEval</a>.
              </p>
            </div>
          </footer>
        </div>
      </div>

  </body>
</html>
