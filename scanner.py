import os
import requests
from dotenv import load_dotenv
from dataLayer import in_database, increment_quantity, add_item
from bs4 import BeautifulSoup

def get_upcdata(UPC):
    API_KEY = os.getenv('API_KEY')
    requestString = "https://api.upcdatabase.org/product/" + str(UPC) + "?apikey=" + str(API_KEY)
    response = requests.get(requestString)
    if response.status_code == 200:
        if response.json()["success"] == True:
            return response.json()
        return None
    else:
        return None
        
def initialize_data(UPC):
    rawData = get_upcdata(UPC)
    print(rawData)
    data = default_data(UPC)
    if rawData is None:
        return data

    if rawData["title"] != "":
        data["title"] = rawData["title"]
    else:
        data["title"] = rawData["description"]

    return data

def default_data(UPC):
    data = {}
    data["title"] = "Unknown"
    data["upc"] = UPC
    data["quantity"] = 1
    data["price"] = None
    data["notes"] = None
    data["lowNum"] = 0
    return data

# Powered by Nutritionix API
def get_data(UPC):
    NUTRITIONIX_APP = os.getenv('NUTRITIONIX_APP')
    NUTRITIONIX_KEY = os.getenv('NUTRITIONIX_KEY')
    requestString = "https://trackapi.nutritionix.com/v2/search/item?upc=" + str(int(UPC))
    response = requests.get(requestString, headers={"x-app-id": NUTRITIONIX_APP, "x-app-key": NUTRITIONIX_KEY})  
    print(response.json())
    if "foods" in response.json():
        data = response.json()["foods"][0]
        return data
    else:
        return None

def populate_data(UPC):
    rawData = get_data(UPC)
    data = blank_nutritionix(UPC)
    if rawData is None:
        return data
    data["food_name"] = rawData["food_name"]
    data["brand_name"] = rawData["brand_name"]
    data["upc"] = UPC
    data["quantity"] = 1
    data["notes"] = None
    data["lowNum"] = 0
    data["img_url"] = rawData["photo"]["thumb"]
    return data

def blank_nutritionix(UPC):
    data = {}
    data["food_name"] = "Unknown"
    data["brand_name"] = None
    data["upc"] = UPC
    data["quantity"] = 1
    data["notes"] = None
    data["lowNum"] = 0
    data["img_url"] = None
    return data

def dcpi_data(DCPI):
    rawData = get_target_data(DCPI)
    print(rawData)
    data = blank_target(DCPI)
    if rawData is None:
        return data
    data["food_name"] = rawData["title"].replace(" : Target", "")
    data["url"] = rawData["link"]
    data["img_url"] = rawData["pagemap"]["cse_image"][0]["src"]
    return data

def get_target_data(DCPI):
    formattedDCPI = DCPI[:3] + "-" + DCPI[3:5] + "-" + DCPI[5:]
    print(formattedDCPI)
    requestString = "https://customsearch.googleapis.com/customsearch/v1/?exactTerms=" + formattedDCPI + "&cx=b4baf1166a6ca203f&key=" + os.getenv('CSE_API_KEY')
    response = requests.get(requestString)
    print(response.json())
    if "items" in response.json():
        data = response.json()["items"][0]
        return data
    else:
        return None

def blank_target(DCPI):
    data = {}
    data["food_name"] = "Unknown"
    data["brand_name"] = None
    data["upc"] = DCPI
    data["quantity"] = 1
    data["notes"] = None
    data["lowNum"] = 0
    data["img_url"] = None
    data["url"] = None
    return data

def process_upc(UPC,DCPI=False):
    if in_database(UPC):
        increment_quantity(UPC)
        print("Incremented quantity")
    else:
        data = ""
        if DCPI:
            data = dcpi_data(UPC)
        else:
            data = populate_data(UPC)
        print(data)
        add_item(data)

def main():
    load_dotenv()
    #Test UPC, from Matzos
    while True:
        UPC = input("Enter UPC: ")
        if UPC == "":
            break
        process_upc(UPC, True)

if __name__ == "__main__":
    main()
