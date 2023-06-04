from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# procedimento que exibe a pontuação do dicionário de palavras
sa = SentimentIntensityAnalyzer()
# print(sa.lexicon)

# procedimento que exibe a pontuação de palavras com espaço " "
score = [(tok, score) for tok, score in sa.lexicon.items() if " " in tok]
# print(score)

# print(sa.polarity_scores(text="Python is very readable and it's great for NLP."))

# print(sa.polarity_scores(text="Python is not a bad choice for most applications."))

corpus = ["Absolutely perfect! Love it! :-) :-) :-)", "Horrible! Completely useless. :(", "It was OK. Some good and some bad things."]

for doc in corpus:
    scores = sa.polarity_scores(doc)
    #('{:+}: {}'.format(scores['compound'], doc))

