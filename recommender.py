from gensim.models import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import pandas as pd
import ast

from word_embedding.document_embedding import TfidfEmbeddingVectoriser
from feature_extraction.feature_extractor import ingredient_processing

def get_recommendations(number_of_recos, scores):
    df_recipes = pd.read_csv("data/jamie_oliver_mains_trimmed.csv")
    top = sorted(range((len(scores))), key=lambda i: scores[i], reverse=True)[:number_of_recos]
    recommendations = pd.DataFrame(columns=["recipe", "ingredients", "score", "url"])
    count = 0
    for i in top:
        recommendations.at[count, "recipe"] = df_recipes["recipe_name"][i]
        recommendations.at[count, "ingredients"] = df_recipes["ingredients"][i]
        recommendations.at[count, "url"] = df_recipes["recipe_url"][i]
        recommendations.at[count, "score"] = str(scores[i])
        count += 1
    return recommendations

def calculate_recommendations(ingredients, n=5):
    model = Word2Vec.load("models/model_cbow.bin")
    model.init_sims(replace=True)
    if model:
        print("model initialised")
    data = pd.read_csv("data/jamie_oliver_mains_trimmed.csv")
    corpus_sorted = []
    for lists in data.trimmed_ingredients:
        lists = ast.literal_eval(lists)
        lists.sort()
        corpus_sorted.append(lists)
    
    tfidf_vec_tr = TfidfEmbeddingVectoriser(model)
    tfidf_vec_tr.fit(corpus_sorted)
    doc_vec = tfidf_vec_tr.transform(corpus_sorted)
    doc_vec = [doc.reshape(1, -1) for doc in doc_vec]
    

    user_input = ingredients
    user_input = user_input.split(",")
    user_input = ingredient_processing(user_input)
    input_embedding = tfidf_vec_tr.transform([user_input])[0].reshape(1,-1)

    cos_sim = map(lambda x: cosine_similarity(input_embedding, x)[0][0], doc_vec)
    scores = list(cos_sim)
    recommendation = get_recommendations(n, scores)
    return recommendation

if __name__ == "__main__":
    user_input = "tofu, mirin, mango, pineapple, chutney"
    rec = calculate_recommendations(user_input)
    print(rec)