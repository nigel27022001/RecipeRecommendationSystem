import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import requests
import time
import ast
import random

class Recipe():
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(requests.get(self.url).content, 'html.parser')

    def recipe_name(self):
        try:
            curr_recipe_name_item = self.soup.find("main")
            curr_recipe_name = curr_recipe_name_item.get("data-recipe-title").strip()
            return curr_recipe_name
        except:
            return None

    def ingredients(self):
        try:
            ingredients = []
            ingredient_soup = self.soup.find("div", {"class":"ingredients-rich-text"})
            ingredient_element_list = ingredient_soup.find_all("p", class_="type-body")
            for ingredient in ingredient_element_list:
                ingredients.append(ingredient.getText())
            return ingredients
        except:
            return np.nan
        
    def serving_size(self):
        try:
            serving_soup = self.soup.find_all("h6", class_="type-subtitle-sm line-clamp-2")
            for content in serving_soup:
                if "serves" in content.decode_contents():
                    return content.decode_contents()
            return "serves 0"
        except:
            return None
        
    def cooking_time(self):
        try:
            serving_soup = self.soup.find_all("h6", class_="type-subtitle-sm line-clamp-2")
            for content in serving_soup:
                if "min" in content.decode_contents() or "hr" in content.decode_contents():
                    return content.decode_contents()
            return "-"
        except:
            return None
        
    def difficulty(self):
        try:
            serving_soup = self.soup.find_all("h6", class_="type-subtitle-sm line-clamp-2")
            for content in serving_soup:
                content_string = content.decode_contents()
                if "Not Too Tricky" in content_string:
                    return 3
                elif "Super easy" in content_string:
                    return 1
                elif "Showing Off" in content_string:
                    return 5
            return -1
        except:
            return None
        
    def recipe_url(self):
        try:
            return self.url
        except:
            return None

url = "https://www.jamieoliver.com/recipes/course/desserts"
page_url_format = "/?page="

#Obtaining the number of pages on this website
main_page = requests.get(url)
main_soup = BeautifulSoup(main_page.text, "html.parser")
page_info = main_soup.find('div', class_="pagination-grid")
x_data = page_info.get("x-data")
num_pages_string_prefix = x_data.rfind("numPages")
x_data = x_data[num_pages_string_prefix:]
x_data = x_data.split(",")[0]
x_data = ''.join(filter(str.isdigit, x_data))
num_of_pages = int(x_data)

page_links = []
for page_no in range(num_of_pages):
    page_no = page_no + 1
    page_url = url + page_url_format + str(page_no)
    recipe_menu_page = requests.get(page_url)
    recipe_menu_soup = BeautifulSoup(recipe_menu_page.text, "html.parser")
    recipe_menu_anchors = recipe_menu_soup.findAll("a")
    for anchor in recipe_menu_anchors:
        page_links.append(anchor.get("href"))
    print("page" + str(page_no) + "is done.")
    time.sleep(0.5)
page_link_df = pd.Series(page_links)
recipe_urls_df = page_link_df[(page_link_df.str.contains("/recipes") == True) 
                              & (page_link_df.str.count("/") > 3)
                              & (page_link_df.str.contains("special-diets") == False)
                              & (page_link_df.str.contains("dishtype") == False)
                              & (page_link_df.str.contains("course") == False)
                              & (page_link_df.str.contains("book") == False)
                              & (page_link_df.str.contains("favourites") == False)].unique()
recipe_urls_df = "https://www.jamieoliver.com" + recipe_urls_df

recipe_attribs = ['recipe_name', 'serving_size', 'cooking_time', 'difficulty', 'ingredients', 'recipe_url']
output_df = pd.DataFrame(columns=recipe_attribs)
for curr_index in range(len(recipe_urls_df)):
    curr_url = recipe_urls_df[curr_index]
    curr_recipe = Recipe(curr_url)
    output_df.loc[curr_index] = [getattr(curr_recipe, recipe_attrib)() for recipe_attrib in recipe_attribs]
    time.sleep(random.uniform(0.15, 0.20))
output_df.to_csv('data/jamie_oliver_mains.csv')