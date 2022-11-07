import requests
from bs4 import BeautifulSoup
import re
from bs4.element import Comment
import os


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        return False
    return True


if __name__ == '__main__':
    # url = 'http://www.cs.uic.edu/Sistla/'
    # HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    # res = requests.get(url, timeout=(3, 60), verify=False, headers=HEADERS)
    # print(res.url)
    # print(res.status_code)
    # print(res.text)
    #
    # soup = BeautifulSoup(res.text, 'html.parser')
    # links = soup.find_all('a', href=True)
    # web_page_paragraph_contents = soup.find_all(text=True)
    # web_page_paragraph_contents = filter(tag_visible, web_page_paragraph_contents)
    # text = " ".join(term.strip() for term in web_page_paragraph_contents)
    # text = text.lower()
    #
    # text = re.sub("[^a-z]+", " ", text)

    list1 = []
    for filename in os.listdir('/Users/rishabhgoel/Documents/Fall22/IR/Web-Search-Engine/uic-docs-text'):
        list1.append(int(filename[:-4]))

    list2 = []
    with open("mapping.txt") as f:
        content = f.readlines()

    for line in content:
        line = line.strip()
        num = line.split()[0]
        list2.append(int(num))

    print(sorted(list(set(list2).difference(list1))))
    print(sorted(list(set(list1).difference(list2))))
