from typing import Union
from fastapi import  APIRouter, UploadFile, File,Request
from ..controller.contractController import get_contact_parsed_metadata_under_a_particular_space,create_contact_space,upload_contacts,update_contact
from ..models.Model import contractSpaceModel
contractParse = APIRouter()

@contractParse.post("/contacts/create-space")
async def func2(details:contractSpaceModel,request:Request):
    return await create_contact_space(details,request)


@contractParse.post("/contacts/add_contacts")
async def func3(file: UploadFile = File(...)):
    return await upload_contacts(file)

@contractParse.get("/contacts/{contact_space_id}")
async def func4():
    return await get_contact_parsed_metadata_under_a_particular_space()
@contractParse.put("/contacts/update/{contact_space_id}")
async def func5():
    return await update_contact()

@contractParse.put("/contacts/override/{contact_id}")
async def func6():
    return await update_contact()

@contractParse.delete("/contacts/{contact_id}")
async def func7():
    return await update_contact()
