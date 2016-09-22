from collections import defaultdict
import csv, sys, json, os
import random


class StackOverflowMessage(object):
    def __init__(self, id, content, votes):
        '''
        content is a list of Code or Text elements.
        '''
        self.id = id
        self.content = content
        self.votes = votes

    def to_dict(self):
        return {'id': self.id, 'content': self.content, 'votes':
            self.votes}


class StackOverflowPost(object):
    def __init__(self, title, tags, favorites, question, answers):
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
        self.favorites = favorites

    def to_dict(self):
        answers = []
        for message in self.answers:
            answers.append(message.to_dict())
        return json.dumps({'title': self.title, 'tags': self.tags,
                           'favorites': self.favorites, 'question':
                               self.question.to_dict(), 'answers': answers})


def get_posts(input_file):
    posts = []

    with open(input_file, 'r') as input:
        for raw_record in input:
            record = json.loads(raw_record)
            answers = []
            for ans in record['answers']:
                answers.append(StackOverflowMessage(ans['Id'], ans['Body'], ans['Score']))
            question = StackOverflowMessage(record['Id'], record['Body'], record['Score'])
            posts.append(StackOverflowPost(record['Title'], record['Tags'],
                                      record['FavoriteCount'], question,
                                           answers))
            # print json.dumps(post.to_dict())

    return posts
