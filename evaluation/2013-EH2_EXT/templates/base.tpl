<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{get_variable("title")}}</title>

    <!-- JQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
    <script src="https://code.jquery.com/ui/1.14.1/jquery-ui.min.js" integrity="sha256-AlTido85uXPlSyyaZNsjJXeCs07eSv3r43kyCVc8ChI=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">


    {% block head %}

    {% endblock %}
  </head>

  <body>
    <header class="row" style="margin-bottom: 30px;">
      {% block header %}
        <h1 class="display-1">{{get_variable("title")}}</h1>
      {% endblock %}

    </header>

    <nav class="navbar navbar-expand-md">
      <div class="navbar-collapse collapse w-100 order-1 order-md-0 dual-collapse2">
        <div class="mx-auto order-0">
          {# <button class="navbar-toggler" type="button" data-toggle="collapse" data-target=".dual-collapse2"> #}
          {#   <span class="navbar-toggler-icon"></span> #}
          {# </button> #}
        </div>
        <ul class="navbar-nav mr-auto">
          {% if auth.validates_connection("connected")[0] %}
            <li class="nav-item">
              Logged in as <b>{{ auth.user.user_id}}</b>, <a href="{{auth.url_deco}}" class="badge bg-danger">logout</a>.
            </li>
          {% endif %}
          <ul>
      </div>
    </nav>

    <div class="container">

      <div class="container">
        {% block content %}

        {% endblock %}
      </div>
    </div>

    <footer class="row" style="margin-top:20px;">
      <div class="col-12 text-center">
        {% block footer %}

        {% endblock %}
      </div>
    </footer>
  </body>
</html>
