from fileinput import filename

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import logging

app=FastAPI()
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging=logging.getLogger(__name__)

client=MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.5.8")
db=client["orders_db"]
collection=db["orders"]

@app.get("/checkstatus/{order_id}")
def check_status(order_id:str):
    
    logging.info("Recieved Order_id")
    record=collection.find_one({"order_id":order_id})

    if not record:
        logging.error("invalid order_id")
        raise HTTPException(status_code=404,detail="NOT DATA FOUND")
    else:
        logging.info("valid order_id")
        status=record["status"]
        return status
