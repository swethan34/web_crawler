from flask import Flask, render_template, request
import mysql.connector
import os
from dotenv import load_dotenv
import math

load_dotenv()

app = Flask(__name__)

# DB config
db_config = {
    'host': os.getenv("MYSQL_HOST"),
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': os.getenv("MYSQL_DATABASE")
}
@app.route("/")
def home():
    keyword = request.args.get("q", "")
    sort_by = request.args.get("sort", "score")
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    # ✅ Only allow safe sort fields
    if sort_by not in ['score', 'comments']:
        sort_by = 'score'

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    if keyword:
        count_query = "SELECT COUNT(*) as total FROM posts WHERE title LIKE %s OR author LIKE %s"
        cursor.execute(count_query, (f"%{keyword}%", f"%{keyword}%"))
        total = cursor.fetchone()['total']

        data_query = f"""
            SELECT * FROM posts
            WHERE title LIKE %s OR author LIKE %s
            ORDER BY {sort_by} DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(data_query, (f"%{keyword}%", f"%{keyword}%", per_page, offset))
    else:
        cursor.execute("SELECT COUNT(*) as total FROM posts")
        total = cursor.fetchone()['total']

        data_query = f"SELECT * FROM posts ORDER BY {sort_by} DESC LIMIT %s OFFSET %s"
        cursor.execute(data_query, (per_page, offset))

    posts = cursor.fetchall()
    total_pages = math.ceil(total / per_page)

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        posts=posts,
        keyword=keyword,
        sort_by=sort_by,
        page=page,
        total_pages=total_pages
    )

if __name__ == "__main__":
    app.run(debug=True)
