import os
import json
import inquirer

class ApplicationFramework:
    def __init__(self):
        self.__runBot()

    def __runBot(self):
        self.setupBot()
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
            if not 'tree' in botData:
                trees = []
                for file in os.listdir('./trees/'):
                    trees.append(file.replace(".json", "")) 
                questions = [
                    inquirer.List('option',
                        message="Which tree and functions do you want to use?",
                        choices=trees,
                    ),
                ]
                answers = inquirer.prompt(questions)
                botData['function'] = answers['option']
                botData['tree'] = json.load(open('./trees/'+answers['option']+'.json','r'))

        # update bot file
        with open("bot.json", "w") as jsonFile:
            jsonFile.write(json.dumps(botData,indent=4, sort_keys=True, separators=(',', ': ')).replace('\\n','\n'))

    def startChat(self):
        tree = botData['tree']['start']
        print(botData['name'] + ': ' + botData['tree']['compliment'])
        while True:
            message=input('You:')
            if message.strip()=='Tchau':
                print(botData['name'],': Tchau')
                break
            reply = bot.get_response(message)
            print(botData['name'],reply)
            print(reply.conficence)

betterChat()