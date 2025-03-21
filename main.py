from typing import Union

from fastapi import FastAPI
import sys
import os

from fastapi.middleware.cors import CORSMiddleware
# sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from .routes.authRoute import auth
from .routes.contractRoute import contractParse
# from .config.database import database_connect,db
app = FastAPI()
# users_collection = database_connect()

# Ensure the database is available
# if not db:
#     raise Exception("Database connection failed")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/")
# async def read_root():
#     return ("This is the homee")


# #User related route - resigtration, login, getting user details

# @app.post("/registration")
# async def user_registration():
#     #User registratiin logic goes here, with password hashing and all the other things needed for the registration
#     return({"message:": "This is the user registration route"})

# @app.post("/sign-in")
# async def user_signin():
#     #User sign in logic goes here, jwt token all the other things needed for the sigining in
#     return({"message:": "This is the user registration route"})

app.include_router(auth,prefix=f"/api/v1/auth")


@app.get("/user/{user_id}")
async def get_user():
    #Getting user logic goes here, it will include fetching the user details, 
    #including contacts, agent status and other things that they have under their hood
    return({"message:": "This is the user registration route"})



#User contacts space related routes - creating contacts space, creating contacts and updating it where more than one pdf can be uploaded all for the same movie or porperty

# @app.post("/contacts/create-space")
# async def create_contact_space():
#     #Creating contact_space related logic goes here
#     return({"message:": "This is the contact space post route"})


# @app.post("/contacts/add_contacts")
# async def upload_contacts():
#     #Uploading contacts and feeding that contact to the gemini api logics goes here
#     #parsed contact details will be saved in the database and that saving logic will also goes here probably
#     return({"message:": "This is the contact uploading post route"})

app.include_router(contractParse,prefix=f"/api/v1")

# @app.get("/contacts/{contact_id}")
# async def get_contact_parsed_metadata():
#     #All the individual contact getting logic goes here. This route will fetch the meta data from the db using contact id provided and serve
#     return({"message:": "This is the individual contact get route"})

# @app.get("/contacts/{contact_space_id}")
# async def get_contact_parsed_metadata_under_a_particular_space():
#     #All the available contact getting logic goes here. This route will fetch the meta data from the db using contact_space_id provided and serve all the available contact in that space
#     return({"message:": "This is the all contact under space get route"})

@app.put("/contacts/update/{contact_space_id}")
async def update_contact():
    #If we want to update the contacts spaces data, then the logic goes here.
    return({"message:": "This is the update contact space data put route"})

@app.put("/contacts/override/{contact_id}")
async def update_contact():
    #If we want to explicitly override the contacts metadata, then the logic goes here. Like for if our gemini misses of or fails to obtain certain attributes of the contacts then we will be able to manually update it,
    #that logics goes here
    return({"message:": "This is the update individual contact metadata put route"})

@app.delete("/contacts/{contact_id}")
async def update_contact():
    #If we want to delete contacts, that logic goes here
    return({"message:": "This is the delete individual contact delete route"})



#agents route, these routes will be responsible for controlling ai agents, there will be realtime update what agents are doing maybe using websocket

@app.get("/agents/{contact_id}")
async def initiate_agent():
    #agent will get the contact metadata using contact id , and using that metadata it will scrap the erbsite and 
    #update the contact violating database
    return({"message:": "This is the calling agent route"})

@app.get("/agents/{agent_id}")
async def initiate_agent():
    #this route will give the real time update of the agent that is current working or not using websocket
    return({"message:": "This is the agent status route"})