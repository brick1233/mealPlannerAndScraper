# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import re
import os
import shutil
from datetime import datetime as date
import unicodedata

# function to find the domain of a url


# function to find the domain of a url
def parseDomain(url):
    # match for "www.MATCH.com"
    findDomain = re.search(r"\.[A-Za-z0-9]+\.", url)

    # Access the matched text using group(), else report bad url
    if findDomain:
        return (findDomain.group()[1:-1])
    else:
        return ("bad_url")


# function to parse the ingredients and recipe contained
# by a website. htmlKey is a dictionary containing the relevant html tags etc.
def parseRecipeSite(url, htmlKey):
    # send request and read html if good request
    page = requests.get(url)  # read page
    if page.status_code == 200:
        # get the soup
        soup = BeautifulSoup(page.content, 'html.parser')

        # isolate ingredient/recipe keys
        # isolate the text from the website and return
        ingredientStr = htmlKey[0][0](soup, htmlKey[0][1])
        recipeStr = htmlKey[1][0](soup, htmlKey[1][1])
        return (ingredientStr, recipeStr)
    else:
        return f'This url "{url}" had a bad request. Error #: {page.status_code}'

# function to find all, provide soup and relvant tags


# function to find all, provide soup and relvant tags
def findAll(soup, key):
    # isolate the section and run if exists
    htmlList = soup.find_all(key[0], key[1])

    if htmlList:
        data = str()
        # add each item to the string and return
        for item in htmlList:
            # Get text from each tag
            data += item.text.strip() + "\n"
        return data
    else:
        return f"Error with these tags:\n{key}\nAnd this soup:\n{soup}"

# function to find a specific section, then read the text of a certain tag


def find_findAll(soup, key):

    # find the section
    section_container = soup.find(key[0], key[1])

    # If the container is found, find all list items within it and return
    if section_container:
        filteredContainer = section_container.find_all(key[2], key[3])

        data = "\n".join([item.text.strip()
                         for item in filteredContainer])

        return data
    else:
        return f"Error with these tags:\n{key}\nAnd this soup:\n{soup}"


def findAttribute(soup, htmlKey):

    resultSet = soup.find_all(htmlKey[0], htmlKey[1])
    attributeValues = ""
    for element in resultSet:
        attributeValues += element.get(htmlKey[2]) + "\n"
    return attributeValues


def storeScrapedRecipes(file, recipeTuple, url):

    recipeName = file.name.split("/")[-1].split(".")[0]
    #clean up the recipe's ingredients and instructions
    ingredients = re.sub(r"\n+", "\n", recipeTuple[0])
    recipe = re.sub(r"\n+", "\n", recipeTuple[1])
    #start the recipe
    string = ""
    string += f'Name:\n{recipeName.replace("-", " ")}\n\n' #title
    string += unicodedata.normalize('NFKD',
                                    f'Ingredients:\n{ingredients}\n\n').replace(u"⁄", "/") #ingredients
    string += f'Directions:\n{recipe}\n\n' #instructions
    string += f'Notes:\nScraped from {url} on {str(date.today()).split(" ")[0]}\n\n' #notes
    string += f'Date:\n{str(date.today()).split(" ")[0]}' #date
    file.write(re.sub(r"\n\n\n+", "\n\n", string))
    # file.write(string)


def findRecipeUrls(scrapeFilePath):
    try:
        with open(scrapeFilePath, "r") as file:
            # Read lines, strip whitespace, and store in a list
            urls = [line.strip() for line in file.readlines()]
            # Convert the list to a tuple
            return tuple(urls)
    except:
        print(f"Error: File '{scrapeFilePath}' not found.")
        return tuple()

def formatIngredients (ingreStr):
    print(ingreStr)

# set-up html parsing keys
# allrecipes key
allRecipe_ingredient = (
    find_findAll, ("ul", {"mm-recipes-structured-ingredients__list"}, 'p', {}))
allRecipe_recipe = (find_findAll, ("div", {
                    "id": "mm-recipes-steps_1-0"}, "p", {"id": re.compile(r'mntl-sc-block_*')}))

# afamilyfeast key
familyFeast_ingredient = (findAttribute, ('input', {
                          'id': re.compile(r"ingredient_checkbox_\w+")}, "aria-label"))
familyFeast_recipe = (
    find_findAll, ('div', {'class': "oc-recipe-instructions tasty-recipes-instructions"}, re.compile(r'(p)|(li)'), {"id": re.compile(r'instruction-step-*')}))

# compile keys in a dictionary of nested tuples
htmlKeys = {"allrecipes": (allRecipe_ingredient, allRecipe_recipe),
            "afamilyfeast": (familyFeast_ingredient, familyFeast_recipe),
            "bad_url": ""}

# set up folder to house the scraped recipes
wd = "/home/jvucelic/Documents/githubDocs/testingRepo/mealPlanner"
scrapedDir = os.path.join(wd, "scrapedRecipes")
newDir = f'{scrapedDir}/{str(date.today()).split(" ")[0]}'
if os.path.isdir(newDir):
    shutil.rmtree(newDir)

os.mkdir(newDir)

# define web pages of interest

urlTuple = findRecipeUrls(f'{scrapedDir}/recipeURLs.txt')

for url in urlTuple:
    #extract the url, checking for trailing "/"
    if url[-1] != "/":
        url += "/"
    
    try:
        domain = parseDomain(url)
        ingredients, recipe = parseRecipeSite(url, htmlKeys[domain])
        #formatIngredients(ingredients)
        with open(f'{newDir}/{url.split("/")[-2]}.txt', "w+", encoding="utf-8") as file:
            storeScrapedRecipes(file, (ingredients, recipe), url)

    except:
        htmlKeys["bad_url"] += url + "\n"
        print("BAD")