from config.db import run_query
from movie_data import movies

print("=" * 50)
print("Loading MovieVerse Data into CognoDB...")
print("=" * 50)

# ==========================================
# CREATE GENRE NODES
# ==========================================

genres = set()

for movie in movies:

    for genre in movie["genres"]:

        genres.add(genre)

for genre in sorted(genres):

    run_query(

        """
        MERGE (:Genre {name:$name})
        """,

        {
            "name": genre
        }

    )

print(f"✅ Genres Loaded : {len(genres)}")


# ==========================================
# CREATE DIRECTOR NODES
# ==========================================

directors = set()

for movie in movies:

    directors.add(movie["director"])

for director in sorted(directors):

    run_query(

        """
        MERGE (:Director {name:$name})
        """,

        {
            "name": director
        }

    )

print(f"✅ Directors Loaded : {len(directors)}")

# ==========================================
# CREATE ACTOR NODES
# ==========================================

actors = set()

for movie in movies:

    for actor in movie["actors"]:

        actors.add(actor)

for actor in sorted(actors):

    run_query(

        """
        MERGE (:Actor {name:$name})
        """,

        {
            "name": actor
        }

    )

print(f"✅ Actors Loaded : {len(actors)}")


# ==========================================
# CREATE MOVIE NODES
# ==========================================

print("\nLoading Movies...")

for movie in movies:

    run_query(

        """

        MERGE (m:Movie {title:$title})

        SET

            m.year = $year,
            m.rating = $rating,
            m.poster = $poster,
            m.overview = $overview,
            m.trailer = $trailer

        """,

        {

            "title": movie["title"],
            "year": movie["year"],
            "rating": movie["rating"],
            "poster": movie["poster"],
            "overview": movie["overview"],
            "trailer": movie["trailer"]

        }

    )

print(f"✅ Movies Loaded : {len(movies)}")

# ==========================================
# CREATE GENRE RELATIONSHIPS
# ==========================================

print("\nCreating Genre Relationships...")

for movie in movies:

    for genre in movie["genres"]:

        run_query(

            """

            MATCH (m:Movie {title:$title})

            MATCH (g:Genre {name:$genre})

            MERGE (m)-[:BELONGS_TO]->(g)

            """,

            {
                "title": movie["title"],
                "genre": genre
            }

        )

print("✅ Genre Relationships Created")


# ==========================================
# CREATE DIRECTOR RELATIONSHIPS
# ==========================================

print("\nCreating Director Relationships...")

for movie in movies:

    run_query(

        """

        MATCH (m:Movie {title:$title})

        MATCH (d:Director {name:$director})

        MERGE (d)-[:DIRECTED]->(m)

        """,

        {
            "title": movie["title"],
            "director": movie["director"]
        }

    )

print("✅ Director Relationships Created")


# ==========================================
# CREATE ACTOR RELATIONSHIPS
# ==========================================

print("\nCreating Actor Relationships...")

for movie in movies:

    for actor in movie["actors"]:

        run_query(

            """

            MATCH (m:Movie {title:$title})

            MATCH (a:Actor {name:$actor})

            MERGE (a)-[:ACTED_IN]->(m)

            """,

            {
                "title": movie["title"],
                "actor": actor
            }

        )

print("✅ Actor Relationships Created")
# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 50)

print("📊 DATA LOADING SUMMARY")

print("=" * 50)

print(f"🎬 Movies      : {len(movies)}")
print(f"🎭 Actors      : {len(actors)}")
print(f"🎬 Directors   : {len(directors)}")
print(f"🎯 Genres      : {len(genres)}")

print("=" * 50)

print("✅ All Nodes Created Successfully!")

print("✅ All Relationships Created Successfully!")

print("✅ MovieVerse Graph Database Ready!")

print("=" * 50)

print("""
🎉 MovieVerse Data Loaded Successfully!

You can now run:

    python app.py

and start exploring MovieVerse.
""")