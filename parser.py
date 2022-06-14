import requests
from bs4 import BeautifulSoup
from bs4 import Comment

class Parser(object):

    def __init__(self, lang):

        self.url = "https://en.wiktionary.org/wiki/{}?printable=yes"
        self.soup = None
        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries = 2))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries = 2))
        self.lang = lang
        self.word = 'example'
        self.result = ''
    
    def get_data(self):

        response = self.session.get(self.url.format(self.word))
        if response.status_code != 200:
            return False
        self.soup = BeautifulSoup(response.text, 'html.parser')
        
        return True

    def fetch(self):

        # downloading data
        try:
            tmp = self.get_data()
        except:
            return '<h2>No internet connection :(</h2>'
        if not tmp or self.word == '' or self.word == None:
            return '<h2>Word not found :(</h2>'
        span = self.soup.find('span', {'class':'mw-headline', 'id':self.lang.title()})
        if span == None:
            return '<h2>Word not found :(</h2>'
        h2 = span.parent

        # cleaning data
        for tag in ['table', 'sup', 'hr']:
            for i in self.soup.find_all(tag):
                i.extract()
        for i in self.soup.find_all('span', {'class':'mw-editsection'}):
            i.extract()
        for i in self.soup.find_all('a'):
            i.replaceWithChildren()
        for clss in ['thumb tright', 'NavFrame', 'sister-wikipedia', 'list-switcher', 'term-list-header', 'was-wotd']:
            for i in self.soup.find_all('div', {'class':clss}):
                i.extract()
        for i in self.soup.find_all('span', {'class':'mw-headline'}):
            for term in ['Translations', 'Declension', 'Derived_terms', 'Related_terms', 'Coordinate_terms', 'Conjugation', 'See_also']:
                if term in i['id']:
                    i.parent.extract()
        for i in self.soup.find_all('span', {'class':'mw-headline'}):
            if 'Further_reading' in i['id']:
                i.parent.find_next('ul').extract()
                i.parent.extract()

        # combining data
        html = ''
        for tag in h2.next_siblings:
            if tag.name == "h2":
                break
            else:
                if not isinstance(tag, Comment):
                    html += str(tag)
        self.result = html

        return self.result
