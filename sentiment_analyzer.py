import csv
import sys
import requests
import json
from nltk.tokenize import word_tokenize
import os, glob, re, itertools, HTMLParser
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import progressbar

folder_input = 'dataset_part2'
folder_output = 'twitter_output/'

def get_sentiment(text):
    """
    # @param text: blob of text
    # @return list of (sentiment, score) -> ('pos', '0.33')
    """
    blob = TextBlob(text, analyzer=NaiveBayesAnalyzer())
    sentiment = blob.sentiment.classification
    score = '{0:.4f}'.format(blob.sentiment.p_pos - blob.sentiment.p_neg)
    return [sentiment, score]

# def get_sentiment(text):
#     """
#     # @param text: blob of text
#     # @return list of (sentiment, score) -> ('pos', '0.33')
#     """
#     blob = TextBlob(text)
#     score = 0.0
#     for sentence in blob.sentences:
#         score += blob.sentiment.polarity
#     sentiment = 'Positive'
#     if score < 0:
#         sentiment = 'Negative'
#     elif score == 0:
#         sentiment = 'Neutral'
#
#     return [sentiment, score]

def get_storetype(store):
    store_num = int(re.findall("[0-9]+", store)[0])
    if store_num <= 11:
        return "Corporate retailer"
    return "Authorized retailer"

def preprocess_text(tweet):
    tweet = tweet.decode("utf8").encode('ascii', 'ignore')
    text = tweet.lower()
    html_parser = HTMLParser.HTMLParser()
    html_parsed_text = html_parser.unescape(text)
    standardized_text = ''.join(''.join(s)[:2] for _,s in itertools.groupby(html_parsed_text))
    cleaned_text = ' '.join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",standardized_text).split())
    return word_tokenize(cleaned_text)

def find_product(tweet):
    tweet_text = set(preprocess_text(tweet))
    product_dict = {"uverse":"uverse","attfiber":"fiber",
                "fiber":"fiber","directv":"directv",
                "directvservice":"directv"}
    product_set = set(product_dict.keys())

    for word in tweet_text:
        if word in product_set:
            return product_dict[word]
    return "general"

def find_service(tweet):
    tweet_text = set(preprocess_text(tweet))
    service_dict = {"technician":"technician dispatch",
                "installer":"technician dispatch",
                "installation":"product installation",
                "install":"product installation",
                "installed":"product installation",
                "store":"store experience",
                "experience":"store experience",
                "satisfaction":"satisfaction",
                "satisfied":"satisfaction",
                "unsatisfied":"satisfaction",
                }
    service_set = set(service_dict.keys())

    for word in tweet_text:
        if word in service_set:
            return service_dict[word]
    return "general"

def process_file(file_input): # pragma: no cover
    firstline = True
    try:
        f_in = open(file_input, 'rt')
        filepath = f_in.name.split('.')[0]
        file_out = filepath.split("/")[1]
        new_file = folder_output + file_out + '_processed.csv'
        f_out = open(new_file, 'w')
        # print "File being processed %s" % (new_file)
        reader = csv.reader(f_in)
        # Reads file line-by-line
        for row in reader:
            # skip first line
            if firstline:
                firstline = False
                continue
            text = row[6]

            # Add type of store
            store_type = get_storetype(row[0])
            row.insert(1, store_type)

            # Get sentiment for text blob
            sentiment, score = get_sentiment(text)
            row[8] = sentiment
            row.insert(9, score)

            # Find product from text
            product = find_product(text)
            row.insert(10, product)

            # Find service from text
            service = find_service(text)
            row.insert(11, service)

            writer = csv.writer(f_out)
            writer.writerow((row))

    except UnicodeDecodeError as e:
        pass

    finally:
        f_in.close()

def main(): # pragma: no cover
    try:
        bar = progressbar.ProgressBar()
        for filename in bar(glob.glob(os.path.join(folder_input, '*.csv'))):
            if not os.path.isdir(filename):
                process_file(filename)
    except Exception as e:
        print(e)

if __name__ == '__main__': # pragma: no cover
    main()