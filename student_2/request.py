from fastapi import FastAPI,Request

req=FastAPI()

@req.get("/")
async def read_request(request:Request):
       
    body=await request.json()

    return{
        "body":body
      
    }