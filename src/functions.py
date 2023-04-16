import re

from data.userFunctions import UserFunctions

class Functions():
    def __init__(self):
        super().__init__()
        self.userFunctions = UserFunctions()

    def execFunction(self, function, tree, globals):
        functionName = function.split('(')[0]
        newVar = None
        if functionName not in globals:
            varsToReplace = function.split('(')[1].replace('{{', '').replace('}}', '')[:-1].split(', ')
            varsValue = []
            for i in varsToReplace:
                varsValue.append(globals[i])
            functionValue =  getattr(self.userFunctions, functionName)(*varsValue)
            newVar = {functionName: functionValue}
        if 'answer' in tree:
            varsToReplace = re.findall( r'{{(.*?)}}', tree['answer'])
            if functionName in newVar:
                if newVar[functionName] == None:
                    return {'vars': newVar, 'answer': tree['answerNull']}
            for var in varsToReplace:
                vars = var.split(".")
                customVar = newVar
                for i in vars:
                    customVar = customVar[i]
                tree['answer'] = tree['answer'].replace('{{'+var+'}}', str(customVar))
            return {'vars': newVar, 'answer': tree['answer']}
