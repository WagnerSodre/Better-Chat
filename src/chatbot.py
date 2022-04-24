import nltk
import json
import re
import random
import string # to process standard python strings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data.userFunctions import UserFunctions

from src.treeNavigation import TreeNavigation
from src.functions import Functions

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "hi there", "hello"]

class Chatbot():
    def __init__(self, botData):
        super().__init__()
        self.botData = botData
        text = json.dumps(botData['tree']['start'])
        self.tree = botData['tree']['start']
        self.userFunctions = UserFunctions()
        self.functions = Functions()
        self.treeNavigation = TreeNavigation(botData, self.tree)
        start =  getattr(self.userFunctions, 'start')()
        globals().update(start)
        text=text.lower()# converts to lowercase
        nltk.download('punkt') # first-time use only
        nltk.download('wordnet') # first-time use only
        self.sent_tokens = nltk.sent_tokenize(text, botData['language'])# converts to list of sentences 
        self.word_tokens = nltk.word_tokenize(text, botData['language'])# converts to list of word

        self.lemmer = nltk.stem.WordNetLemmatizer()
        self.remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

    def LemTokens(self, tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]

    def LemNormalize(self, text):
        return self.LemTokens(nltk.word_tokenize(text.lower().translate(self.remove_punct_dict)))

    # Checking for greetings
    def greeting(self, sentence):
        """If user's input is a greeting, return a greeting response"""
        for word in sentence.split():
            if word.lower() in GREETING_INPUTS:
                return random.choice(GREETING_RESPONSES)

    def updateSentTokens(self, updateType, user_response):
        if updateType == 'append':
            self.sent_tokens.append(user_response)
        elif updateType == 'remove':
            self.sent_tokens.remove(user_response)

    # Generating response
    def generateResponse(self, user_response, tree):
        robo_response=''
        TfidfVec = TfidfVectorizer(tokenizer=self.LemNormalize, stop_words=self.botData['language'])
        tfidf = TfidfVec.fit_transform(self.sent_tokens)
        vals = cosine_similarity(tfidf[-1], tfidf)
        idx=vals.argsort()[0][-2]
        flat = vals.flatten()
        flat.sort()
        req_tfidf = flat[-1]
        self.sent_tokens[idx] = re.sub(r'^.*?{"name"', '{"name"', self.sent_tokens[idx])
        self.sent_tokens[idx] = self.sent_tokens[idx][0:50]
        tree = self.treeNavigation.updateTree(self.sent_tokens[idx], tree)
        if(req_tfidf==0):
            if tree != self.botData['tree']['start']:
                res = self.treeNavigation.retry(self.sent_tokens[idx])
                robo_response = robo_response+res
            else:
                robo_response="I am sorry! I don't understand you"
            return robo_response
        else:
            if 'function' in tree:
                functionsOutput = self.functions.execFunction(tree['function'], tree, globals())
                tree['answer'] = functionsOutput['answer']
                globals().update(functionsOutput['vars'])
            if 'answer' in tree:
                robo_response = robo_response+tree['answer']
            elif 'answerNull' in tree:
                robo_response = robo_response+tree['answerNull']
            elif tree != self.botData['tree']['start']:
                res = self.treeNavigation.retry(self.sent_tokens[idx])
                print(self.sent_tokens[idx])
                robo_response = robo_response+res
            if 'childs' in tree:
                tree = self.treeNavigation.goTo(tree, 'childs')
            elif 'options' in tree:
                tree = self.treeNavigation.goTo(tree, 'options')
            else:
                if robo_response != "I am sorry! I don't understand you":
                    robo_response = robo_response+'\nCan I help you with anything else?'
                    tree = self.treeNavigation.resetTree()
            return {'tree': tree, 'answer': robo_response+'\nYou: '}

    def getResponse(self, user_response):
        self.sent_tokens.append(user_response)
        self.word_tokens=self.word_tokens+nltk.word_tokenize(user_response)
        final_words=list(set(self.word_tokens))
        print(self.botData['name']+": ",end="")
        response = self.generateResponse(user_response, self.tree)
        self.tree = response['tree']
        print(response['answer'])
        self.sent_tokens.remove(user_response)