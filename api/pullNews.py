import json, os

import feedparser, urllib.request
import requests
from readability import Document

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from bs4 import BeautifulSoup
from bs4.element import Comment

URL = "https://news.google.com/news/rss"
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
    return u" ".join(t.strip() for t in visible_texts)


def write_sentiment(text_file, clean_doc):
    sentiment_dict = analyser.polarity_scores(clean_doc)
    analysis = TextBlob(clean_doc)
    if sentiment_dict["compound"] >= 0.05:
        text_file.write("Positive")
        print("Positive")
    elif sentiment_dict["compound"] <= -0.05:
        text_file.write("Negative")
        print("Negative")
    else:
        text_file.write("Neutral")
        print("Neutral")
    print(analysis.sentiment)
    text_file.write("\n")
    if analysis.sentiment[0] > 0:
        text_file.write("Positive sentiment")
    elif analysis.sentiment[0] < 0:
        text_file.write("Negative sentiment")
    else:
        text_file.write("Neutral sentiment")
    text_file.write("\n")


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
            response = requests.get(entry.link)
            doc = Document(response.text)
            print("title " + doc.title())
            with open("sentiment.txt", "a+") as text_file:
                clean_doc = doc.summary()
                clean_doc_bs4 = text_from_html(page)
                text_file.write("\n ----------------------------")
                text_file.write(doc.title())
                text_file.write("\n Readability:")
                write_sentiment(text_file, clean_doc)
                text_file.write("\n BS4:")
                write_sentiment(text_file, clean_doc_bs4)
                text_file.write("\n ----------------------------")
        except urllib.error.HTTPError as e:
            print(e.reason)
        except urllib.error.URLError as e:
            print(e.reason)


if __name__ == "__main__":
    main()
