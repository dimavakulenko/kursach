from pydantic import BaseModel



class InformationAboutUser(BaseModel):
    name: str
    second_name: str
    photo_url: str
    country: str