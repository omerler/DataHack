import os, sys, csv
from collections import defaultdict
from parsingMethods import extract_methods
from stackoverflow import get_posts
from semantics import extract_feature_vector, get_tokens_frequency_of_text, get_tokens_frequency, tokenize_text, get_stackoverflow_message_text

TOTAL_POSTS = 856000

def write_dataset_record(csv_writer, feature_vector, label):
    csv_writer.writerow(map(str, [label] + feature_vector))
    
def get_method_tokens(method):
    method_name_tokens = get_tokens_frequency_of_text(method.name)
    method_arg_name_tokens = get_tokens_frequency([argument.name for argument in method.arguments])
    method_arg_type_tokens = get_tokens_frequency([argument.type for argument in method.arguments])
    method_return_type_token = {method.return_type: 1.0}
    return set(method_name_tokens) | set(method_arg_name_tokens) | set(method_arg_type_tokens) | set(method_return_type_token)
    
def get_post_tokens(post):
    return set(tokenize_text(post.title)), set(tokenize_text(get_stackoverflow_message_text(post.question))), \
            set.union(*[set(tokenize_text(get_stackoverflow_message_text(answer))) for answer in post.answers])
            
def hueristic_filter(method_tokens, post_tokens):
    post_title_tokens, post_question_tokens, post_answers_tokens = post_tokens
    title_shared_tokens = len(post_title_tokens & method_tokens)
    question_shared_tokens = len(post_question_tokens & method_tokens)
    answers_shared_tokens = len(post_answers_tokens & method_tokens)
    return title_shared_tokens > 0 and question_shared_tokens > 0 and answers_shared_tokens > 1

if __name__ == "__main__":

    sys.argv = [None, 'C://downloads/code_project/', 'filtered_posts.json', 'dataset.csv'] # XXX

    input_file = os.path.join(sys.argv[1], sys.argv[2])
    output_file = os.path.join(sys.argv[1], sys.argv[3])

    with open(output_file, 'wb') as output_file:

        csv_writer = csv.writer(output_file)

        total_positive_features = 0
        total_negative_features = 0

        prev_posts = []
        
        for i, post in enumerate(get_posts(input_file)):
        
            post_tokens = get_post_tokens(post)
        
            if i % 100 == 0:
                print 'Processed %d posts [%d%%]' % (i, int(100.0 * float(i) / TOTAL_POSTS))
                print "total of positive features: %d" % total_positive_features
                print "total of negative features: %d" % total_negative_features
            
            for answer in post.answers:
                for method in extract_methods(answer.content):
                
                    if i % 100 == 0:
                        print "post: %s, answer: %s, method: %s" % (post.question.id, answer.id, method.name)
                
                    method_tokens = get_method_tokens(method)
                    
                    if hueristic_filter(method_tokens, post_tokens):
                        feature_positive_vector = extract_feature_vector(method, post, answer)
                        write_dataset_record(csv_writer, feature_positive_vector, label = 1)
                        total_positive_features += 1
                    
                    for prev_post, prev_post_tokens in prev_posts:
                        if hueristic_filter(method_tokens, prev_post_tokens):
                            feature_negative_vector = extract_feature_vector(method, prev_post)
                            write_dataset_record(csv_writer, feature_negative_vector, label = 0)
                            total_negative_features += 1
                            break

            prev_posts += [(post, post_tokens)]
            
            if len(prev_posts) > 1000:
                prev_posts.pop(0)