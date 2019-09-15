import os
import sys
import spotipy
import spotipy.util as util
import json

from spotipy.oauth2 import SpotifyClientCredentials
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

import jinja2

jinja_environment = jinja2.Environment(autoescape=True, loader=jinja2.FileSystemLoader('templates'))

# necessary authentication
client_credentials_manager = SpotifyClientCredentials(client_id='e812282d3ae844fb8f04d7db0be3fa88', client_secret='ca72a07f1bfb471f8ab7cbbb5dd0cd4b')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

meter_questions = 0
tempo_questions = 0
key_questions = 0


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///music.db")

@app.route("/")
@login_required
def index():
    return redirect("/history")


@app.route("/history")
@login_required
def history():

    if session["name"] == "student":

        #finds username
        username = db.execute("SELECT username FROM users WHERE user_id = :id", id = session["user_id"])[0]["username"]

        #finds quizzes and scores for this student
        quizzes = db.execute("SELECT score, quiz_name FROM history WHERE username = :username", username = username)

        return render_template("student_history.html", quizzes = quizzes)

    if session["name"] == "teacher":

        #finds username
        username = db.execute("SELECT username FROM users WHERE user_id = :id", id = session["user_id"])[0]["username"]

        #finds quizzes
        quizzes = db.execute("SELECT quiz_name FROM quizzes WHERE teacher = :teacher", teacher = username)
        avg_scores = []

        #iterates over each quiz
        for quiz in quizzes:

            # finds sum of scores
            sum = 0
            scores = db.execute("SELECT score FROM history WHERE quiz_name = :quiz_name", quiz_name = quiz["quiz_name"])
            for score in scores:
                sum += score["score"]

            # adds quiz name and average score to the dict
            if len(scores) == 0:
                avg_scores.append({"quiz_name": quiz["quiz_name"], "score": 0})
            else:
                avg_scores.append({"quiz_name": quiz["quiz_name"], "score": sum/len(scores)})

        return render_template("teacher_history.html", scores = avg_scores)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        session["name"] = rows[0]["identity"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/take_quiz", methods=["POST", "GET"])
@login_required
def take_quiz():

    if request.method == "POST":
        quiz_name = request.form.get("quiz_name")

        #gets song ids
        meter_songs = str.split(db.execute("SELECT meter_songs FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)[0]["meter_songs"])
        tempo_songs = str.split(db.execute("SELECT tempo_songs FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)[0]["tempo_songs"])
        key_songs = str.split(db.execute("SELECT key_songs FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)[0]["key_songs"])

        return render_template("quiz.html", meter_songs = meter_songs, tempo_songs = tempo_songs, key_songs = key_songs)

    if request.method == "GET":
        return render_template("enter_quiz.html")

@app.route("/take", methods=["POST"])
@login_required
def take():

    #gets quiz name
    if request.form.get("quiz_name") is None:
        return apology("must provide quiz name", 403)
    quiz_name = request.form.get("quiz_name")

    #checks quiz name
    if len(db.execute("SELECT * FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)) == 0:
        return apology("invalid quiz name", 403)

    #gets song ids
    meter_songs = str.split(db.execute("SELECT meter_songs FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)[0]["meter_songs"])
    tempo_songs = str.split(db.execute("SELECT tempo_songs FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)[0]["tempo_songs"])
    key_songs = str.split(db.execute("SELECT key_songs FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)[0]["key_songs"])

    #intializes lists for grades
    meter_grade = 0
    tempo_grade = 0
    key_grade = 0

    for song in meter_songs:

        #finds answer
        analysis = spotify.audio_analysis(song)
        answer = int(analysis["sections"][0]["time_signature"])

        if request.form.get("meter_question" + song) is None:
            return apology("must answer every question", 403)

        #checks answer
        if (answer == int(request.form.get("meter_question" + song))):
            meter_grade += 1

    for song in tempo_songs:

        #finds answer
        analysis = spotify.audio_analysis(song)
        answer = float(analysis["sections"][0]["tempo"])

        if request.form.get("tempo_question" + song) is None:
            return apology("must answer every question", 403)

        #checks answer
        if (abs(answer - float(request.form.get("tempo_question" + song))) < abs((float(analysis["sections"][0]["tempo_confidence"])-1)*answer)):
            tempo_grade += 1

    for song in key_songs:

        #finds answer
        analysis = spotify.audio_analysis(song)
        answer = int(analysis["sections"][0]["key"])

        if request.form.get("key_question" + song) is None:
            return apology("must answer every question", 403)

        #checks answer
        if(answer == int(request.form.get("key_question" + song))):
            key_grade += 1

    #finds avg grade
    avg = (meter_grade + tempo_grade + key_grade)*100 / (len(meter_songs)+len(tempo_songs)+len(key_songs))

    username = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])[0]["username"]

    #inserts score into database
    db.execute("INSERT INTO history (quiz_name, username, score) VALUES (:quiz_name, :username, :score)",
    quiz_name = quiz_name, username = username, score = avg)

    return render_template("quiz_graded.html", meter_grade = meter_grade/len(meter_songs)*100, tempo_grade = tempo_grade/len(tempo_songs)*100, key_grade = key_grade/len(key_songs)*100)

@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        username = request.form.get("username")

        # Check if username is taken
        exists = db.execute("SELECT username FROM users WHERE username = :username",
                            username=username)
        if not len(exists) == 0:
            return apology("username is taken", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        password = request.form.get("password")

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        confirmation = request.form.get("confirmation")

        # Ensure confirmation was valid
        if not password == confirmation:
            return apology("passwords must match", 400)

        # Ensure identity was submitted
        if not request.form.get("identity"):
            return apology("must provide identity", 400)

        identity = request.form.get("identity")

        # Insert user into database
        db.execute("INSERT INTO users (username, hash, identity) VALUES (:username, :hash, :identity)",
                    username = username, hash = generate_password_hash(password), identity = identity)

        # Redirect to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

#checks if username is taken
@app.route("/check", methods=["GET"])
def check():
    username = request.args.get("username")
    return jsonify(len(username) > 0 and len(db.execute("SELECT * FROM users WHERE username = :username",
                                                        username = username)) == 0)
#checks if quiz name is taken
@app.route("/check_name", methods=["GET"])
def check_name():
    quiz_name = request.args.get("quiz_name")
    return jsonify(len(quiz_name) > 0 and len(db.execute("SELECT * FROM quizzes WHERE quiz_name = :quiz_name",
                                                        quiz_name = quiz_name)) == 0)

@app.route("/scores", methods=["POST"])
@login_required
def scores():
    name = request.form.get("quiz_name")

    #gets scores
    scores = db.execute("SELECT username, score FROM history WHERE quiz_name = :name", name = name)

    return render_template("quiz_score.html", scores = scores)

#generates form to make quiz
@app.route("/make_form", methods=["POST", "GET"])
@login_required
def make_form():
    if request.method == "GET":
        return render_template("make_form.html")

    if request.method == "POST":
        global meter_questions
        meter_questions = int(request.form.get("meter_questions"))
        global tempo_questions
        tempo_questions = int(request.form.get("tempo_questions"))
        global key_questions
        key_questions = int(request.form.get("key_questions"))

        return render_template("quiz_form.html", meter_questions = meter_questions, tempo_questions = tempo_questions, key_questions =  key_questions )

#generates quiz
@app.route("/make_quiz", methods=["POST"])
@login_required
def make_quiz():
    meter_songs = ""
    tempo_songs = ""
    key_songs = ""

    #accesses number of each type of question
    global meter_questions
    global tempo_questions
    global key_questions

    for i in range( meter_questions):
        #searches for tracks
        if request.form.get("meter_question" + str(i)) is None:
            return apology("must provide a value for all fields", 403)
        tracks = spotify.search(request.form.get("meter_question" + str(i)), type = "track")

        #extracts track id
        meter_songs += tracks["tracks"]["items"][0]["id"] + " "

    for i in range( tempo_questions):
        #searchs for tracks
        if request.form.get("tempo_question" + str(i)) is None:
            return apology("must provide a value for all fields", 403)
        tracks = spotify.search(request.form.get("tempo_question" + str(i)), type = "track")

        #extracts track id
        tempo_songs += tracks["tracks"]["items"][0]["id"] + " "

    for i in range( key_questions):
        #searches for tracks
        if request.form.get("key_question" + str(i)) is None:
            return apology("must provide a value for all fields", 403)
        tracks = spotify.search(request.form.get("key_question" + str(i)), type = "track")

        #extracts track id
        key_songs += tracks["tracks"]["items"][0]["id"] + " "

    if request.form.get("quiz_name") is None:
        return apology("must provide quiz name", 403)

    quiz_name = request.form.get("quiz_name")

    #checks if quiz name is taken
    if not (len(quiz_name) > 0 and len(db.execute("SELECT * FROM quizzes WHERE quiz_name = :quiz_name", quiz_name = quiz_name)) == 0):
        return apology("quiz name is taken", 403)

    username = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id = session["user_id"])[0]["username"]

    #inserts quiz into database
    db.execute("INSERT INTO quizzes (quiz_name, teacher, meter_songs, tempo_songs, key_songs) VALUES(:quiz_name, :teacher, :meter_songs, :tempo_songs, :key_songs)",
    quiz_name = quiz_name, teacher = username, meter_songs = meter_songs, tempo_songs = tempo_songs, key_songs = key_songs)

    return render_template("share.html", quiz_name = quiz_name)

def errorhandler(e):
    """Handle error"""
    return apology("sorry yikes", 400)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

