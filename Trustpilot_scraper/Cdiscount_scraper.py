
import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd
import csv
import os


def get_reviews_from_page(url):
    try:
        req = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        req.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(req.text, 'html.parser')
        reviews_raw = soup.find("script", id="__NEXT_DATA__").string
        reviews_raw = json.loads(reviews_raw)
        return reviews_raw["props"]["pageProps"]["reviews"]
    except (requests.RequestException, json.JSONDecodeError, AttributeError) as e:
        return []

def scrape_trustpilot_reviews(base_url: str, cutoff_date: str):
    reviews_data = []
    page_number = 1

    while True:
        url = f"{base_url}&page={page_number}"
        reviews = get_reviews_from_page(url)

        if not reviews:
            break

        for review in reviews:
            review_date = pd.to_datetime(review["dates"]["publishedDate"]).strftime("%Y-%m-%d")

            # Stop if the review date is earlier than the cutoff date
            if review_date < cutoff_date:
                return reviews_data

            data = {
                'Date': review_date,
                'Author': review["consumer"]["displayName"],
                'Body': review["text"],
                'Heading': review["title"],
                'Rating': review["rating"],
                'Location': review["consumer"]["countryCode"]
            }
            reviews_data.append(data)

        page_number += 1
    
    return reviews_data



base_url = 'https://fr.trustpilot.com/review/www.cdiscount.com?sort=recency'
reviews_data = scrape_trustpilot_reviews(base_url, '2024-02-13')

output_file = "C:\\Users\\elect\\Desktop\\Cdiscount_reviews_project\\Data\\raw_data.csv"
output_dir = os.path.dirname(output_file)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

if reviews_data:
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=reviews_data[0].keys())
        
  
        writer.writeheader()
        
   
        writer.writerows(reviews_data)


