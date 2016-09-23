from parsingMethods import *
from semantics import *
import json
from stackoverflow import get_posts
import operator

import javalang

def getMethod(userMethodSignature):
    try:
        userMethodSignature = "public class module {\n" + userMethodSignature + "\n}"
        tree = javalang.parse.parse(userMethodSignature)
        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                method = parse_method(node)
                return method
        return None
    except:
        return None

def getMethodTokens(method):
    method_name_tokens = get_tokens_frequency_of_text(method.name)
    method_arg_name_tokens = get_tokens_frequency([argument.name for argument in method.arguments])
    method_arg_type_tokens = get_tokens_frequency([argument.type for argument in method.arguments])
    method_return_type_token = {method.return_type: 1.0}
    return method_name_tokens, method_arg_name_tokens, \
           method_arg_type_tokens, method_return_type_token


def findHueristic(userMethodSignature):
    nearestPost = []
    userTokens = set(getMethodTokens(userMethodSignature))
    for post in get_posts(constants.FILTERED_POSTS):
        if set(tokenize_text(post.title)) & userTokens > 0 and \
            set(tokenize_text(get_stackoverflow_message_text(post.question))) \
                        & userTokens  > 1\
            and set.union([tokenize_text(get_stackoverflow_message_text(
                    answer)) for answer in post.answers]) & userTokens > 1:
            nearestPost.append(post)
    print (len(nearestPost)) ###
    return nearestPost

def secondSort(nearestPost, method):
    postsDict = {}
    for post in nearestPost:
        num = predict_proba(extract_feature_vector(method, post)) ###
        postsDict[post] = num
    return sorted(postsDict.items(), key=operator.itemgetter(1), reverse=True)[:10]


def manager(userMethodSignature):
    method = getMethod(userMethodSignature)
    if not method:
        return "problem with method syntax"
    nearestPosts = findHueristic(userMethodSignature)
    return secondSort(nearestPosts, method)





