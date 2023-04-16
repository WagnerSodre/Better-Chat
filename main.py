import json

from src.chatbot import Chatbot

with open('bot.json') as json_file:
    botData = json.load(json_file)

chatbot = Chatbot(botData)

flag=True
print(botData['name']+": " + botData['tree']['compliment'] + '\n You: ')

while(flag==True):
    user_response = input()
    user_response = user_response.lower()
    if(user_response != 'bye'):
        if(user_response == 'thanks' or user_response == 'thank you'):
            flag = False
            print(botData['name']+": You are welcome..")
        else:
            if(chatbot.greeting(user_response) != None):
                print(botData['name']+": "+chatbot.greeting(user_response))
            else:
                response = chatbot.getResponse(user_response)
                if response["negativity"] == True:
                    flag = False
                    print("Enviando para um atendente humano... (Esse é o fim da interação nessa versão)")
                else:
                    print(response["message"])
                    print(chatbot.__dict__)
    else:
        flag=False
        print(botData['name']+": Bye! take care..")    