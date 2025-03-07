import requests
import json
import csv
import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict
import os
import random

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
    "32503216": "Geography",
    "32499086": "Everyday Life",
    "32503318": "Philosophy/Religion",
    "32503419": "Arts",
    "32503569": "Society/Social Sciences",
    "32503733": "Biology/Health Sciences",
    "32503805": "Physical Sciences",
    "32504022": "Mathematics"
}

# Fetch data from wikipedia API by psid
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

        articles = []
        
        # Extract title and category from response
        if isinstance(data, dict) and '*' in data and isinstance(data['*'], list):
            for outer_item in data['*']:
                if isinstance(outer_item, dict) and 'a' in outer_item:
                    a_data = outer_item['a']
                    if isinstance(a_data, dict) and '*' in a_data and isinstance(a_data['*'], list):
                        for article in a_data['*']:
                            if isinstance(article, dict) and 'title' in article:
                                articles.append({
                                    # 'title': article['title'].replace('_', ' '),
                                    'title': article['title'],
                                    'category': psid_to_category.get(psid, 'Unknown')
                                })
            
        random.shuffle(articles)
        return articles
            
    except requests.RequestException as e:
        print(f"Error fetching data for psid {psid}: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return []

def main():
    output_dir = "./db/data"
    os.makedirs(output_dir, exist_ok=True)
    
    all_articles = []
    
    for psid, category in psid_to_category.items():
        print(f"Fetching data for category: {category} (PSID: {psid})...")
        articles = fetch_petscan_data(psid)
        all_articles.extend(articles)
    
    # Write to CSV
    csv_path = os.path.join(output_dir, "wiki_articles.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['title', 'category'])
        writer.writeheader()
        writer.writerows(all_articles)
    
    # Write to JSON
    json_path = os.path.join(output_dir, "wiki_articles.json")
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(all_articles, jsonfile)
        
    print(f"Exported {len(all_articles)} articles to {csv_path} and {json_path}")

if __name__ == "__main__":
    main()