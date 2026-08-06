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
# Create Driver
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
        session.run(query, parameters or {}).consume()

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

    RETURN
        m.title AS title,
        m.year AS year,
        m.rating AS rating,
        m.poster AS poster

    ORDER BY {order}
    """

    with driver.session() as session:

        result = session.run(query)

        return [dict(record) for record in result]
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
        any(genre IN genres
            WHERE toLower(genre) CONTAINS toLower($keyword))

    RETURN

        m.title AS title,
        m.year AS year,
        m.rating AS rating,
        m.poster AS poster

    ORDER BY m.title
    """

    with driver.session() as session:

        result = session.run(
            query,
            keyword=keyword
        )

        return [dict(record) for record in result]


# ==========================
# Movie Details
# ==========================

def get_movie(title):

    query = """

    MATCH (m:Movie {title:$title})

    OPTIONAL MATCH (d:Director)-[:DIRECTED]->(m)

    OPTIONAL MATCH (a:Actor)-[:ACTED_IN]->(m)

    OPTIONAL MATCH (m)-[:BELONGS_TO]->(g:Genre)

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

        if record:
            return dict(record)

        return None
# ==========================
# Recommendations
# ==========================

def get_recommendations(title):

    query = """

    MATCH (m:Movie {title:$title})

    OPTIONAL MATCH (m)-[:BELONGS_TO]->(g:Genre)<-[:BELONGS_TO]-(rec:Movie)

    WHERE rec.title <> $title

    RETURN DISTINCT

        rec.title AS title,
        rec.year AS year,
        rec.rating AS rating,
        rec.poster AS poster

    ORDER BY rec.rating DESC

    LIMIT 6

    """

    with driver.session() as session:

        result = session.run(
            query,
            title=title
        )

        return [dict(record) for record in result]


# ==========================
# Actor Page
# ==========================

def get_actor(name):

    query = """

    MATCH (a:Actor {name:$name})-[:ACTED_IN]->(m:Movie)

    RETURN

        a.name AS actor,

        collect({

            title:m.title,
            year:m.year,
            rating:m.rating,
            poster:m.poster

        }) AS movies

    """

    with driver.session() as session:

        record = session.run(
            query,
            name=name
        ).single()

        if record:
            return dict(record)

        return None


# ==========================
# Director Page
# ==========================

def get_director(name):

    query = """

    MATCH (d:Director {name:$name})-[:DIRECTED]->(m:Movie)

    RETURN

        d.name AS director,

        collect({

            title:m.title,
            year:m.year,
            rating:m.rating,
            poster:m.poster

        }) AS movies

    """

    with driver.session() as session:

        record = session.run(
            query,
            name=name
        ).single()

        if record:
            return dict(record)

        return None


# ==========================
# Genre Page
# ==========================

def get_genre(name):

    query = """

    MATCH (g:Genre {name:$name})<-[:BELONGS_TO]-(m:Movie)

    RETURN

        g.name AS genre,

        collect({

            title:m.title,
            year:m.year,
            rating:m.rating,
            poster:m.poster

        }) AS movies

    """

    with driver.session() as session:

        record = session.run(
            query,
            name=name
        ).single()

        if record:
            return dict(record)

        return None

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
# Delete All Data
# ==========================

def delete_all_data():

    query = """
    MATCH (n)
    DETACH DELETE n
    """

    with driver.session() as session:

        session.run(query).consume()

    print("✅ Database Cleared")


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

        session.run(query).consume()

    print("✅ Duplicate Movies Removed")