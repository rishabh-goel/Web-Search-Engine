import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Set of stopwords from english
from WebScraper import stemmer

stopwords = set(stopwords.words('english'))


# Method to tokenize the Cranfield documents
def tokenize_documents(current_path):
    folder = current_path + "/uic-docs-text"
    os.chdir(folder)

    document_corpus = {}

    for filename in os.listdir(folder):
        file = folder + '/' + filename
        f = open(file, 'r')
        content = f.read()
        file_number = int(filename[:-4])
        word_list = []

        # Ignoring words that are either numbers and or have length <= 2
        # Extracting only Title and Text info
        for word in content.split():
            if len(word) > 2:
                word_list.append(word)

        document_corpus[file_number] = stemmer(word_list)

    return document_corpus


# Method to tokenize the queries
def tokenize_queries(current_path):
    global queries
    os.chdir(current_path)
    with open("queries.txt") as f:
        queries = {}
        content = f.readlines()
        index = 1

        # Ignoring words that are either numbers or have length <= 2
        for line in content:
            word_list = []
            for word in line.split():
                if word.isdigit():
                    continue

                if len(word) > 2:
                    word_list.append(word.lower())
            queries[index] = stemmer(word_list)
            index += 1

    return queries


# Method to calculate the document frequency of words
def df_calc(documents):
    df = {}
    for key, value in documents.items():
        for word in value:
            if word in df:
                df[word].add(key)
            else:
                df[word] = {key}

    for i in df:
        df[i] = len(df[i])

    return df


# Method to calculate the tf_idf of both documents and queries
def calculate_tf_idf(item, vocab, DF, N):
    tf_idf = {}

    for i in range(1, len(item) + 1):
        tokens = item[i]
        word_count = len(tokens)
        counter = Counter(tokens)

        for token in tokens:
            tf = counter[token] / word_count
            if token in vocab:
                df = DF[token]
            else:
                df = 0

            idf = np.log2((N + 1) / (df + 1))

            tf_idf[(i, token)] = tf * idf

    return tf_idf


# Method to convert documents to document vector
def document_to_vector(documents, vocab, tf_idf):
    doc_vector = np.zeros((len(documents), len(vocab)))

    for item in tf_idf.items():
        idx = vocab.index(item[0][1])
        doc_vector[item[0][0] - 1][idx] = tf_idf[item[0]]

    return doc_vector


# Method to convert queries to query vector
def query_to_vector(queries, vocab, tf_idf):
    query_vector = np.zeros((len(queries), len(vocab)))

    for item in tf_idf.items():
        if item[0][1] in vocab:
            idx = vocab.index(item[0][1])
            query_vector[item[0][0] - 1][idx] = tf_idf[item[0]]

    return query_vector


# Method to calculate cosine similarity
def cosine_similarity(doc_vector, query_vector):
    cos_sim = defaultdict(list)
    for i in range(len(query_vector)):
        for j in range(len(doc_vector)):
            cos_sim[i + 1].append((j + 1, np.dot(query_vector[i], doc_vector[j]) /
                                   (np.linalg.norm(query_vector[i]) * np.linalg.norm(doc_vector[j]))))

    # Sorting the cosine similarity in descending order
    for i in range(1, len(cos_sim) + 1):
        cos_sim[i] = sorted(cos_sim[i], key=lambda x: x[1], reverse=True)

    return cos_sim


# Method to parse relevance.txt
def parse_mapping_doc(path):
    os.chdir(path)
    with open("mapping.txt") as f:
        text = f.readlines()
        mapping = {}
        for line in text:
            index, url = line.split()
            mapping[int(index)] = url

    return mapping


if __name__ == '__main__':
    # Fetch path from command line
    path = sys.argv[1]

    # Tokenize documents and queries
    documents = tokenize_documents(path)
    queries = tokenize_queries(path)

    # Calculate document frequency and vocabulary
    DF = df_calc(documents)
    vocab = [x for x in DF]

    # Calculate tf_idf and create vectors for both documents and queries
    document_tf_idf = calculate_tf_idf(documents, vocab, DF, len(documents))
    document_vector = document_to_vector(documents, vocab, document_tf_idf)

    query_tf_idf = calculate_tf_idf(queries, vocab, DF, len(documents))
    query_vector = query_to_vector(queries, vocab, query_tf_idf)

    # Calculate cosine similarity using the vectors
    query_cosine_similarity = cosine_similarity(document_vector, query_vector)

    mapping_doc = parse_mapping_doc(path)

    # Part 1 - Display query and document id in order of decreasing cosine similarity
    for query_id, cosine_list in query_cosine_similarity.items():
        for doc_id, cosine in cosine_list[:10]:
            print(f"{query_id}, {mapping_doc[doc_id]}")



