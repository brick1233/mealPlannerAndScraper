from datetime import datetime as date
import shutil
import re
import itertools
import os
from random import randrange
from bs4 import BeautifulSoup


def stringToFloat(floatStr):
    #print(floatStr)
    # convert quantity to float
    

    if "/" and " " in floatStr:

        numer = float(floatStr.split(" ")[1].split("/")[0])
        denom = float(floatStr.split(" ")[1].split("/")[1])
        return (float(floatStr.split(" ")[0]) + float(numer/denom))
    elif "/" in floatStr:

        numer = float(floatStr.split("/")[0])
        denom = float(floatStr.split("/")[1])
        return (numer/denom)

    elif " " in floatStr:
        return (float(floatStr.split(" ")[0]) + float(floatStr.split(" ")[1]))
    else:
        try:
            return float(floatStr)
        except:
            print(
                f'ERROR: Failed to parse this string "{floatStr}" into a float value.')

def processScrapedRecipe(ingredientStr):
    # remove trailing ")"s
    floatStr = re.sub(r"[)]+\Z", "", ingredientStr)
    # remove nested parentheses (ADD LOGIC !!)
    if re.search(r'[(].+[(]', floatStr):
        nestedParIndex = re.search(r'[(].+[(]', floatStr).span()[1]
        floatStr = floatStr[:nestedParIndex-1] + floatStr[nestedParIndex:]
    #split the float str into list 
    splitStr = floatStr.split("(")
    if "TO" in splitStr[1]:
        unitQuantity = stringToFloat(splitStr[0].strip())  
        unitSize = float(splitStr[1].split("TO")[1].strip()[0])
        unit = str(splitStr[1]).split(")")[0].split(" ")[-1]
        item = splitStr[1].split(")")[1]
        amnt = float(unitSize) * float(unitQuantity)
        return amnt, unit, item
    else:
        parentheseInfo = splitStr[1].replace("-", " ")
        unitQuantity = stringToFloat(splitStr[0].strip())  
        unitSize = float(parentheseInfo.split(" ")[0])
        unit = parentheseInfo.split(")")[0].split(" ")[-1]
        item = splitStr[1].split(")")[1]
        amnt = float(unitSize) * float(unitQuantity)
        return amnt, unit, item
    
def findAmount(amtStr):
    """
    Extracts and converts ingredient amount and unit from a string.

    Args:
        amnStr: String containing the amount and unit.

    Returns:
        the amount as a float and the unit as a string.
    """
    # define regex
    regex = r"(\d+|\.\d+)(\.\d+\s+\d+\/\d+|\.\d+|\/\d+|\s+\d+\/\d+)?"

    # clean passed string
    amtStr = amtStr.strip()
    # extract unit and quantity
    try:
        # find int, float,
        amount = re.match(regex, amtStr)
        unit = amtStr[(amount.span()[1]+1):]

        # convert quantity to float
        rawAmnt = amount.group()
        amount = stringToFloat(rawAmnt)

        # convert to numbers if dozen is unit
        if unit == "DOZEN":
            amount = float(rawAmnt)*12
            unit = ""

        # return quantity and unit
        return round(float(amount), 2), unit
    except:
        amount = amtStr
        return round(float(amount), 2), ""


def findRecipes(recipeDir):
    """
    Finds all recipe files within a directory.

    Args:
        recipeDir: Path to the directory containing recipe files.

    Returns:
        fileNames: A set of paths to the recipe files.
    """

    fileNames = set()
    for root, dirs, files in os.walk(recipeDir, topdown=False):
        for name in files:
            if name.endswith(".txt"):
                fileNames.add(os.path.join(root, name))
    return fileNames


def readRecipe(fileName):
    """
    Reads a recipe file and extracts the ingredients.

    Args:
        fleName: Path to the recipe file.

    Returns:
        ingredientList: A list of ingredient strings.
    """
    # Open the recipe
    with open(fileName, 'r') as recipe:
        # Store the files contents as lists of lines
        lines = [line.strip() for line in recipe]

    # split the recipe by section
    recipeList = [[]]
    for x, y in itertools.groupby(lines, lambda z: z == ''):
        if x:
            recipeList.append([])
        recipeList[-1].extend(y)

    # remove the empty lines (list comprehension is pretty baller)
    recipeList = [[line for line in section if line != '']
                  for section in recipeList]

    return recipeList


def createWeeklyFolder(recipes, shoppingList, storageDir):
    """
    Creates a new folder with the week's recipes and shopping list.

    Args:
        recipes: Set of paths to the recipe files.
        shoppingList: Dictionary of ingredients and their quantities.
        storage_dir: Path to the directory where weekly folders are stored.
    """
    # make newDir (remove if already exits)

    
    # iterate over each recipe and copy to newDir
    for path in recipes:
        recipeHtml = os.path.basename(path).replace(".txt", ".html")
        recipeSections = tuple(readRecipe(path))
        textToHTML(os.path.join(formatDir, "htmlFormatRecipe.txt"), f'{storageDir}/{recipeHtml}', recipeSections)
    
    #write the shopping list down
    textToHTML(os.path.join(formatDir, "htmlFormatShoppingList.txt"), f'{storageDir}/shoppingList.html', shoppingList)
            

#function to create html tag
#args: soup-soup to add to, tagName-type of tag, tagString-text to populate tag
def makeHtmlTag(soup, tagName, tagString):
    newTag = soup.new_tag(tagName)
    newTag.string = tagString
    return newTag

def textToHTML(templateHTML, outputPath, recipeInfo):
    #extract recipe info
    if type(recipeInfo) == tuple:
        recipeName = recipeInfo[0][1]
        ingreList = recipeInfo[1][1:]
        recipeList = recipeInfo[2][1:]
        noteList = recipeInfo[3][1:]
        #write info in proper locations according to the template
        with open(templateHTML, "r") as htmlBase, open(outputPath, "w") as newHtml:
            
            recipeSoup = BeautifulSoup(htmlBase.read(), features="lxml")
            title = recipeSoup.find('div', {"id":"recipe-name"})
            ingredients = recipeSoup.find('ul', {"id":"ingredients"})
            recipe = recipeSoup.find('ol', {"style" : "list-style-type: decimal"})
            notes = recipeSoup.find('ul', {"id":"notes"})
            recipeDate = recipeSoup.find('h2', {"id":"date"})
            
            #title tag
            title.insert_after(makeHtmlTag(recipeSoup, "p", recipeName))
            
            #list of ingredient tags
            for item in reversed(ingreList):
                ingredients.insert_after(makeHtmlTag(recipeSoup, "li", item))
            
            #list of recipe steps
            for item in reversed(recipeList):
                recipe.insert_after(makeHtmlTag(recipeSoup, "li", item))
            
            #potential notes
            if noteList:
                for item in reversed(noteList):
                    notes.insert_after(makeHtmlTag(recipeSoup, "li", item))
                    
            recipeDate.insert_after(makeHtmlTag(recipeSoup, "p", str(date.today()).split(" ")[0]))
    
        
            newHtml.write(recipeSoup.prettify())
    elif type(recipeInfo) == dict:
        # write shoppingList to html file
        with open(templateHTML, "r") as htmlBase, open(outputPath, "w") as newHtml:
            shoppingListSoup = BeautifulSoup(htmlBase.read())
            listTag = shoppingListSoup.find('ol', {"style" : "list-style-type: disc"})
            for ingredient, quantity in recipeInfo.items():
                listTag.insert_after(makeHtmlTag(shoppingListSoup, "li", f"{quantity[0]} - {quantity[1]} {ingredient}"))
                
            newHtml.write(shoppingListSoup.prettify())


# Set up imports and directory stuff
wd = "/mealPlanner"
storageDir = wd+"/mealPlans"
formatDir =  "/mealPlanner/formatFiles"

try:
    mealPlanLen = int(input("How many days do you want to plan for?\n")) + 1
except:
    print("Error: Valid length not provided. Meal plan will be for 4 days.")
    mealPlanLen = 5
    
#recipeDir = 'recipes'
recipeDir = 'recipes/'

# find the recipes as a tuple of paths
recipeSet = tuple(findRecipes(f'{wd}/{recipeDir}'))

#based on the available recipes and meal plan length, "randomly" select a number of them
numberOfRecipes = len(recipeSet)
mealPlan_recipes = []
for x in range(mealPlanLen):
    mealPlan_recipes.append(recipeSet[randrange(numberOfRecipes)])
    
# open each recipe, and store the ingredients used
ingredientList = []
for recipe in enumerate(mealPlan_recipes):
    # check to see if ingredients are where expected
    # if not where expected, return empty list
    if readRecipe(recipe[1])[1][0].upper() != "INGREDIENTS:":
        print(
            f"Could not find the ingredient's section for the recipe {recipe[1].upper()}. Recipe files should have ingredients as the second section.")
        ingredients = []
    # else, return ingredient list
    else:
        ingredients = readRecipe(recipe[1])[1][1:]
    
    ingredientList.extend(ingredients)


cleanerDict = {r"tea\w+\s": "tsp ", r"table\w+\s": "tbs " , r"tbl\w+\s": "tbs ",
               r"ounce\w+\s": "oz ", r"pound(\w+)?": "lb", r"cup\w+": "cup",
               r"\([^()]*\)$":"", r"\W\Z": ""} #last two removes trailing comments/punctuation

# standardize the units names and make uppercase
for oldStr, newStr in cleanerDict.items():

    ingredientList = [re.sub(oldStr, newStr, line, flags=re.IGNORECASE)
                      for line in ingredientList]

ingredientList = [line.upper().replace("  ", " ") for line in ingredientList]


# extract each ingredient, adding ammounts in a dictionary
shoppingList = {}
# patterm identifiers
digitFirst_regex = r'^\d+'
digitFirstParser_regex = r'^(\d+(\/\d+)?\s+(\d+\/\d+)?(\(.+[)])?)'
for line in ingredientList:
    #instantiate varibles
    amnt, unit, item = ('','','')
    # check for different formats
    digitFirst = re.match(digitFirst_regex, line)
    if digitFirst:
        
        try:
            if re.search(r'[(]\d', line):
                amnt, unit, item = processScrapedRecipe(line)
                #print(processScrapedRecipe(line))
            else:
                quantMatch = re.match(digitFirstParser_regex, line)
                amnt = quantMatch.group()
                quantDescription = line[quantMatch.span()[1]:].strip()
                #print(quantDescription)
                amnt = stringToFloat(amnt.strip())
                unit = ''
                item = quantDescription
                foundUnit = False
                for keyWord in cleanerDict.values():
                    if re.match(keyWord.upper().strip(), item.split(" ")[0].strip()) and keyWord != "":
                        unit = quantDescription.split(" ")[0]
                        item = item.replace(unit, "")
                        foundUnit = True
                        break
                if foundUnit == False:
                    unit = ''
                

        except:
            print(f'Error: failed to process this ingredient: "{line}".')
    elif re.search(r"\d", line):
        item, quant = line.split("-", maxsplit=1)
        amnt, unit = findAmount(quant)
    else:
        print(f"Error: could not identify any numeric values in this string \n{line}")
    
    #add items to shopping list 
    if item.strip() not in shoppingList.keys() and item.strip() != "":
        shoppingList[item.strip()] = [amnt, unit.strip()]
    elif item.strip() in shoppingList.keys():
        shoppingList[item.strip()][0] += amnt

#create a folder with the shopping list and recipes
mealPlan_dir = f'{storageDir}/{str(date.today()).split(" ")[0]}'
if os.path.isdir(mealPlan_dir):
    shutil.rmtree(mealPlan_dir)
os.mkdir(mealPlan_dir)

createWeeklyFolder(mealPlan_recipes, shoppingList, mealPlan_dir)
