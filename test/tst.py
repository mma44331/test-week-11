from pydantic import BaseModel,Field,ValidationError
from typing import Optional


class User(BaseModel):
    username: str
    age: int
    email: str
class LibraryMember (BaseModel):
    LibraryMember: str = Field(min_length=8,max_length=8)
    full_name: str = Field(min_length=2,max_length=100)
    age: int = Field(ge=0,le=120)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    phone: Optional[str] = Field(max_length=15)

try:
    l1 = LibraryMember(LibraryMember="4794565",full_name="h",age=184,email="eydhfcbfcx.com",phone="45896352")
except ValidationError as e:
    print(e)
#
# u1 = User(username="meyir",age=25,email="ndjfh@gmail.com")
# u2 = User(username="moshe",age=26,email="xassdfh@gmail.com")
# u3 = User(username="bini",age=84,email="ndhth@gmail.com")

print(l1)