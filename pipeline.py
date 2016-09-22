from collections import defaultdict
import csv
import random

class StackOverflowMessage(object):
    def __init__(self, content, votes, favorites):
        '''
        content is a list of Code or Text elements.
        '''
        self.content = content
        self.votes = votes
        self.favorites = favorites

class StackOverflowPost(object):
    def __init__(self, title, tags, question, answers):
        '''
        title - string
        tags - list of strings
        question - StackOverflowMessage
        answers - list of StackOverflowMessage
        '''
        self.title = title
        self.tags = tags
        self.question = question
        self.answers = answers

