from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.get("/")
async def read_root():
    return ("This is the homee")


#User related route - resigtration, login, getting user details

@app.post("/registration")
async def user_registration():
    #User registratiin logic goes here, with password hashing and all the other things needed for the registration
    return({"message:": "This is the user registration route"})

@app.post("/sign-in")
async def user_signin():
    #User sign in logic goes here, jwt token all the other things needed for the sigining in
    return({"message:": "This is the user registration route"})


@app.get("/user/{user_id}")
async def get_user():
    #Getting user logic goes here, it will include fetching the user details, 
    #including contacts, agent status and other things that they have under their hood
    return({"message:": "This is the user registration route"})



#User contacts space related routes - creating contacts space, where more than one pdf can be uploaded all for the same movie or porperty

@app.post("/contacts/create-space")
async def create_contact_space():
    #Creating contact_space related logic goes here
    return({"message:": "This is the contact space post route"})


@app.post("/contacts/add_contacts")
async def upload_contacts():
    #Uploading contacts and feeding that contact to the gemini api logics goes here
    #parsed contact details will be saved in the database and that saving logic will also goes here probably
    return({"message:": "This is the contact uploading post route"})

@app.get("/contacts/{contact_id}")
async def get_contact_parsed_metadata():
    #All the individual contact getting logic goes here. This route will fetch the meta data from the db using contact id provided and serve
    return({"message:": "This is the individual contact get route"})