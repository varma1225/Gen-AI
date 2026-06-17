from multiprocessing import get_logger

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import logging

app = FastAPI()

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging=logging.getLogger(__name__)
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["orders_db"]
collection = db["orders"]


class Status(BaseModel):
    order_id: str


@app.post("/validate_status")
def validation(data: Status):

    try:
        logging.info(f"Received order_id: {data.order_id}")

        record = collection.find_one({"order_id": data.order_id})

        if not record:
            raise HTTPException(status_code=404, detail="Record not found")

        update_record = collection.update_one(
            {"order_id": data.order_id},
            {"$set": {"status": "completed"}}
        )

        return {
            "message": "Status updated successfully",
            "matched_count": update_record.matched_count,
            "modified_count": update_record.modified_count,
            "status_code": 200
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        logging.error(str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")