import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk import PorterStemmer
from nltk.corpus import stopwords
from urllib3.exceptions import InsecureRequestWarning

stopwords = set(stopwords.words('english'))
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

'''
The scraper also extracts the visible text from each of these pages, which are persisted in a directory uic-docs-text
Also Parses the Html and returns all the available links in the page .
'''

docs_directory = "uic-docs-text/"


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, features='html.parser')
    web_page_paragraph_contents = soup.find_all(text=True)
    web_page_paragraph_contents = filter(tag_visible, web_page_paragraph_contents)
    text = ''
    for para in web_page_paragraph_contents:
        if not ('https:' in str(para.text)):
            text = text + str(para.text).strip() + "\n"

    word_list = []

    for word in text.split():
        if len(word) > 2:
            word_list.append(word)

    stemmed_list = stemmer(word_list)
    return " ".join(stemmed_list)


def scrape_links(html):
    soup = BeautifulSoup(html, features='html.parser')
    links = soup.find_all('a', href=True)
    return links


def scrape_info(html, filecounter):
    doc_text = text_from_html(html)
    create_document(doc_text, docs_directory + str(filecounter) + ".txt")
    return doc_text


def create_document(text, filename):
    with open(filename, 'w') as f:
        f.write(text)


def scrape_page(url, index):
    try:
        res = requests.get(url, timeout=(3, 60), verify=False, headers=HEADERS)
        return res.text, res.url, index, res.status_code
    except requests.RequestException:
        return


def stemmer(word_list):
    porter_stemmer = PorterStemmer()
    stemmed_word_list = []

    for word in word_list:
        if word not in stopwords:
            stemmed_word = porter_stemmer.stem(word)
            stemmed_word = re.sub('[^A-Za-z</>]+', '', stemmed_word)
            if stemmed_word not in stopwords and stemmed_word not in stemmed_word_list:
                stemmed_word_list.append(stemmed_word)
    return stemmed_word_list
