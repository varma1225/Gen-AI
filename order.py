from multiprocessing import get_logger
from urllib.error import HTTPError
from models import Data,Status,Record
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import logging
import uuid

app = FastAPI()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger=logging.getLogger(__name__)
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["orders_db"]
collection = db["orders"]



@app.post("/insert-user")
def insert_details(details:Data):
    order_id="ORD-"+str(uuid.uuid4())[:4]
    data = {
         "name":details.name,
         "order_id":order_id,
         "item":details.item,
         "status":details.status if details.status else "pending",
         "number":details.phone_number
    }

    record=collection.insert_one(data)
    if record.inserted_id:
        logging.info(f"inserted id{record.inserted_id}")
       
        return {
            "order_id":order_id,
            "staus":"succesfully inserted"


        }
    else :
        raise HTTPError(status_code=404,detail="Failed to insert record")
        



@app.post("/validate_status")
def validation(data: Status):

    try:
        logging.info(f"Received order_id: {data.order_id}")

        record = collection.find_one({"order_id": data.order_id})

        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        else:
            return {
                "cust_name":record["name"],
                "order_id":data.order_id,
                "order_name":record["item"],
                "order_status":record["status"],
                "number":record["number"]
            }
    except HTTPException as e :
        print(f"http error {e}")
@app.put("/update-status")
def update_status(details:Record):
    id=details.id
    status=details.status
    update=collection.update_one({"order_id":id},{"$set":{"status":status}})

    if update.modified_count:
        return {
            "message":"updated status"

        }
    else:
        raise HTTPError(status_code=404,detail="Failed to insert record")
       
@app.get("/get-details/{number}")
def get_details_by_number(number):
    record=collection.find_one({"number":number})
    if record:
        return {


            "cust_name":record["name"],
            "order_id":record["order_id"],
            "order_name":record["item"],
            "order_status":record["status"],
            "number":record["number"]

        }
    else :
        raise HTTPException(status_code=404,detail="record not found")
