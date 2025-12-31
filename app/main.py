import uvicorn
from fastapi import FastAPI
from data_interactor import Connect
from pydantic import BaseModel, Field


class ContactUpdate(BaseModel):
    first_name: str = Field(default=None,max_length=50, min_length=3)
    last_name: str = Field(default=None,max_length=50, min_length=3)
    phone_number: str = Field(default=None,max_length=20, min_length=3)

class Contact(BaseModel):
    first_name: str = Field(max_length=50,min_length=3)
    last_name: str  = Field(max_length=50,min_length=3)
    phone_number: str = Field(max_length=20,min_length=3)



app = FastAPI()


con = Connect()


@app.get("/contacts")
def get_all_contacts():
    data = con.get_contacts()
    return data

@app.post("/contacts")
def create_new_contact(contact:Contact):
    return con.create_new_contact(contact.model_dump())

@app.put("/contacts/{id}")
def update_contact(id:str,contact:ContactUpdate):
    return con.update_contact(id,contact.model_dump(exclude_none=True))

@app.delete("/contacts/{id}")
def delete_contact(id:str):
    return con.delete_contact(id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost",port=8000 , reload=True)
