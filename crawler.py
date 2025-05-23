import os
import praw
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Reddit credentials
client_id = os.getenv("REDDIT_CLIENT_ID")
client_secret = os.getenv("REDDIT_CLIENT_SECRET")
user_agent = os.getenv("REDDIT_USER_AGENT")

# MySQL credentials
db_host = os.getenv("MYSQL_HOST")
db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_name = os.getenv("MYSQL_DATABASE")

# Connect to Reddit
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Connect to MySQL
conn = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name
)
cursor = conn.cursor()

# Create table (if not exists)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id VARCHAR(10) PRIMARY KEY,
        title TEXT,
        author VARCHAR(255),
        score INT,
        comments INT,
        url TEXT
    )
''')

def fetch_yuki_posts():
    subreddit = reddit.subreddit("all")
    for submission in subreddit.search("Yuki Tsunoda", sort="new", limit=20):
        try:
            cursor.execute('''
                INSERT INTO posts (id, title, author, score, comments, url)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                submission.id,
                submission.title,
                str(submission.author),
                submission.score,
                submission.num_comments,
                submission.url
            ))
            print(f"Saved: {submission.title}")
        except mysql.connector.IntegrityError:
            print(f"Skipped duplicate: {submission.title}")

    conn.commit()

fetch_yuki_posts()
cursor.close()
conn.close()

