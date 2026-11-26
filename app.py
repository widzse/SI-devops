import os
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)
# Change both constants in Lab 3, then build a DIFFERENT image.
CODE_VERSION = "v1"
GREETING = "Hello from the original Flask release"

@app.get("/")
def index():
    return jsonify(greeting=GREETING, version=CODE_VERSION)

@app.get("/version")
def version():
    return jsonify(version=CODE_VERSION)

@app.get("/health")
def health():
    if os.getenv("FAIL_HEALTH", "false").lower() == "true":
        return jsonify(status="not ready"), 503
    return jsonify(status="ok")

@app.get("/db-time")
def db_time():
    try:
        with pymysql.connect(host=os.getenv("DB_HOST", "db"),
                             user=os.getenv("DB_USER", "flask"),
                             password=os.environ["DB_PASSWORD"],
                             database=os.getenv("DB_NAME", "flask"),
                             connect_timeout=3, read_timeout=3, write_timeout=3) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT NOW()")
                value = cursor.fetchone()[0]
        return jsonify(database_time=str(value), version=CODE_VERSION)
    except (pymysql.MySQLError, KeyError):
        app.logger.warning("Database request failed; inspect dependency configuration")
        return jsonify(error="database unavailable"), 503
