from collections import defaultdict
import csv

class Argument(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Method(object):
    def __init__(self, name, return_type, arguments):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments

class StackOverflowMessage(object):
    def __init__(self, content, votes, favorites):
        '''
        content is a list of Code or Text elements.
        '''
        
class StackOverflowPost(object):
    def __init__(self, title, tags, question, answers)
        '''
        title - string
        tags - list of strings
        question - StackOverflowMessage
        answers - list of StackOverflowMessage
        '''

def extract_feature_vector(method, post, answer = None):
    '''
    Will ignore answer in the post.
    '''
    distance_between_method_name_to_post_title = ...
    distance_between_method_name_to_post_question = ...
    return [distance_between_method_name_to_post_title, distance_between_method_name_to_post_question, post.question.votes, ...]
        
def write_dataset_record(csv_writer, feature_vector, label):
    csv_writer.writerow(map(str, [label] + feature_vector))
        
def create_training_set(posts):
    with open(TRAINING_SET_FILEPATH, 'w') as output_file:
        
        methods_per_posts = defaultdict(list)
        csv_writer = csv.writer(output_file)
        
        # TODO do something with duplicates

        for post in posts:
            for answer in post.answers:
                for method in extract_methods(answer.content):
                    if is_legitimate_method(method): # e.g. not main
                        feature_vector = extract_feature_vector(method, post, answer)
                        write_dataset_record(csv_writer, feature_vector, label = 1)
                        methods_per_posts[post] += [method]
                        
        all_posts_with_methods = list(methods_per_posts.keys())
                    
        for _ in xrange(total_positive_records):
            
            reference_post_index = random.randint(0, len(all_posts_with_methods) - 1)
            method_post_index = None
            while method_post_index is not None and method_post_index != reference_post_index:
                method_post_index = random.randint(0, len(all_posts_with_methods) - 1)
            
            post = all_posts_with_methods[reference_post_index]
            method = random.choice(methods_per_posts[all_posts_with_methods[method_post_index]])
            feature_vector = extract_feature_vector(method, post) # TODO maybe add a dummy answer to ignore
            write_dataset_record(csv_writer, feature_vector, label = 0)
        