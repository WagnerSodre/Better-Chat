# -*- coding: utf-8 -*-
import json
from chalice import Chalice, Response, CORSConfig

from chalicelib.chatbot import Chatbot

cors_config = CORSConfig(
    allow_origin='*',
    allow_headers="*"
)

app = Chalice(app_name='better_chat')

@app.route('/interact', methods=['POST'], content_types=['application/json'], cors=cors_config)
def interact():
    print('call')
    print(app.current_request)
    payload = app.current_request.json_body 
    if not payload:
        payload = {}
        
    user_response = payload.get('user_response', None)
    chatbot = payload.get('chatbot', None)

    if not chatbot:
        with open('/var/task/chalicelib/data/bot.json') as json_file:
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
                try:
                    response = chatbot.getResponse(user_response)
                    if response["negativity"] == True:
                        res = {"message": "Enviando para um atendente humano... (Esse é o fim da interação nessa versão)", "chatbot": None}
                    else:
                        res = {"message": response["message"], "chatbot": chatbot.export()}
                except:
                    with open('/var/task/chalicelib/data/bot.json') as json_file:
                        botData = json.load(json_file)
                    chatbot = Chatbot(botData, None)
                    return {"message": "Me desculpe, eu não te entendi.", "chatbot": chatbot.export()}
    else:
        res = {"message": "Tchau! Até a próxima!", "chatbot": None}   
    print(res)
    return res