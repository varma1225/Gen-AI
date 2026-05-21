from pydantic import BaseModel

class Data(BaseModel):
    name:str
    status:str="pending"
    item:str
    phone_number:str
class Status(BaseModel):
    order_id:str
    
class Record(BaseModel):
    id:str
    status:str