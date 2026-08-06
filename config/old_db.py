from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import atexit

# ==========================
# Load Environment Variables
# ==========================

load_dotenv()

URI = os.getenv("DB_URI")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")

# ==========================
# Neo4j Driver
# ==========================

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

# ==========================
# Verify Connection
# ==========================

def verify_connection():

    try:

        driver.verify_connectivity()

        print("✅ Connected to CognoDB Successfully!")

    except Exception as e:

        print("❌ Connection Failed")
        print(e)

# ==========================
# Close Connection
# ==========================

def close_connection():

    driver.close()

atexit.register(close_connection)

# ==========================
# Execute Query
# ==========================

def run_query(query, parameters=None):

    with driver.session() as session:

        session.run(
            query,
            parameters or {}
        ).consume()

# ==========================
# Home Page Movies
# ==========================

def get_movies(sort="title"):

    order = {
        "title": "m.title ASC",
        "rating": "m.rating DESC",
        "year": "m.year DESC"
    }.get(sort, "m.title ASC")

    query = f"""
    MATCH (m:Movie)

    WHERE m.poster IS NOT NULL

    RETURN

        m.title AS title,
        m.year AS year,
        m.rating AS rating,
        m.poster AS poster,
        m.trailer AS trailer

    ORDER BY {order}
    """

    with driver.session() as session:

        result = session.run(query)

        movies = []

        for record in result:

            movies.append({

                "title": record["title"],
                "year": record["year"],
                "rating": record["rating"],
                "poster": record["poster"],
                "trailer": record["trailer"]

            })

        return movies

# ==========================
# Search Movies
# ==========================

def search_movies(keyword):

    query = """

    MATCH (m:Movie)

    OPTIONAL MATCH (m)-[:BELONGS_TO]->(g:Genre)

    WITH m, collect(g.name) AS genres

    WHERE

        toLower(m.title) CONTAINS toLower($keyword)

        OR

        any(
            genre IN genres
            WHERE toLower(genre)
            CONTAINS toLower($keyword)
        )

    RETURN DISTINCT

        m.title AS title,
        m.year AS year,
        m.rating AS rating,
        m.poster AS poster,
        m.trailer AS trailer

    ORDER BY m.title

    """

    with driver.session() as session:

        result = session.run(
            query,
            keyword=keyword
        )

        movies = []

        for record in result:

            movies.append({

                "title": record["title"],
                "year": record["year"],
                "rating": record["rating"],
                "poster": record["poster"],
                "trailer": record["trailer"]

            })

        return movies

# ==========================
# Movie Details
# ==========================

def get_movie(title):

    query = """

    MATCH (m:Movie {title:$title})

    OPTIONAL MATCH
    (d:Director)-[:DIRECTED]->(m)

    OPTIONAL MATCH
    (a:Actor)-[:ACTED_IN]->(m)

    OPTIONAL MATCH
    (m)-[:BELONGS_TO]->(g:Genre)

    RETURN

        m.title AS title,
        m.year AS year,
        m.rating AS rating,
        m.poster AS poster,
        m.overview AS overview,
        m.trailer AS trailer,

        collect(DISTINCT a.name) AS actors,

        collect(DISTINCT g.name) AS genres,

        d.name AS director

    """

    with driver.session() as session:

        record = session.run(
            query,
            title=title
        ).single()

        if not record:
            return None

        return {

            "title": record["title"],
            "year": record["year"],
            "rating": record["rating"],
            "poster": record["poster"],
            "overview": record["overview"],
            "trailer": record["trailer"],
            "actors": record["actors"],
            "genres": record["genres"],
            "director": record["director"]

        }

# ==========================
# Recommendations
# ==========================

def get_recommendations(title):

    query = """

    MATCH (m:Movie {title:$title})

    OPTIONAL MATCH
    (m)-[:BELONGS_TO]->(g:Genre)<-[:BELONGS_TO]-(gm:Movie)

    OPTIONAL MATCH
    (d:Director)-[:DIRECTED]->(m)

    OPTIONAL MATCH
    (d)-[:DIRECTED]->(dm:Movie)

    OPTIONAL MATCH
    (a:Actor)-[:ACTED_IN]->(m)

    OPTIONAL MATCH
    (a)-[:ACTED_IN]->(am:Movie)

    WITH collect(gm) + collect(dm) + collect(am) AS recs

    UNWIND recs AS rec

    WITH DISTINCT rec

    WHERE
        rec IS NOT NULL
        AND rec.title <> $title
        AND rec.poster IS NOT NULL

    RETURN

        rec.title AS title,
        rec.year AS year,
        rec.rating AS rating,
        rec.poster AS poster,
        rec.trailer AS trailer

    ORDER BY rec.rating DESC

    LIMIT 6

    """

    with driver.session() as session:

        result = session.run(
            query,
            title=title
        )

        movies = []

        for record in result:

            movies.append({

                "title": record["title"],
                "year": record["year"],
                "rating": record["rating"],
                "poster": record["poster"],
                "trailer": record["trailer"]

            })

        return movies

# ==========================
# Actor Page
# ==========================

def get_actor(name):

    query = """

    MATCH (a:Actor {name:$name})
    -[:ACTED_IN]->
    (m:Movie)

    WHERE m.poster IS NOT NULL

    RETURN

        a.name AS name,

        collect({

            title: m.title,
            year: m.year,
            rating: m.rating,
            poster: m.poster,
            trailer: m.trailer

        }) AS movies

    """

    with driver.session() as session:

        record = session.run(
            query,
            name=name
        ).single()

        if not record:
            return None

        return {

            "name": record["name"],
            "movies": record["movies"]

        }


# ==========================
# Director Page
# ==========================

def get_director(name):

    query = """

    MATCH (d:Director {name:$name})
    -[:DIRECTED]->
    (m:Movie)

    WHERE m.poster IS NOT NULL

    RETURN

        d.name AS name,

        collect({

            title: m.title,
            year: m.year,
            rating: m.rating,
            poster: m.poster,
            trailer: m.trailer

        }) AS movies

    """

    with driver.session() as session:

        record = session.run(
            query,
            name=name
        ).single()

        if not record:
            return None

        return {

            "name": record["name"],
            "movies": record["movies"]

        }


# ==========================
# Genre Page
# ==========================

def get_genre(name):

    query = """

    MATCH (g:Genre {name:$name})
    <-[:BELONGS_TO]-
    (m:Movie)

    WHERE m.poster IS NOT NULL

    RETURN

        g.name AS name,

        collect({

            title: m.title,
            year: m.year,
            rating: m.rating,
            poster: m.poster,
            trailer: m.trailer

        }) AS movies

    """

    with driver.session() as session:

        record = session.run(
            query,
            name=name
        ).single()

        if not record:
            return None

        return {

            "name": record["name"],
            "movies": record["movies"]

        }

# ==========================
# Dashboard Statistics
# ==========================

def get_total_movies():

    query = """
    MATCH (m:Movie)
    RETURN count(m) AS total
    """

    with driver.session() as session:

        return session.run(query).single()["total"]


def get_total_actors():

    query = """
    MATCH (a:Actor)
    RETURN count(a) AS total
    """

    with driver.session() as session:

        return session.run(query).single()["total"]


def get_total_directors():

    query = """
    MATCH (d:Director)
    RETURN count(d) AS total
    """

    with driver.session() as session:

        return session.run(query).single()["total"]


def get_total_genres():

    query = """
    MATCH (g:Genre)
    RETURN count(g) AS total
    """

    with driver.session() as session:

        return session.run(query).single()["total"]


# ==========================
# Remove Duplicate Movies
# ==========================

def remove_duplicate_movies():

    query = """

    MATCH (m:Movie)

    WITH
        m.title AS title,
        collect(m) AS movies

    WHERE size(movies) > 1

    FOREACH (

        movie IN tail(movies) |

        DETACH DELETE movie

    )

    """

    with driver.session() as session:

        session.run(query)


# ==========================
# Delete All Data
# ==========================

def delete_all_data():

    query = """

    MATCH (n)

    DETACH DELETE n

    """

    with driver.session() as session:

        session.run(query)

    print("✅ All data deleted successfully!")