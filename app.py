# -*- coding: utf-8 -*-
import json
from chalice import Chalice, Response

from src.chatbot import Chatbot

app = Chalice(app_name='better_chat')

@app.route('/interact', methods=['OPTIONS'])
def interact():
    res = Response(
                headers={
                    "Access-Control-Allow-Methods": "POST,PUT,GET,OPTIONS",
                    "Access-Control-Allow-Origin": app.current_request.headers["Origin"],
                    "Access-Control-Allow-Headers": "authorization,content-type,x-empcookie",
                    "Access-Control-Max-Age": "6000",
                },
                body="",
            )
    print(res.__dict__)
    return res

@app.route('/interact', methods=['POST'])
def interact():
    print('call')
    payload = app.current_request.json_body 
    if not payload:
        payload = {}
        
    user_response = payload.get('user_response', None)
    chatbot = payload.get('chatbot', None)

    if not chatbot:
        with open('bot.json') as json_file:
            botData = json.load(json_file)

        chatbot = Chatbot(botData, None)
        return {"message": botData['tree']['compliment'], "chatbot": chatbot.export()}
    else:
        chatbot = Chatbot(None, chatbot)

    user_response = user_response.lower()

    if(user_response != 'tchau'):
        if('obrigado' in user_response):
            res = {"message": "Por nada! Ajudo em mais algo?", "chatbot": chatbot.export()}
        else:
            if(chatbot.greeting(user_response) != None):
                res = {"message": chatbot.greeting(user_response), "chatbot": chatbot.export()}
            else:
                response = chatbot.getResponse(user_response)
                if response["negativity"] == True:
                    res = {"message": "Enviando para um atendente humano... (Esse é o fim da interação nessa versão)", "chatbot": None}
                else:
                    res = {"message": response["message"], "chatbot": chatbot.export()}
    else:
        res = {"message": "Tchau! Até a próxima!", "chatbot": None}   
    return res