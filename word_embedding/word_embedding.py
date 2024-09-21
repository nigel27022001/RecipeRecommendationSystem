from gensim.models import Word2Vec
import pandas as pd
import ast

data = pd.read_csv('data/jamie_oliver_mains_trimmed.csv')
corpus_sorted = []
for lists in data.trimmed_ingredients:
    lists = ast.literal_eval(lists)
    lists.sort()
    corpus_sorted.append(lists)

doc_lengths = [len(doc) for doc in corpus_sorted]
avg_length = float(sum(doc_lengths)/len(doc_lengths))
avg_length = round(avg_length)

model_cbow = Word2Vec(corpus_sorted, sg=0, workers=8, window=avg_length, min_count=1, vector_size=100)
model_cbow.save('models/model_cbow.bin')
