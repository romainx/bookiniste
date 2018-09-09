#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
import bottlenose
import fire
from bs4 import BeautifulSoup
from colorama import init 
from termcolor import colored 
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Util:

    @staticmethod
    def extract_text(bs4_element):
        value = None
        if bs4_element:
            value = bs4_element.text
        return value

class Price():
    
    def __init__(self, target, lowest_new_price, lowest_used_price):
        self.target = target
        self.new = Price._convert(lowest_new_price)
        self.used = Price._convert(lowest_used_price)
    
    @staticmethod
    def _convert(price):
        converted = None
        if price:
            converted = int(price) / 100
        return converted
    
    @staticmethod
    def _format_number(price, color, symbol='€', sign=''):
        price = '{price:{sign:}.1f}'.format(price = price, 
                                            sign = sign)
        return colored('{:<6}'.format(str(price) + symbol), color)

    def __repr__(self):
        # Le Traquet kurde, Jean Rolin.
        deal = self.deal()
        return '{target: <5}-> {min: <6}/ {new: <6} ({diff: <6})'.format(
            min = Price._format_number(self.min, deal),
            new = Price._format_number(self.new, 'white'),
            target = Price._format_number(self.target, 'cyan'),
            diff = Price._format_number(price = self.diff, color = deal, sign = '+')
            )
    @property
    def min(self):
        m = None
        if self.new is None:
            m = self.used
        if self.used is None:
            m = self.new
        if self.new and self.used:
            m = min(self.new, self.used)
        return m

    @property
    def diff(self):
        return self.min - self.target
    
    @property
    def percentage(self):
        return self.diff / self.target * 100
        
    def deal(self):
        deal = 'red'
        if self.diff <= 3:
            deal = 'green'
        elif self.diff <= 5:
            deal = 'yellow'
        return deal
    

class Book():
    """A book as I manage it"""

    TITLE_MAX_LEN = 25

    def __init__(self, title, author, price):
        self.title = title
        self.author = author
        self.price = price

    def __repr__(self):
        # Le Traquet kurde, Jean Rolin.
        return '{title:<27}: {price}'.format(
            title = (self.title[:Book.TITLE_MAX_LEN] + '..') if len(self.title) > Book.TITLE_MAX_LEN else self.title,
            price = self.price)


class Bookiniste():
    
    def __init__(self):
        # AWS params
        self.aws = None
        # The whislist to load and check for deals
        self.whislist = None
        # The list of books
        self.books = []
        # Params used to perform the call to the AWS libs
        self.params = {
            'ItemId': None,
            'IdType': 'ISBN',
            'ResponseGroup': 'ItemAttributes,OfferSummary',
            'SearchIndex': 'Books'
            }
        self.aws, self.whislist = self._load_data()


    def _load_data(self):
        # Parse JSON into an object with attributes corresponding to dict keys.
        path = os.path.join(os.path.expanduser('~'),'Dropbox/bookiniste.json')
        with open(path) as f:
            data = json.load(f)
        self.aws = data['aws']
        self.whislist = data['whislist']
        return self.aws, self.whislist

    def check_deals(self):
        for item in tqdm(self.whislist, unit='req.'):
            self.params['ItemId'] = item['ISBN'].replace('-', '')
            amazon = bottlenose.Amazon(self.aws['AWS_ACCESS_KEY_ID'], 
                                       self.aws['AWS_SECRET_ACCESS_KEY'], 
                                       self.aws['AWS_ASSOCIATE_TAG'], 
                                       Region='FR', MaxQPS=0.9, Parser=lambda text: BeautifulSoup(text, 'xml'))
            # Running the query
            r = amazon.ItemLookup(**self.params)
            # Retrieving prices
            lowest_new_price = None
            lowest_used_price = None
            try:
                 lowest_new_price = Util.extract_text(r.ItemLookupResponse.Items.Item.OfferSummary.LowestNewPrice.Amount)
                 lowest_used_price = Util.extract_text(r.ItemLookupResponse.Items.Item.OfferSummary.LowestUsedPrice.Amount)
            except:
                logger.warn('Cannnot retrieve price for {}'.format(self.params['ItemId']))
            
            price = Price(target = item['target'],
                      lowest_new_price = lowest_new_price,
                      lowest_used_price = lowest_used_price)
            book = Book(title = Util.extract_text(r.ItemLookupResponse.Items.Item.ItemAttributes.Title),
                     author = Util.extract_text(r.ItemLookupResponse.Items.Item.ItemAttributes.Author),
                     price = price
                    )
            # <ItemAttributes>.Binding
            #tqdm.write('{} done'.format(book.title))
            self.books.append(book)
        return self.books

    def deals(self):
        self.books = self.check_deals()
        for book in sorted(self.books, key=lambda book: book.price.diff):
            print('- {book}'.format(book = book))

if __name__ == '__main__':
      fire.Fire(Bookiniste)
