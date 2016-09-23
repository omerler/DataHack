import os
import pickle

import numpy as np
import pandas as pd

from sklearn.cross_validation import KFold
from sklearn.feature_selection import VarianceThreshold, RFE, SelectFromModel
from sklearn.preprocessing import normalize

from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import confusion_matrix, roc_auc_score, f1_score, precision_score, recall_score, accuracy_score

from constants import DIR

SEED = 7126

data = pd.read_csv(os.path.join(DIR, 'dataset.csv')).fillna(-1)
X = data.values[:, 1:]
y = data.values[:, 0]
print X.shape, y.shape
n = len(X)

def specificity_score(y_true, y_pred, *args, **kwargs):
    return recall_score(y_true == 0, y_pred == 0, *args, **kwargs)

def calc_scores(y_true, y_pred):
    return [roc_auc_score(y_true, y_pred)] + [matric_func(y_true, y_pred) for matric_func in METRIC_FUNCS]

def format_scores(scores):
    return ', '.join(['%s = %f' % metric_tuple for metric_tuple in zip(METRIC_NAMES, scores)])
    
METRICS = [
    ('F1', f1_score),
    ('Precision', precision_score),
    ('Recall', recall_score),
    ('Specificity', specificity_score),
    ('Accuracy', accuracy_score),
]

METRIC_NAMES, METRIC_FUNCS= zip(*METRICS)
METRIC_NAMES = ['AUC'] + list(METRIC_NAMES)

np.random.seed(SEED)

kf = KFold(n, shuffle = True, random_state = SEED, n_folds = 3)
model = RandomForestClassifier(n_estimators = 100, min_samples_split = 60, min_samples_leaf = 35, max_features = 0.15, \
        n_jobs = -1, class_weight = 'balanced', random_state = SEED)
        
all_test_scores = []

print '-' * 50
        
for train_index, test_index in kf:

    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    print 'KFold train_size = %d, test_size = %d' % (len(y_train), len(y_test))

    model.fit(X_train, y_train)
    y_pred_train = model.predict(X_train)
    print 'Training confusion matrix:'
    print confusion_matrix(y_train, y_pred_train)
    print 'Training scores: ' + format_scores(calc_scores(y_train, y_pred_train))
    
    y_pred_test = model.predict(X_test)
    print 'Test confusion matrix:'
    print confusion_matrix(y_test, y_pred_test)
    test_scores = calc_scores(y_test, y_pred_test)
    print 'Test scores: ' + format_scores(test_scores)
    all_test_scores += [test_scores]

    print '*' * 50
    
avg_test_scores = tuple(np.mean(np.array(all_test_scores), axis = 0))
print 'Average test scores: ' + format_scores(avg_test_scores)

model.fit(X, y)

with open(os.path.join(DIR, 'model.pkl'), 'wb') as f:
    pickle.dump(model, f)

print 'Done.'
