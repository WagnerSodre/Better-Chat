import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import json
import re
import numpy as np
import random
import string # to process standard python strings

import functions

#reference: https://medium.com/@ritidass29/create-your-chatbot-using-python-nltk-88809fa621d1

#TODO: Filtrar oque vai ser lido do json como text, Executar funções no JSON, Implementar análise de sentimentos

sa = SentimentIntensityAnalyzer()

score = [(tok, score) for tok, score in sa.lexicon.items() if " " in tok]

with open('bot.json') as json_file:
    botData = json.load(json_file)

text = json.dumps(botData['tree']['start'])
start =  getattr(functions, 'start')()
globals().update(start)
tree = botData['tree']['start']
text=text.lower()# converts to lowercase
nltk.download('punkt') # first-time use only
nltk.download('wordnet') # first-time use only
sent_tokens = nltk.sent_tokenize(text, botData['language'])# converts to list of sentences 
word_tokens = nltk.word_tokenize(text, botData['language'])# converts to list of word

lemmer = nltk.stem.WordNetLemmatizer()
def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)
GREETING_RESPONSES = ["hi", "hey", "hi there", "hello"]


# Checking for greetings
def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Generating response
def response(user_response):
    robo_response=''
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words=botData['language'])
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-1]
    sent_tokens[idx] = re.sub(r'^.*?{"name"', '{"name"', sent_tokens[idx])
    sent_tokens[idx] = sent_tokens[idx][0:50]
    updateTree(sent_tokens[idx], tree)
    if(req_tfidf==0):
        if tree != botData['tree']['start']:
            res = retry(sent_tokens[idx])
            robo_response = robo_response+res
        else:
            robo_response="I am sorry! I don't understand you"
        return robo_response
    else:
        if 'function' in tree:
            execFunction(tree['function'])
        if 'answer' in tree:
            robo_response = robo_response+tree['answer']
        elif 'answerNull' in tree:
            robo_response = robo_response+tree['answerNull']
        elif tree != botData['tree']['start']:
            res = retry(sent_tokens[idx])
            print(sent_tokens[idx])
            robo_response = robo_response+res
        if 'childs' in tree:
            goTo(tree, 'childs')
        elif 'options' in tree:
            goTo(tree, 'options')
        else:
            if robo_response != "I am sorry! I don't understand you":
                robo_response = robo_response+'\nCan I help you with anything else?'
                resetTree()
        return robo_response+'\nYou: '

def execFunction(function):
    functionName = function.split('(')[0]
    if functionName not in globals():
        varsToReplace = re.search('{{(.*)}}', function)
        varsValue = []
        for i in range(len(varsToReplace.groups())):
            varsValue.append(globals()[varsToReplace.group(i).replace('{{', '').replace('}}', '')])
        functionValue =  getattr(functions, functionName)(*varsValue)
        globals().update({functionName: functionValue})
    print(tree)
    if 'answer' in tree:
        tree['answer'] = tree['answer'].replace('{{'+functionName+'}}', globals()[functionName])

def resetTree():
    global tree
    tree = botData['tree']['start']

def retry(target):
    temp = tree
    resetTree()
    findByChild(temp, tree)
    updateTree(target, tree)
    if 'answer' in tree:
        return tree['answer']
    elif 'answerNull' in tree:
        return tree['answerNull']
    elif tree != botData['tree']['start']:
        return retry(target)
    else:
       return "I am sorry! I don't understand you"

def findByChild(branch, originalTree):
    for child in originalTree:
        if json.dumps(child).lower().find(json.dumps(branch).lower()) >= 0:
            if ('childs' in child and child['childs'] == branch) or ('options' in child and child['options'] == branch):
                global tree
                tree = originalTree
                return
            findByChild(branch, child['childs'])

def goTo(originalTree, branch):
    global tree
    tree = originalTree[branch]

def updateTree(text, originalTree):
    global tree
    # get the target branch
    for branch in originalTree:
        # find branch with the text
        if json.dumps(branch).lower().find(text) >= 0:
            if 'options' in branch:
                tree = branch
            elif 'childs' in branch and json.dumps(branch['childs']).lower().find(text) >= 0:
                updateTree(text, branch['childs'])
            else:
                tree = branch

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
            if(greeting(user_response) != None):
                print(botData['name']+": "+greeting(user_response))
            else:
                sent_tokens.append(user_response)
                word_tokens=word_tokens+nltk.word_tokenize(user_response)
                final_words=list(set(word_tokens))
                print(botData['name']+": ",end="")
                print(response(user_response))
                sent_tokens.remove(user_response)
    else:
        flag=False
        print(botData['name']+": Bye! take care..")    