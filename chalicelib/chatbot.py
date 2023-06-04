# -*- coding: utf-8 -*-
import nltk
import json
import re
import random
import string # to process standard python strings

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from googletrans import Translator

from chalicelib.data.userFunctions import UserFunctions

from chalicelib.treeNavigation import TreeNavigation
from chalicelib.functions import Functions

nltk.data.path.append("/var/task/chalicelib/nltk_data")

GREETING_INPUTS = ("olá", "oi", "saudações", "eai", "como vai","hey",)
GREETING_RESPONSES = ["oi", "olá"]
NEGATIVE_INPUTS = ["não", "negativo"]
POSITIVE_INPUTS = ["sim", "positivo"]
SENTIMENT_EXCLUSION_INPUTS = ["reclamar", "reclame", "reclama", "reclamação", "denuncia", "denuncie", "denuncia"]

class Chatbot():
    def __init__(self, botData, instance):
        if instance:
            super().__init__()
            for key in instance['self']:
                setattr(self, key, instance['self'][key])
            globals().update(instance['globals'])
            self.lemmer = nltk.stem.WordNetLemmatizer()
            self.userFunctions = UserFunctions()
            self.functions = Functions()
            self.treeNavigation = TreeNavigation(self.botData , self.tree)
            text = json.dumps(self.botData['tree']['start'])
            self.sent_tokens = nltk.sent_tokenize(text, self.botData['language'])# converts to list of sentences 
            self.word_tokens = nltk.word_tokenize(text, self.botData['language'])# converts to list of word
        else:
            super().__init__()
            self.userHistory = []
            self.botData = botData
            text = json.dumps(self.botData['tree']['start'])
            self.tree = self.botData['tree']['start']
            self.saveAnswer = None
            self.userFunctions = UserFunctions()
            self.functions = Functions()
            self.treeNavigation = TreeNavigation(self.botData , self.tree)
            start =  getattr(self.userFunctions, 'start')()
            globals().update(start)
            text=text.lower()# converts to lowercase
            self.sent_tokens = nltk.sent_tokenize(text, self.botData['language'])# converts to list of sentences 
            self.word_tokens = nltk.word_tokenize(text, self.botData['language'])# converts to list of word

            self.lemmer = nltk.stem.WordNetLemmatizer()
            self.remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

    def LemTokens(self, tokens):
        return [self.lemmer.lemmatize(token) for token in tokens]

    def LemNormalize(self, text):
        return self.LemTokens(nltk.word_tokenize(text.lower().translate(self.remove_punct_dict)))

    # Checking for greetings
    def greeting(self, sentence):
        """If user's input is a greeting, return a greeting response"""
        if sentence in GREETING_INPUTS:
            return f"{random.choice(GREETING_RESPONSES)}, meu nome é {self.botData['name']}, como posso te ajudar?"

    def updateSentTokens(self, updateType, user_response):
        if updateType == 'append':
            self.sent_tokens.append(user_response)
        elif updateType == 'remove':
            self.sent_tokens.remove(user_response)

    # Generating response
    def generateResponse(self, go_back, tree, user_response):
        print(tree)
        robo_response=''
        if 'stopwords' in self.botData:
            stopwords = self.botData['stopwords']
        else:
            stopwords = self.botData['language']
        alreadyFound = False

        if len(tree) == 1:
            tree = tree[0]
            alreadyFound = True
        else:
            tags = []
            for option in tree:
                tags = option["tags"].split(", ")
                for word in user_response.lower().split(" "):
                    if word in tags:
                        tree = option
                        alreadyFound = True
        if not alreadyFound:
            TfidfVec = TfidfVectorizer(tokenizer=self.LemNormalize, stop_words=stopwords)
            tfidf = TfidfVec.fit_transform(self.sent_tokens)
            vals = cosine_similarity(tfidf[-1], tfidf)
            flat = vals.flatten()
            flat.sort()
            req_tfidf = flat[-1]
            matches = []
            for index, match in enumerate(vals.argsort()[0][::-1]):
                if index > 0:  
                    self.sent_tokens[match] = re.sub(r'^.*?{"name"', '{"name"', self.sent_tokens[match])
                    self.sent_tokens[match] = self.sent_tokens[match][0:50]
                    if self.sent_tokens[match] not in matches:
                        matches.append(self.sent_tokens[match])
            if go_back:
                match = matches[1]
            else:
                match = matches[0]
            tree = self.treeNavigation.updateTree(match, tree)
            if tree == None:
                robo_response="Me desculpe, eu não te entendi."
                return {'tree': self.botData['tree']['start'], 'saveAnswer': None, 'answer': robo_response}
            if(req_tfidf==0):
                if tree != self.botData['tree']['start']:
                    res = self.treeNavigation.retry(match)
                    robo_response = robo_response+res
                else:
                    robo_response="Me desculpe, eu não te entendi."
                return {'tree': tree, 'saveAnswer': None, 'answer': robo_response}
        else:
            if 'saveAnswer' in tree:
                if tree['saveAnswer'] in globals():
                    saveAnswer = None
                    temp_tree = tree.copy()
                    print(temp_tree)
                    while 'childs' in temp_tree:
                        temp_tree = temp_tree['childs'][0]
                    functionsOutput = self.functions.execFunction(temp_tree['function'], temp_tree, globals())
                    if functionsOutput['vars']:
                        tree = temp_tree
                    else:
                        saveAnswer = tree['saveAnswer']
                else:
                    saveAnswer = tree['saveAnswer']
            else:
                saveAnswer = None
            if 'function' in tree:
                print('executing function')
                functionsOutput = self.functions.execFunction(tree['function'], tree, globals())
                print('function results: ', functionsOutput)
                tree['answer'] = functionsOutput['answer']
                if functionsOutput['vars']:
                    globals().update(functionsOutput['vars'])
            if 'answer' in tree:
                robo_response = robo_response+tree['answer']
            elif 'answerNull' in tree:
                robo_response = robo_response+tree['answerNull']
            elif tree != self.botData['tree']['start']:
                res = self.treeNavigation.retry(match)
                robo_response = robo_response+res
            if 'childs' in tree:
                tree = self.treeNavigation.goTo(tree, 'childs')
            elif 'options' in tree:
                tree = self.treeNavigation.goTo(tree, 'options')
            else:
                if robo_response != "Me desculpe, eu não te entendi.":
                    robo_response = robo_response+'\nPosso te ajudar com algo mais?'
                    tree = self.treeNavigation.resetTree()
            return {'tree': tree, 'saveAnswer': saveAnswer, 'answer': robo_response}

    def getResponse(self, user_response):
        print('getResponse tree')
        print(self.tree)
        if 'não consegui' in user_response:
            return {"message": "Vou te encaminhar para um atendente humano para atender melhor sua demanda.", "negativity": False}
        if 'positiveAnswer' in self.tree and user_response.lower() in POSITIVE_INPUTS:
            self.tree = self.tree['positiveAnswer']
            return {"message": self.tree['answer'], "negativity": False}
        if 'negativeAnswer' in self.tree and user_response.lower() in NEGATIVE_INPUTS:
            self.tree = self.tree['negativeAnswer']
            return {"message": self.tree['answer'], "negativity": False}
        self.userHistory.append(user_response)
        sentimentDecision = self.sentimentDecision(user_response)
        print(sentimentDecision)
        if sentimentDecision["quit"] == True:
            return {"message": sentimentDecision["user_response"], "negativity": True}
        if sentimentDecision["go_back"]:
            print("!!!!!!!!!!! GOING BACK !!!!!!!!!!!!!!!!!")
            user_response = sentimentDecision["user_response"]
        print(user_response)
        if self.saveAnswer:
            globals().update({self.saveAnswer: user_response})
            self.saveAnswer = None
        if 'saveAnswer' in self.tree:
            if self.tree['saveAnswer'] not in globals():
                globals().update({self.tree['saveAnswer']: user_response})
                self.tree = self.tree['childs'][0]
                self.tree['answer'] = self.tree['answer']+'\nPosso te ajudar com algo mais?'
                return {"message": self.tree['answer'], "negativity": False}
        self.sent_tokens.append(user_response)
        self.word_tokens=self.word_tokens+nltk.word_tokenize(user_response)
        #final_words=list(set(self.word_tokens))
        response = self.generateResponse(sentimentDecision["go_back"], self.tree, user_response)
        print('---------------------------')
        print(response)
        self.saveAnswer = response['saveAnswer']
        self.tree = response['tree']
        self.sent_tokens.remove(user_response)
        return {"message": response['answer'], "negativity": False}

    def sentimentDecision(self, user_response):
        for word in user_response.lower().split(" "):
            if word in SENTIMENT_EXCLUSION_INPUTS:
                return {"user_response": user_response, "go_back": False, "quit": False}
        sa = SentimentIntensityAnalyzer()
        #score = [(tok, score) for tok, score in sa.lexicon.items() if " " in tok]
        #if user_response.lower() not in NEGATIVE_INPUTS and self.tree != self.botData['tree']['start']:
        if self.botData['language'] != 'english':
            translator = Translator()
            user_response = translator.translate(user_response, src='pt', dest='en').text
        scores = sa.polarity_scores(user_response)['compound']
        print('score sentimento: ', scores)
        #print('Sentiment: ', scores)
        if scores < -0.3:
            self.tree = self.botData['tree']['start']
            return {"user_response": "Enviando para atendente humano...", "go_back": False, "quit": True}
        elif scores < -0.05:
            self.tree = self.botData['tree']['start']
            if (len(self.userHistory) > 2):
                user_response = self.userHistory[-2]
            return {"user_response": user_response, "go_back": True, "quit": False}
        else:
            return {"user_response": user_response, "go_back": False, "quit": False}

    def export(self):
        instance = {}
        instance['self'] = self.__dict__
        del instance['self']['sent_tokens']
        del instance['self']['word_tokens']
        del instance['self']['lemmer']
        del instance['self']['userFunctions']
        del instance['self']['functions']
        del instance['self']['treeNavigation']
        del self
        instance['globals'] = {}
        g = globals()
        for key, value in list(globals().items()):
            if isinstance(value, str):
                instance['globals'][key] = value
                del g[key]
        return instance