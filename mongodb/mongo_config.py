from pymongo import MongoClient

# Connect to local MongoDB database
db_client = MongoClient('localhost', 27017)
db = db_client.falcon_db
l_transfer_data = db.l_transfer_data
idp_ips = db.idp_ips