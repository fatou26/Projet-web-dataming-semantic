"""TD1 - From the Unstructured Web to Structured Entities

Phase 1 : Web Crawling and Cleaning
We choose the domain of movies for the project. 
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Iterable

import trafilatura

seed_urls = [
    "https://en.wikipedia.org/wiki/Inception",
    "https://en.wikipedia.org/wiki/The_Godfather",
    "https://en.wikipedia.org/wiki/Parasite_(2019_film)",
    "https://en.wikipedia.org/wiki/Interstellar_(film)",
    "https://en.wikipedia.org/wiki/Spirited_Away",
    "https://en.wikipedia.org/wiki/The_Rip_(film)",
    "https://en.wikipedia.org/wiki/Send_Help",
    "https://en.wikipedia.org/wiki/Goat_(2026_film)",
    "https://en.wikipedia.org/wiki/Fight_Club_(film)",
    "https://en.wikipedia.org/wiki/Parasite_(2019_film)",
    "https://en.wikipedia.org/wiki/The_Matrix",
    "https://en.wikipedia.org/wiki/Gladiator_2",
    "https://en.wikipedia.org/wiki/Seven_(1995_film)",
    "https://en.wikipedia.org/wiki/American_History_X",
    "https://en.wikipedia.org/wiki/The_Pianist_(2002_film)",
    "https://en.wikipedia.org/wiki/Fight_Club",
    "https://www.filmsite.org/starw.html",
    "https://www.filmsite.org/kingk.html",
    "https://www.filmsite.org/hisg.html",
    "https://www.filmsite.org/sear.html",
    "https://www.indiewire.com/criticism/movies/forbidden-fruits-review-1235186119/"
]

def fetch_pages(urls, min_words=500):
    records = []
    for url in urls:
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        
        if content:
            word_count = len(content.split())
            if word_count > min_words:
                print(f"Succès : {url} ({word_count} mots)")
                records.append({
                    "url": url,
                    "text": content,
                    "word_count": word_count
                })
            else:
                print(f"Ignoré : {url} (Trop court : {word_count} mots)")

    with open('data/intermediate/crawler_output.jsonl', 'w', encoding='utf-8') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')


