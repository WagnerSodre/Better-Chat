import json

class TreeNavigation():
    def __init__(self, botData, tree):
        super().__init__()
        self.botData = botData
        self.tree = tree

    def resetTree(self):
        self.tree = self.botData['tree']['start']
        return self.tree

    def retry(self, target):
        temp = self.tree
        self.resetTree()
        self.findByChild(temp, self.tree)
        self.updateTree(target, self.tree)
        if 'answer' in self.tree:
            return self.tree['answer']
        elif 'answerNull' in self.tree:
            return self.tree['answerNull']
        elif self.tree != self.botData['tree']['start']:
            return self.retry(target)
        else:
            return "I am sorry! I don't understand you"

    def findByChild(self, branch, originalTree):
        for child in originalTree:
            if json.dumps(child).lower().find(json.dumps(branch).lower()) >= 0:
                if ('childs' in child and child['childs'] == branch) or ('options' in child and child['options'] == branch):
                    self.tree = originalTree
                    return
                self.findByChild(branch, child['childs'])

    def goTo(self, originalTree, branch):
        self.tree = originalTree[branch]
        return self.tree

    def updateTree(self, text, originalTree):
        # get the target branch
        for branch in originalTree:
            # find branch with the text
            if json.dumps(branch).lower().find(text) >= 0:
                if 'options' in branch:
                    self.tree = branch
                    return self.tree
                elif 'childs' in branch and json.dumps(branch['childs']).lower().find(text) >= 0:
                    return self.updateTree(text, branch['childs'])
                else:
                    self.tree = branch
                    return self.tree
