#!/usr/bin/env python
# Credits - Similar structure used as here:
# http://blog.sampingchuang.com/setup-user-authentication-in-flask/

from flask import Flask, render_template, request, jsonify, json, redirect
from urllib2 import Request, urlopen
from flask.ext.login import login_required, login_user, current_user, logout_user, confirm_login, login_fresh
from users.user import User
from extensions import db, login_manager
import urllib
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.secret_key = 'secret key'

# flask-sqlalchemy
db.init_app(app)

# flask-login
# login_manager.login_view = 'frontend.index'
# login_manager.refresh_view = 'frontend.index'

@login_manager.user_loader
def load_user(id):
  return User.query.get(id)

login_manager.setup_app(app)

with app.app_context():
  # db.drop_all(bind=None)
  db.create_all(bind=None)


base_route = 'http://api.themoviedb.org/3/'
api_key = '21191bb1a231eae99a7864b641d45dc3'

@app.route('/')
def renderPage():
  """
  When the server first starts, route to the home page
  """
  return render_template("index.html")

@app.route('/login-page')
def renderLogin():
  """
  When the user tries to access login, route to the login page
  """
  return render_template("login.html")

@app.route('/register-page')
def renderRegistration():
  """
  When the user tries to access registration, route to the registration page
  """
  return render_template("register.html")

@app.route('/register/')
def registerUser():
  """
  Use the given username and password to create a user if it doesn't already exist
  """
  if User.user_name_exists(request.args['username']):
    return "-1"
  else:
    user = User(
           user_name=request.args['username'],
           password=request.args['password'],
           recent_results=['1', '2', '3'])
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return "ok"

@app.route('/login/')
def loginUser():
  """
  Use the given username and password to either login the user or return an error
  """
  user, authenticated = User.authenticate(request.args['username'], request.args['password'])
  if user != None and authenticated:
    login_user(user)
    return "ok"
  else:
    return "-1"

@app.route('/logout')
def logoutUser():
  """
  Logs the current user out of their account
  """
  logout_user()
  return render_template("index.html")

@app.route('/actors/', methods =['GET'])
def cross_reference_actors():
  """
  Endpoint for the actor cross-reference search
  Takes the two actor strings from the front-end
  Returns an array of common movies between the actors
  """
  if (current_user.is_authenticated):
    if current_user.recent_first == request.args['firstActor'] and current_user.recent_second == request.args['secondActor']:
      return jsonify({
        'commonMovies': current_user.recent_results
      })

  first_actor_id = get_actor_id(request.args['firstActor'])
  second_actor_id = get_actor_id(request.args['secondActor'])

  first_actor_credits = get_actor_credits(first_actor_id)
  second_actor_credits = get_actor_credits(second_actor_id)

  common_movies = get_common_movies(first_actor_credits, second_actor_credits)

  current_user.recent_first = request.args['firstActor']
  current_user.recent_second = request.args['secondActor']
  current_user.recent_results = common_movies
  db.session.commit()

  return jsonify({
    'commonMovies': common_movies
  })

@app.route('/movies/', methods =['GET'])
def cross_reference_movies():
  """
  Endpoint for the movie cross-reference search
  Takes the two movie strings from the front-end
  Returns an array of common actors between the movies
  """
  if (current_user.is_authenticated):
    if current_user.recent_first == request.args['firstMovie'] and current_user.recent_second == request.args['secondMovie']:
      return jsonify({
        'commonActors': current_user.recent_results
      })

  first_movie_id = get_movie_id(request.args['firstMovie'])
  second_movie_id = get_movie_id(request.args['secondMovie'])

  first_movie_cast = get_movie_cast(first_movie_id)
  second_movie_cast = get_movie_cast(second_movie_id)

  common_actors = get_common_actors(first_movie_cast, second_movie_cast)

  current_user.recent_first = request.args['firstMovie']
  current_user.recent_second = request.args['secondMovie']
  current_user.recent_results = common_actors
  db.session.commit()

  return jsonify({
    'commonActors': common_actors
  })

@app.route('/login', methods=['GET', 'POST'])
def login():
  return flask.render_template('index.html')

# @login_manager.user_loader
#   def load_user(id):
#     return User.query.get(id)

def get_actor_id(actor_name):
  """
  Takes in an actor_name string
  Returns the TMDB ID of the actor
  """
  query = urllib.urlencode({
    'query': actor_name,
    'api_key': api_key,
  })
  actor_request = Request(base_route + 'search/person?' + query)
  actor = parse_request(actor_request)
  return actor['results'][0]['id']

def get_actor_credits(actor_id):
  """
  Takes in the TMDB ID of an actor
  Returns all of the movie credits of the actor with that ID
  """
  query = urllib.urlencode({
    'api_key': api_key,
  })
  credits_request = Request(base_route + 'person/' + str(actor_id) + '/movie_credits?' + query)
  credits = parse_request(credits_request)
  return credits['cast']

def parse_request(tmdb_request):
  """
  Takes a Request object, opens it, reads it as json, then converts to a python object
  Returns the python object representing the data in the Request
  """
  parsed_json = urlopen(tmdb_request).read()
  return json.loads(parsed_json)

def get_common_movies(first_actor_credits, second_actor_credits):
  """
  Takes two arrays of actor credits, first_actor_credits and second_actor_credits
  Returns an array of movies that are common to both actors
  """
  common_movies = []
  for first_movie in first_actor_credits:
    for second_movie in second_actor_credits:
      if first_movie['id'] == second_movie['id']:
        common_movies.append({
          'title': first_movie['title'],
          'date': first_movie['release_date'][0:4],
        })
  return common_movies

def get_movie_id(movie_name):
  """
  Takes in a movie_name string
  Returns the TMDB ID of the movie
  """
  query = urllib.urlencode({
    'query': movie_name,
    'api_key': api_key,
  })
  movie_request = Request(base_route + 'search/movie?' + query)
  movie = parse_request(movie_request)
  return movie['results'][0]['id']

def get_movie_cast(movie_id):
  """
  Takes in the TMDB ID of an movie
  Returns the cast of the movie with the specific ID
  """
  query = urllib.urlencode({
    'api_key': api_key,
  })
  cast_request = Request(base_route + 'movie/' + str(movie_id) + '/credits?' + query)
  cast = parse_request(cast_request)
  return cast['cast']

def get_common_actors(first_movie_cast, second_movie_cast):
  """
  Takes two arrays of movie casts, first_movie_cast and second_movie_cast
  Returns an array of actors that are common to both movies
  """
  common_actors = []
  for first_actor in first_movie_cast:
    for second_actor in second_movie_cast:
      if first_actor['id'] == second_actor['id']:
        common_actors.append({
          'name': first_actor['name'],
        })
  return common_actors

if __name__ == '__main__':
  app.run(debug=True)