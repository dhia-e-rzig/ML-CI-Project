import pandas as pd
import sklearn.model_selection

from sklearn import metrics
from sklearn.ensemble._hist_gradient_boosting.common import X_BINNED_DTYPE
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB

import numpy as np

from sklearn.linear_model import SGDClassifier
#
# data = []
#
# test_data=[]

data = pd.read_csv('data_for_training.csv', header=0, names=['Text', 'Class'],encoding ='utf-8')

# test_data = pd.read_csv('test_data.csv', header=0, names=['Text','Class'],encoding ='utf-8')
print(data.columns)
# exit()

X_train,X_test,Y_train,Y_test=sklearn.model_selection.train_test_split(data['Text'],data['Class'], random_state=12)

text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(2,2))), ('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-6, random_state=42,max_iter=100, tol=None))])
# text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(2,2))), ('clf', MultiNomialNB())])
# text_clf = Pipeline([('vect', CountVectorizer(min_df=10, encoding='latin-1', ngram_range=(1, 2), stop_words='english')),('tfidf', TfidfTransformer()), ('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, random_state=42,max_iter=5, tol=None))])

# print(X_train)
# print(Y_train)
# exit()
text_clf.fit(X_train, Y_train)

predicted = text_clf.predict(X_test)

for prediction in zip(predicted):
    print('%s' % (prediction))

print(np.mean(predicted == Y_test))


from sklearn.feature_extraction.text import TfidfVectorizer

tfidfconvert = TfidfVectorizer(ngram_range=(2,2)).fit(X_train)

X_transformed=tfidfconvert.transform(X_train)
# print(tfidfconvert.get_feature_names())

# exit()
# Clustering the training sentences with K-means technique

from sklearn.cluster import KMeans
modelkmeans = KMeans(n_clusters=2, random_state=0)
modelkmeans.fit(X_transformed)

X_transformed=tfidfconvert.transform(X_test)

predicted=modelkmeans.predict(X_transformed)
for i in range(0,  len(predicted)):
    print(X_test.to_list()[i])
    print(predicted[i])

print(np.mean(predicted == Y_test))

print('s')
