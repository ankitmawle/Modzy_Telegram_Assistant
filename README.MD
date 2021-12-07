# Modzy Based Telegram Assistant
Ever got over loaded with incoming and long messages on 100s of groups on telegram, ever thought or having a single place where you can get all messages completely summarized, Now we have a solution.

## What it Does 
Telegram Assistant allows you to subscribe to various public channels and get their feed directly to a single chat, summerized into less than 100 words. This will allow users to have benefit of not missing important message, while making lengthy messages short to read from

## Testing
Go to the Modzybot on telegram to check the live demo. Subscribe to a channel and get the summarized feeds directly to your chat
[@Modzybot](https://t.me/Modzybot)

## Deploying the code on your bot 
1. Create the .env file with following specs

```
MODZY_BASE_URL = 
api_id = 
api_hash = 
phone = 
bot_apikey = 
Mongo = 
MODZY_API_KEY = 
```
2. Download required libraries from requirements.txt file using following command
```
pip install -r requirements.txt
```

3. Generate two session files for the base account to work as modzy.session and modzy2.session

4. run main.py file   