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

    def toStr(self):
        str(self.id, )


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


if __name__ == "__main__":
    input_file = os.path.join(sys.argv[1], sys.argv[2])

    with open(input_file, 'r') as input:
        for record in input:
            answers = []
            for answer in record['answers']:
                answers.append(StackOverflowMessage(answer['Id'], answer['Body'], answer['Score']))
            question = StackOverflowMessage(record['Id'], record['Body'], record['Score'])
            post = StackOverflowPost(record['Title'], record['Tags'], record['FavoriteCount'], question, answers)
            print json.dumps(post.to)
