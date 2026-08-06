from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session,
    flash
)

import sqlite3
from auth_db import create_user_table

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config.old_db import (
    verify_connection,
    get_movies,
    search_movies,
    get_movie,
    get_recommendations,
    get_actor,
    get_director,
    get_genre,
    get_total_movies,
    get_total_actors,
    get_total_directors,
    get_total_genres
)

# ==========================================
# APP CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = "movieverse_secret_key"

verify_connection()

create_user_table()

# ==========================================
# SIGNUP
# ==========================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Already Logged In
    if "user" in session:
        return redirect("/")

    if request.method == "POST":

        username = request.form["username"].strip()

        email = request.form["email"].strip()

        password = generate_password_hash(
            request.form["password"]
        )

        conn = sqlite3.connect("users.db")

        cursor = conn.cursor()

        try:

            cursor.execute(

                """
                INSERT INTO users
                (username,email,password)
                VALUES(?,?,?)
                """,

                (username,email,password)

            )

            conn.commit()

            flash("✅ Account Created Successfully!")

            return redirect("/login")

        except sqlite3.IntegrityError:

            flash("❌ Email Already Exists!")

        finally:

            conn.close()

    return render_template("signup.html")


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET","POST"])
def login():

    # Already Logged In
    if "user" in session:
        return redirect("/")

    if request.method == "POST":

        email = request.form["email"].strip()

        password = request.form["password"]

        conn = sqlite3.connect("users.db")

        cursor = conn.cursor()

        cursor.execute(

            "SELECT * FROM users WHERE email=?",

            (email,)

        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(

            user[3],

            password

        ):

            session["user"] = user[1]

            flash(f"🎉 Welcome {user[1]}!")

            return redirect("/")

        flash("❌ Invalid Email or Password!")

    return render_template("login.html")


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.pop("user",None)

    flash("👋 Logged Out Successfully!")

    return redirect("/login")

# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    keyword = request.args.get("search", "").strip()

    sort = request.args.get("sort", "title")

    if keyword:

        movies = search_movies(keyword)

    else:

        movies = get_movies(sort)

    return render_template(

        "index.html",

        movies=movies,

        total_movies=get_total_movies(),

        total_actors=get_total_actors(),

        total_directors=get_total_directors(),

        total_genres=get_total_genres(),

        sort=sort

    )


# ==========================================
# MOVIE DETAILS
# ==========================================

@app.route("/movie/<title>")
def movie_details(title):

    if "user" not in session:
        return redirect("/login")

    movie = get_movie(title)

    if movie is None:

        return render_template(
            "404.html"
        ),404

    recommendations = get_recommendations(title)

    return render_template(

        "movie_details.html",

        movie=movie,

        recommendations=recommendations

    )

# ==========================================
# ACTOR PAGE
# ==========================================

@app.route("/actor/<name>")
def actor(name):

    if "user" not in session:
        return redirect("/login")

    actor = get_actor(name)

    if actor is None:

        return "<h2>Actor Not Found</h2>",404

    return render_template(

        "actors.html",

        actor=actor

    )


# ==========================================
# DIRECTOR PAGE
# ==========================================

@app.route("/director/<name>")
def director(name):

    if "user" not in session:
        return redirect("/login")

    director = get_director(name)

    if director is None:

        return "<h2>Director Not Found</h2>",404

    return render_template(

        "directors.html",

        director=director

    )


# ==========================================
# GENRE PAGE
# ==========================================

@app.route("/genre/<name>")
def genre(name):

    if "user" not in session:
        return redirect("/login")

    genre = get_genre(name)

    if genre is None:

        return "<h2>Genre Not Found</h2>",404

    return render_template(

        "genre.html",

        genre=genre

    )
# ==========================================
# FAVORITES
# ==========================================

@app.route("/favorites")
def favorites():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "favorites.html"
    )


# ==========================================
# API
# ==========================================

@app.route("/api/movies")
def api_movies():

    if "user" not in session:
        return jsonify(
            {"error":"Unauthorized"}
        ),401

    return jsonify(
        get_movies()
    )


# ==========================================
# TOP RATED
# ==========================================

@app.route("/top-rated")
def top_rated():

    if "user" not in session:
        return redirect("/login")

    movies = sorted(

        get_movies(),

        key=lambda x:x["rating"],

        reverse=True

    )

    return render_template(

        "top_rated.html",

        movies=movies

    )


# ==========================================
# TRENDING
# ==========================================

@app.route("/trending")
def trending():

    if "user" not in session:
        return redirect("/login")

    movies = [

        movie

        for movie in get_movies()

        if movie["rating"] >= 8.5

    ]

    return render_template(

        "trending.html",

        movies=movies

    )


# ==========================================
# 404 PAGE
# ==========================================

@app.errorhandler(404)
def page_not_found(e):

    return render_template(
        "404.html"
    ),404


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )