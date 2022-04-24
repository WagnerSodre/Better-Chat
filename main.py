import json

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.chatbot import Chatbot

with open('bot.json') as json_file:
    botData = json.load(json_file)

chatbot = Chatbot(botData)

sa = SentimentIntensityAnalyzer()

score = [(tok, score) for tok, score in sa.lexicon.items() if " " in tok]

flag=True
print(botData['name']+": " + botData['tree']['compliment'] + '\n You: ')

while(flag==True):
    user_response = input()
    user_response = user_response.lower()
    scores = sa.polarity_scores(user_response)
    print("Sentiment: ", scores)
    if(user_response != 'bye'):
        if(user_response == 'thanks' or user_response == 'thank you'):
            flag = False
            print(botData['name']+": You are welcome..")
        else:
            if(chatbot.greeting(user_response) != None):
                print(botData['name']+": "+chatbot.greeting(user_response))
            else:
                chatbot.getResponse(user_response)
    else:
        flag=False
        print(botData['name']+": Bye! take care..")    