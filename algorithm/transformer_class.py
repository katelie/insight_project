from sklearn.base import BaseEstimator, TransformerMixin
import string


class AnalyzeSentiment(BaseEstimator, TransformerMixin):

    def __init__(self, stopwords=None, punct=None,
                 lower=True, strip=True):
        self.lower      = lower
        self.strip      = strip
        self.stopwords  = mystops
        self.punct      = punct or set(string.punctuation)

    def fit(self, X, y):
        return self

    def inverse_transform(self, X):
        return [" ".join(doc) for doc in X]

    def transform(self, X):
        return [
            list(self.tokenize(doc)) for doc in X
        ]
    
    def tokenize(self, X, y):
        return self

    def sent_value(self, sentence):      
        sentiment = SentimentIntensityAnalyzer().polarity_scores(sentence).values()
        yield np.array(list(sentiment))
#         SentimentIntensityAnalyzer().polarity_scores(mysentence).values()