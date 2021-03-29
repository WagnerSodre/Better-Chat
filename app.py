import os
import json

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

class ApplicationFramework:
    def __init__(self):
        self.__runBot()

    def __runBot(self):
        self.setupBot()
        self.startBot()
        self.startChat()

# Create an "application":
class betterChat(ApplicationFramework):
    def setupBot(self):
        # checks if bot file exists, if not, create a new one
        if not os.path.isfile('bot.json'):
            with open('bot.json', 'w') as f: 
                json.dump({}, f)

        # check the properties of the bot, if there isn't, ask the user
        with open('bot.json') as json_file:
            global botData
            botData = json.load(json_file)
            if not 'name' in botData:
                botData['name'] = input("Enter bot name: ")
            if not 'language' in botData:
                botData['language'] = input("Enter bot language: ")

        # update bot file
        with open("bot.json", "w") as jsonFile:
            json.dump(botData, jsonFile)

    def startBot(self):
        #start bot
        global bot
        bot = ChatBot(
            botData['name'],
            logic_adapters=[
                {
                    "import_path": "chatterbot.logic.BestMatch"
                }
            ]
        )
        trainer = ChatterBotCorpusTrainer(bot)
        trainer.train('./corpus/'+botData['language']+'/')

    def startChat(self):
        while True:
            message=input('\t\t\tYou:')
            if message.strip()=='Tchau':
                print(botData['name'],': Tchau')
                break
            reply = bot.get_response(message)
            print(botData['name'],reply)
            print(reply.conficence)

betterChat()