from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import numpy as np

class TfidfEmbeddingVectoriser(object):
    def __init__(self, cbow_model:Word2Vec):
        self.cbow_model = cbow_model
        self.word_to_weight = None
        self.vector_size = cbow_model.wv.vector_size

    def fit(self, docs):
        text_docs = []
        for doc in docs:
            text_docs.append(" ".join(doc))
        tfidf = TfidfVectorizer()
        tfidf.fit(text_docs)
        max_idf_value = max(tfidf.idf_)
        self.word_to_weight = defaultdict(lambda: max_idf_value, 
                                        [(word, tfidf.idf_[i]) for word, i in tfidf.vocabulary_.items()])
        return self
    
    def transform(self, docs):
        doc_word_vector = self.doc_average_list(docs)
        return doc_word_vector
    
    def doc_average(self, doc):
        mean = []
        for word in doc:
            if word in self.cbow_model.wv.index_to_key:
                mean.append(self.cbow_model.wv.get_vector(word) * self.word_to_weight[word])
        if not mean:
            return np.zeros(self.vector_size)
        else:
            mean = np.array(mean).mean(axis=0)
            return mean
        
    def doc_average_list(self, docs):
        return np.vstack([self.doc_average(doc) for doc in docs])
    