import nltk
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import ast
import string
import re
import unidecode


vocabulary = nltk.FreqDist()
nltk.download('stopwords')
nltk.download('wordnet')
df = pd.read_csv("data/jamie_oliver_mains.csv")

for ingredients in df['ingredients']:
    if ingredients != np.nan:
        ingredients = ast.literal_eval(ingredients)
        for ingredient in ingredients:
            ingredient = ingredient.split(" ")
            vocabulary.update(ingredient)
most_common_words = []
top_common_words = 230
for word, freq in vocabulary.most_common(top_common_words):
    most_common_words.append(word)
measures = ['teaspoon', 't', 'tsp', 'tsp.', 'tablespoon', 'T', 'tb', 'tbsp']
stop_words = stopwords.words('english')
additional_common_words = ['higher', 'welfare', 'free', 'range', 'sprig', 'leaf']
excused_common_words = ['chicken', 'beef', 'duck','lamb', 'pork', 'fillets','parmesan', 'tomato', 'potatoes', 'lemon', 'carrots']
most_common_words = most_common_words + additional_common_words
for word in excused_common_words:
    if word in most_common_words:
        most_common_words.remove(word)

def ingredient_processing(ingredient_list):
    if not isinstance(ingredient_list, list):
        ingredients = ast.literal_eval(ingredient_list)
    else:
        ingredients = ingredient_list

    translator = str.maketrans("", "", string.punctuation)
    lemmatizer = nltk.WordNetLemmatizer()

    trimmed_ingredients = []
    
    for i in ingredients:
        i.translate(translator)
        items = re.split(' |-', i)
        items = [word for word in items if word.isalpha()]
        items = [word.lower() for word in items]
        items = [unidecode.unidecode(word) for word in items]
        items = [lemmatizer.lemmatize(word) for word in items]
        items = [word for word in items if word not in stop_words]
        items = [word for word in items if word not in measures]
        items = [word for word in items if word not in most_common_words]
        if items:
            for word in items:
                trimmed_ingredients.append(word)
    return trimmed_ingredients

df['trimmed_ingredients'] = df['ingredients'].apply(lambda x : ingredient_processing(x))
df = df.dropna()
df.to_csv("data/jamie_oliver_mains_trimmed.csv", index=False)