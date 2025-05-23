from flask import Flask, render_template, request
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL config
db_config = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    keyword = request.args.get("q", "")
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    
    if keyword:
        query = "SELECT * FROM posts WHERE title LIKE %s OR author LIKE %s ORDER BY score DESC"
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("SELECT * FROM posts ORDER BY score DESC LIMIT 20")
    
    posts = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("index.html", posts=posts, keyword=keyword)

if __name__ == "__main__":
    app.run(debug=True)
