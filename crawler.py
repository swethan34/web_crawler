import os
import praw
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Reddit API credentials
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# MySQL connection
conn = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)
cursor = conn.cursor()

# Create table if needed
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id VARCHAR(20) PRIMARY KEY,
        title TEXT,
        author VARCHAR(255),
        score INT,
        comments INT,
        url TEXT
    )
''')
conn.commit()

def fetch_f1_posts(min_score=30, target_new=50):
    subreddit = reddit.subreddit("all")
    added = 0

    for submission in subreddit.search("F1", sort="new", limit=200):
        if submission.score < min_score:
            continue

        post_url = f"https://www.reddit.com{submission.permalink}"

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
                post_url
            ))
            added += 1
            print(f"[+] {submission.title}")
        except mysql.connector.IntegrityError:
            continue

        if added >= target_new:
            break

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    fetch_f1_posts()
