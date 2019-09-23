import pymongo
import json
import os
import sys

# Create database : >use web_scraping_db
#Create collection : >db.createCollection(all_data)


myclient = pymongo.MongoClient('mongodb://localhost:27017/')

mydb = myclient['web_scraping_db']
mycol=mydb["all_data"]


with open(os.path.join(sys.path[0], "json_data.json"), "r") as f:
    file_data = json.load(f)

mycol.insert(file_data)
myclient.close()

