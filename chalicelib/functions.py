import re

from chalicelib.data.userFunctions import UserFunctions

class Functions():
    def __init__(self):
        super().__init__()
        self.userFunctions = UserFunctions()

    def execFunction(self, function, tree, globals):
        print('execFunction!!!!!!!!!!!!!!!!!!!!!!!')
        print(function)
        print(tree)
        print(globals)
        functionName = function.split('(')[0]
        newVar = None
        if functionName not in globals:
            varsToReplace = function.split('(')[1].replace('{{', '').replace('}}', '')[:-1].split(', ')
            varsValue = []
            for i in varsToReplace:
                varsValue.append(globals[i])
            functionValue =  getattr(self.userFunctions, functionName)(*varsValue)
            if functionValue:
                newVar = {functionName: functionValue}
        else:
            print(f'{functionName} in globals')
            newVar = {functionName: globals[functionName]}
        if 'answer' in tree and newVar:
            varsToReplace = re.findall( r'{{(.*?)}}', tree['answer'])
            for var in varsToReplace:
                vars = var.split(".")
                customVar = newVar
                for i in vars:
                    customVar = customVar[i]
                tree['answer'] = tree['answer'].replace('{{'+var+'}}', str(customVar))
            return {'vars': newVar, 'answer': tree['answer']}
        else:
            return {'vars': None, 'answer': tree['answerNull']}
