import os
import sys
import json
import operator
import javalang
import pickle

import numpy as np

from constants import DIR, FILTERED_POSTS
from stackoverflow import get_posts
from parsingMethods import parse_method
from semantics import extract_feature_vector
from createTrainingSet import get_method_tokens, get_post_tokens, hueristic_filter

sys.argv = [None, 'public static Session getConnection(){}'] # XXX

with open(os.path.join(DIR, 'model.pkl'), 'r') as f:
    model = pickle.load(f)

def getMethod(userMethodSignature):
    userMethodSignature = "public class module {\n" + userMethodSignature + "\n}"
    tree = javalang.parse.parse(userMethodSignature)
    for path, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            method = parse_method(node)
            return method

def findHueristic(method):
    
    nearestPost = []
    method_tokens = get_method_tokens(method)
    
    for i, post in enumerate(get_posts(FILTERED_POSTS)):
    
        post_tokens = get_post_tokens(post)
    
        if hueristic_filter(method_tokens, post_tokens):
            nearestPost.append(post)
        
        if i % 10000 == 0:
            print 'Processed %d posts' % i
        
        # XXX
        if i > 20000:
            break
    
    return nearestPost

def secondSort(nearestPost, method):
    postsDict = {}
    for post in nearestPost:
        features = np.array([extract_feature_vector(method, post)])
        features[np.isnan(features)] = -1
        prob = model.predict_proba(features)[0][1]
        postsDict[post.title] = prob
    return sorted(postsDict.items(), key=operator.itemgetter(1), reverse=True)[:20]

def manager(userMethodSignature):
    method = getMethod(userMethodSignature)
    nearestPosts = findHueristic(method)
    print 'Preliminary filter: %d' % len(nearestPosts)
    return secondSort(nearestPosts, method)
    
if __name__ == '__main__':
    userMethodSignature = ' '.join(sys.argv[1:])
    best_posts = manager(userMethodSignature)
    print '\n'.join(['[%f] %s' % (prob, post_title) for post_title, prob in best_posts])
