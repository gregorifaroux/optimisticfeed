import json, os

import feedparser, urllib.request
import requests
from readability import Document
from pathlib import Path

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
from bs4.element import Comment

import time, hashlib

URL = "https://news.google.com/news/rss"
FOLDER = "data"
analyser = SentimentIntensityAnalyzer()


def tag_visible(element):
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return " ".join(t.strip() for t in visible_texts)


def get_sentiment(clean_doc):
    """ Return 1 for positive 0 for neutral and -1 for negative """
    sentiment_dict = analyser.polarity_scores(clean_doc)
    if sentiment_dict["compound"] >= 0.05:
        return 1
    elif sentiment_dict["compound"] <= -0.05:
        return -1
    return 0


def main():
    d = feedparser.parse(URL)
    for entry in d["entries"]:
        try:
            page = urllib.request.urlopen(
                urllib.request.Request(
                    entry.link,
                    data=None,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
                    },
                )
            )
            print("  " + entry.title)
            clean_doc_bs4 = text_from_html(entry.description)
            sentiment = get_sentiment(clean_doc_bs4)
            # Only write positive and neutral
            if sentiment >= 0:
                # Get content
                response = requests.get(entry.link)
                doc = Document(response.text)
                # Generate unique filename
                h = hashlib.new("ripemd160")
                h.update(entry["link"].encode("utf-8"))
                filename = f"{FOLDER}/{h.hexdigest()}.html"
                if Path(filename).exists():
                    continue
                with open(filename, "w") as outfile:
                    outfile.write(doc.summary())

        except urllib.error.HTTPError as e:
            print(e.reason)
        except urllib.error.URLError as e:
            print(e.reason)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(end - start)
