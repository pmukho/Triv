import requests
import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict
import os
import json

DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": "postgres-db",
    "port": "5432"
}

psid_to_category = {
    "23645371": "People",
    "32149945": "History",
    "32149981": "Technology",
}

def fetch_petscan_data(psid: str):
    base_url = "https://petscan.wmcloud.org/psapi.php"
    params = {
        "psid": psid,
        "format": "json",
        "output_compatibility": "quick-intersection"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Enhanced debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response type: {type(data)}")
        print(f"Top level structure: {list(data.keys()) if isinstance(data, dict) else 'List of length ' + str(len(data))}")
        print("First level data sample:", json.dumps(data, indent=2)[:1000]) 
        
        articles = []
        
        # Handle the specific nested structure we've observed
        if isinstance(data, dict) and '*' in data and isinstance(data['*'], list):
            for outer_item in data['*']:
                if isinstance(outer_item, dict) and 'a' in outer_item:
                    a_data = outer_item['a']
                    if isinstance(a_data, dict) and '*' in a_data and isinstance(a_data['*'], list):
                        for article in a_data['*']:
                            if isinstance(article, dict) and 'title' in article:
                                articles.append({
                                    'title': article['title'].replace('_', ' '),
                                    'category': psid_to_category.get(psid, 'Unknown')
                                })
        
        print(f"Processed {len(articles)} articles")
        if articles:
            print("Sample articles:", articles[:3])
        else:
            print("No articles were extracted from the response")
            
        return articles
            
    except requests.RequestException as e:
        print(f"Error fetching data for psid {psid}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(f"Full error details: {type(e).__name__}")
        return []

def connect_to_db() -> psycopg2.extensions.connection:
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")

def insert_articles(conn: psycopg2.extensions.connection, articles: List[Dict]):
    with conn.cursor() as cur:
        query = """
            INSERT INTO wikipedia_articles (title, category)
            VALUES (%s, %s)
            ON CONFLICT (title) DO UPDATE 
            SET category = EXCLUDED.category
        """
        
        article_data = [(
            article['title'],
            article['category']
        ) for article in articles]
        
        execute_batch(cur, query, article_data)
    conn.commit()

def main():
    psid = "23645371"  # Replace with your PSID
    try:
        print("Fetching data from PetScan...")
        articles = fetch_petscan_data(psid)
        print(f"Found {len(articles)} articles")
        
        if not articles:
            print("No articles found. Exiting.")
            return
        
        print("\nSample of first 3 articles:")
        for article in articles[:3]:
            print(f"Title: {article['title']}, Category: {article['category']}")
        
        print("\nConnecting to database...")
        conn = connect_to_db()
        
        print("Inserting articles...")
        insert_articles(conn, articles)
        print("Successfully inserted articles into database")
        
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM wikipedia_articles")
            count = cur.fetchone()[0]
            print(f"\nTotal articles in database: {count}")
            
            cur.execute("SELECT title, category FROM wikipedia_articles LIMIT 3")
            print("\nSample entries in database:")
            for row in cur.fetchall():
                print(f"Title: {row[0]}, Category: {row[1]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()