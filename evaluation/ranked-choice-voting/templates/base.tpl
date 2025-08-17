<!doctype html>
<html lang="en">

  <head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">

    <title>{{title}}</title>
    <!-- JQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
    <script src="https://code.jquery.com/ui/1.14.1/jquery-ui.min.js" integrity="sha256-AlTido85uXPlSyyaZNsjJXeCs07eSv3r43kyCVc8ChI=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">

    <!-- Additional libraries -->
    {# <link href="{{get_asset('/css/helper_replikant.css')}}" rel="stylesheet"> #}
    <script src="{{get_asset('/js/blizzard.js')}}"></script>
    <link href="{{get_asset('/css/blizzard.css')}}" rel="stylesheet">

    {% block head %}
    {% endblock %}

  </head>

  <body>
    <header class="row" style="margin-bottom: 30px;">
      {% block header %}
        <h1  class="display-1">{{title}}</h1>
        <div class="col-12 text-left">
          {% if description is not none %}
            <span>{{description}}</span>
          {% endif %}
          <span></span>
        </div>
      {% endblock %}

            {# <div class="col-12 text-right"> #}
      {#   <p class="text-muted" style="letter-spacing: 1px;"> &nbsp; {%block userintel%} {% if auth.validates_connection("connected")[0] %} Logged in as {{ auth.user.id}} (<a href="{{ auth.url_deco  }} "> Log out </a>) . {% endif %}{%endblock%}</p> #}
      {# </div> #}
    </header>


    <div class="container">
      <div class="container">
        {% block content %}

        {% endblock %}
      </div>
    </div>

    <footer class="row" style="margin-top:20px;">
      <div class="col-12 text-center">
        {% block footer %}
          <img src="{{get_asset('/logos/UH.svg')}}"
               class="img-responsive center-block"
               height="100px" style="margin-right: 10px" />
             {% endblock %}
      </div>
    </footer>
  </body>
</html>
