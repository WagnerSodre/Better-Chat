import re

from data.userFunctions import UserFunctions

class Functions():
    def __init__(self):
        super().__init__()
        self.userFunctions = UserFunctions()

    def execFunction(self, function, tree, globals):
        functionName = function.split('(')[0]
        if functionName not in globals:
            varsToReplace = re.search('{{(.*)}}', function)
            varsValue = []
            for i in range(len(varsToReplace.groups())):
                varsValue.append(globals[varsToReplace.group(i).replace('{{', '').replace('}}', '')])
            functionValue =  getattr(self.userFunctions, functionName)(*varsValue)
            newVar = {functionName: functionValue}
        if 'answer' in tree:
            varsToReplace = re.findall( r'{{(.*?)}}', tree['answer'])
            for var in varsToReplace:
                vars = var.split(".")
                customVar = newVar
                for i in vars:
                    customVar = customVar[i]
                tree['answer'] = tree['answer'].replace('{{'+var+'}}', str(customVar))
            return {'vars': newVar, 'answer': tree['answer']}
