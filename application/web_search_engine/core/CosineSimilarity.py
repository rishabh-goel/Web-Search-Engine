import pathlib
import pickle
import re
from collections import Counter, defaultdict

import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from scipy.special import logsumexp

# import time


stopwords = set(stopwords.words('english'))
pickle_folder = pathlib.Path(__file__).parent / 'static' / 'core' / "pickle"


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


def tokenize_documents(current_path):
    children = current_path.glob("**/*")
    file_paths = [file for file in children if file.is_file()]
    document_corpus = {}

    for filename in file_paths:        
        f = open(filename, 'r')
        content = f.read()
        file_number = int(filename.stem)
        document_corpus[file_number] = content.split()

    with open(pickle_folder / 'tokenized_documents.pickle', 'wb') as f:
        pickle.dump(document_corpus, f)

    return document_corpus


def tokenize_queries(query):
    queries = {}
    index = 1
    word_list = []
    for word in query.split():
        if word.isdigit():
            continue

        if len(word) > 2:
            word_list.append(word.lower())

    queries[index] = stemmer(word_list)
    return queries


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

    with open(pickle_folder / 'document_frequency.pickle', 'wb') as f:
        pickle.dump(df, f)

    return df


def calculate_tf_idf(item, vocab, DF, N, item_type):
    tf_idf = {}

    for key, value in item.items():
        tokens = value
        word_count = len(tokens)
        counter = Counter(tokens)

        for token in tokens:
            tf = counter[token] / word_count
            if token in vocab:
                df = DF[token]
            else:
                df = 0

            idf = np.log2((N + 1) / (df + 1))

            tf_idf[(key, token)] = tf * idf

    if item_type == 'documents':
        with open(pickle_folder / 'document_tf_idf.pickle', 'wb') as f:
            pickle.dump(tf_idf, f)

    return tf_idf


def document_to_vector(documents, vocab, tf_idf):
    x = max(documents, key=int)
    y = len(vocab)
    doc_vector = np.zeros((x, y))

    for item in tf_idf.items():
        idx = vocab.index(item[0][1])
        doc_vector[item[0][0] - 1][idx] = tf_idf[item[0]]

    with open(pickle_folder / 'document_vector.pickle', 'wb') as f:
        pickle.dump(doc_vector, f)

    return doc_vector


def query_to_vector(queries, vocab, tf_idf):
    query_vector = np.zeros((len(queries), len(vocab)))

    for item in tf_idf.items():
        if item[0][1] in vocab:
            idx = vocab.index(item[0][1])
            query_vector[item[0][0] - 1][idx] = tf_idf[item[0]]

    return query_vector


def cosine_similarity(doc_vector, query_vector):
    cos_sim = defaultdict(list)
    for i in range(len(query_vector)):
        for j in range(len(doc_vector)):
            cos_sim[i + 1].append((j + 1, logsumexp(np.dot(query_vector[i], doc_vector[j])) /
                                   logsumexp(np.linalg.norm(query_vector[i]) * np.linalg.norm(doc_vector[j]))))

    for i in range(1, len(cos_sim) + 1):
        cos_sim[i] = sorted(cos_sim[i], key=lambda x: x[1], reverse=True)

    with open(pickle_folder / 'cosine_similarity.pickle', 'wb') as f:
        pickle.dump(cos_sim, f)

    return cos_sim


def parse_mapping_doc(path):
    # with open("/Users/rishabhgoel/Documents/Fall22/IR/Web-Search-Engine/application/web_search_engine/core/static/core/mapping/mapping.txt") as f:
    with open(path) as f:
        text = f.readlines()
        mapping = {}
        for line in text:
            index, url = line.split()
            mapping[int(index)] = url

    return mapping


def main(query):
    # tic = time.perf_counter()
    path = pathlib.Path(__file__).parent / 'static' / 'core' / "uic-docs-text"
    mapping_file_path = pathlib.Path(__file__).parent / 'static' / 'core' / "mapping" / "mapping.txt"

    # documents = tokenize_documents(path)
    with open(pickle_folder / 'tokenized_documents.pickle', 'rb') as f:
        documents = pickle.load(f)
    # DF = df_calc(documents)
    with open(pickle_folder / 'document_frequency.pickle', 'rb') as f:
        DF = pickle.load(f)
    vocab = [x for x in DF]

    # document_tf_idf = calculate_tf_idf(documents, vocab, DF, len(documents), "documents")
    with open(pickle_folder / 'document_tf_idf.pickle', 'rb') as f:
        document_tf_idf = pickle.load(f)

    # document_vector = document_to_vector(documents, vocab, document_tf_idf)    
    with open(pickle_folder / 'document_vector.pickle', 'rb') as f:
        document_vector = pickle.load(f)
    queries = tokenize_queries(query)
    query_tf_idf = calculate_tf_idf(queries, vocab, DF, len(documents), "queries")
    query_vector = query_to_vector(queries, vocab, query_tf_idf)

    query_cosine_similarity = cosine_similarity(document_vector, query_vector)
    mapping_doc = parse_mapping_doc(mapping_file_path)
    result = []
    for doc_id, cosine in query_cosine_similarity[1][:10]:
        result.append(mapping_doc[doc_id])
    # toc = time.perf_counter()
    # print(f"Time =  {toc - tic:0.4f} seconds")
    return result


if __name__ == '__main__':
    main("test string")


