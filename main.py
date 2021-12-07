from re import TEMPLATE
from telethon import TelegramClient, events
from telethon.tl.functions.channels import JoinChannelRequest
import pymongo
import time
from modzy import ApiClient
import telethon.tl.types as types
import multiprocessing
import sys
import os
import logging
import dotenv
from modzy.error import ResultsError
from modzy.jobs import Jobs
import requests

dotenv.load_dotenv()
BASE_URL = os.getenv('MODZY_BASE_URL')
API_KEY = os.getenv('MODZY_API_KEY')
bot_apikey= os.getenv('bot_apikey')
myclient = pymongo.MongoClient(os.getenv('Mongo'))
mydb = myclient["modzy"]
usersToGroups= mydb["usersToGroups"]

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
phone = os.getenv('phone')
session_file1 = 'modzy'  # use your username if unsure
session_file2 = 'modzy2'
botfile1= 'bot'
botfile2= 'bot2'
password = ''  # if you have two-step verification enabled

client = TelegramClient(session_file1, api_id, api_hash, sequential_updates=True)
client2 = TelegramClient(session_file2, api_id, api_hash, sequential_updates=True)
botClient = TelegramClient(botfile1, api_id, api_hash)
#botClient2 = TelegramClient(botfile2, api_id, api_hash)
@botClient.on(events.NewMessage(incoming=True))
async def bot_handle(event):
    message=event.message
    chatId= event.chat_id
    print(message.message)
    print(chatId)
    if (message.message[0:10]=="/subscribe"):
        link= message.message[10:];
        link=link.replace(" ", "")
        loc= link.find("t.me/")
        if loc==-1:
            await event.respond("Please check the message format [Link not found]")
        else :
            await client2.start(phone, password)
            try:
                updates = await client2(JoinChannelRequest(link[loc+5:]))
                await client2.disconnect()
                print(updates.chats[0].id)
                userDict={"user": chatId, "chat": updates.chats[0].id}
                check=usersToGroups.find(userDict)
                try:
                    check[0]
                except: 
                    insert= usersToGroups.insert_one(userDict)
                await event.respond("Successfully updated list")
            except:
                await event.respond("Please check the message format [Link Error]")
            
    if (message.message == "/start"):
        await event.respond("Welcome to Modzy Manager Telegram Assistant.\nGet all the messages you receive on your chats summarized here at one place \nTo subscribe to a public channel copy the Link to the channel and send it with /subcribe command followed by the link\n \n for example \n /subscribe t.me/Modzybot")



@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    message= event.message
    chatId=str(event.chat_id)
    query={"chat": int(chatId[3:])}
    print(chatId)
    users= usersToGroups.find(query)
    if users[0]:
    
        is_link=False
        is_doc= False
        is_doc= False
        is_pdf= False
        is_photo= False
        if type(event.media) is types.MessageMediaPhoto:
            is_photo=True
        elif type(event.media) is types.MessageMediaDocument:
            if event.media.document.mime_type=='application/pdf':
                is_pdf=True
            else:
                is_doc=True
        links=[]
        try:
            for entity in event.entities:
                if type(entity) is types.MessageEntityUrl:
                    is_link=True
                    #links=links+eve.message[entity.offset:entity.offset+entity.length]+"\n"
                    links.append(event.message.message[entity.offset:entity.offset+entity.length])
                elif type(entity) is types.MessageEntityTextUrl:
                    is_link=True
                    links.append(entity.url)
        except:
            is_link=False
        
        if len(message.message)>50:
            modzyClient = ApiClient(base_url=BASE_URL, api_key=API_KEY)
            model = modzyClient.models.get("rs2qqwbjwb")
            modelVersion = modzyClient.models.get_version(model, model.latest_version)
            sources = {"source-key": {"input.txt": message.message}}
            job = modzyClient.jobs.submit_text(model.modelId, modelVersion.version, sources)
            job.block_until_complete(timeout=None)
            if job.status == Jobs.status.COMPLETED:
                result = job.get_result().get_source_outputs("source-key")['results.json']
                print(result.summary)
                summary= result.summary
            else: 
                summary= "Error getting modzy result"
        else:
            summary= "Same as original: "+message.message
        groupName= await client.get_entity(int(chatId))
        
        Template= "Hello, \nWe received a message on "+ groupName.title 
        if is_photo:
            Template+= "\n\nWhich contains an image and caption with summary as follows \n "     
            
        elif is_pdf:
            Template+= "\n\nWhich contains an pdf and caption with summary as follows \n "     
        elif is_doc:
            Template+= "\n\nWhich contains an document and caption with summary as follows \n "     
        else: 
            Template+= "\n\nWhich contains message with summary as follows\n"

        Template+= summary

        if is_link:
            Template+="\n\nWe found following links in the message\n"
            for i in links:
                Template+=i +"\n"
        print(Template)
        for user in users:
            
            data= {'chat_id':user['user'],'text':Template}
            res= requests.post("https://api.telegram.org/bot"+bot_apikey+"/sendMessage",data=data)
            print(res)
    #from1 = await client.get_entity("t.me/linemeup")
    #print(event.message)
    #print(event.message.message)
    #await client.send_message(from1,event.message)
    
    #await client.send_message(from2,event.message)

def initiateClient(phone, password):
    print(time.asctime(), '-', 'bot client execution started')
    botClient.start(bot_token=bot_apikey)
    botClient.run_until_disconnected()
    print(time.asctime(), '-', 'Stopped bot Client')

def initBotClient():
    print(time.asctime(), '-', 'base client execution started')
    client.start(phone, password)
    client.run_until_disconnected()
    print(time.asctime(), '-', 'Stopped base Client')

if __name__ == '__main__':


    base=multiprocessing.Process(target=initiateClient,args=(phone, password))
    base.start()
    bot=multiprocessing.Process(target=initBotClient,args=())
    bot.start()
    base.join()
    bot.join()

