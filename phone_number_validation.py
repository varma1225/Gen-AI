from fastapi import FastAPI
import re
from pydantic import BaseModel

app=FastAPI()

class Phone(BaseModel):
    phone:str

@app.post("/phone_validation")
def get_number(data:Phone):

    phone=re.sub(r"\D","",data.phone)

    if len(phone)==10 or len(phone)==12:
        return {
            "status":"Success",
            "normalized_number":phone
        }
    else:
        return {
            "status":"Failed",
            "Invalid_number":phone
        }
