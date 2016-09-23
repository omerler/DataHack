import os
import sys
import json
import operator
import javalang
import pickle

import numpy as np

from stackoverflow import get_posts
from parsingMethods import *
from semantics import *
from constants import DIR

sys.argv = [None, 'public static JButton createButton(Graphics graphics){}'] # XXX

with open(os.path.join(DIR, 'model.pkl'), 'r') as f:
    model = pickle.load(f)

def getMethod(userMethodSignature):
    userMethodSignature = "public class module {\n" + userMethodSignature + "\n}"
    tree = javalang.parse.parse(userMethodSignature)
    for path, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            method = parse_method(node)
            return method

def getMethodTokens(method):
    method_name_tokens = get_tokens_frequency_of_text(method.name)
    method_arg_name_tokens = get_tokens_frequency([argument.name for argument in method.arguments])
    method_arg_type_tokens = get_tokens_frequency([argument.type for argument in method.arguments])
    method_return_type_token = {method.return_type: 1.0}
    return set(method_name_tokens) | set(method_arg_name_tokens) | set(method_arg_type_tokens) | set(method_return_type_token)

def findHueristic(method):
    
    nearestPost = []
    userTokens = set(getMethodTokens(method))
    
    for i, post in enumerate(get_posts(constants.FILTERED_POSTS)):
    
        title_shared_tokens = len(set(tokenize_text(post.title)) & userTokens)
        question_shared_tokens = len(set(tokenize_text(get_stackoverflow_message_text(post.question))) & userTokens)
        answers_shared_tokens = len(set.union(*[set(tokenize_text(get_stackoverflow_message_text(answer))) for answer in post.answers]) & userTokens)
        
        if title_shared_tokens > 0 and question_shared_tokens > 0 and answers_shared_tokens > 1:
            nearestPost.append(post)
        
        if i % 10000 == 0:
            print 'Processed %d posts' % i
        
        # XXX
        if i > 10000:
            break
    
    print len(nearestPost) # XXX
    return nearestPost

def secondSort(nearestPost, method):
    postsDict = {}
    for post in nearestPost:
        features = np.array([extract_feature_vector(method, post)])
        features[np.isnan(features)] = -1
        prob = model.predict_proba(features)[0][1]
        postsDict[post.title] = prob
    return sorted(postsDict.items(), key=operator.itemgetter(1), reverse=True)#[:10]

def manager(userMethodSignature):
    method = getMethod(userMethodSignature)
    nearestPosts = findHueristic(method)
    return secondSort(nearestPosts, method)
    
if __name__ == '__main__':
    userMethodSignature = ' '.join(sys.argv[1:])
    best_posts = manager(userMethodSignature)
    print '\n'.join(['[%f] %s' % (prob, post_title) for post_title, prob in best_posts])
