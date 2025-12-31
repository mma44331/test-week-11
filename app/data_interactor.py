import os
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
from dotenv import load_dotenv
from bson import ObjectId
load_dotenv()


def get_con_mongo():
    try:

        client = pymongo.MongoClient(host=os.getenv("DB_HOST"),
                                     port=int(os.getenv("DB_PORT")),
                                     serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client
    except PyMongoError as err:
        if isinstance(err, ServerSelectionTimeoutError):
            print("Cannot connect to MongoDB server")
        elif isinstance(err, ConnectionFailure):
            print("MongoDB connection failed")
        else:
            print(err)


def get_db(client):
    if os.getenv("DB_NAME") not in client.list_database_names():
        print("DB not found")
    return client[os.getenv("DB_NAME")]



def get_col(db):
    if os.getenv("DB_COLACTION") not in db.list_collection_names():
        print("colaction not found")
    return db[os.getenv("DB_COLACTION")]



def get_col_connect():
    client = get_con_mongo()
    db = get_db(client)
    col = get_col(db)
    return col


class Connect():
    def __init__(self):
        self.col = get_col_connect()
        if self.col is None:
            raise ConnectionError("Cannot connect to the database")

    def get_contacts(self)->list | dict:
        try:
            res = self.col.find()
            lst = []
            for item in res:
                item["_id"] = str(item["_id"])
                lst.append(item)
            return lst
        except PyMongoError as err:
            print(f"Error db {err}")
            return {"error":str(err)}



    def create_new_contact(self,contact)->dict:
        try:
            print(type(contact))
            res = self.col.insert_one(contact)
            id1 = res.inserted_id
            return {"message": "Contact created successfully","id": str(id1)}
        except PyMongoError as err:
            print(f"Error db {err}")
            return {"error": str(err)}

    def update_contact(self,id:str,contact:dict)->dict | str:
        try:
            self.col.update_one({"_id":ObjectId(id)},{"$set":contact})
            return "The contact person was successfully updated."
        except PyMongoError as err:
            print(f"Error db {err}")
            return {"error": str(err)}




    def delete_contact(self,id)->dict | str:
        try:
                self.col.delete_one({"_id":ObjectId(id)})
                return "The contact was successfully deleted."
        except PyMongoError as err:
            print(f"Error db {err}")
            return {"error": str(err)}


a = Connect()

