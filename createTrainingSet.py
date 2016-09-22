import os, sys, csv
from collections import defaultdict
from parsingMethods import extract_methods
from stackoverflow import get_posts
from semantics import extract_feature_vector

TOTAL_POSTS = 856000

def write_dataset_record(csv_writer, feature_vector, label):
    csv_writer.writerow(map(str, [label] + feature_vector))

if __name__ == "__main__":

    sys.argv = [None, 'C://downloads/code_project/', 'filtered_posts.json', 'dataset.csv'] # XXX

    input_file = os.path.join(sys.argv[1], sys.argv[2])
    output_file = os.path.join(sys.argv[1], sys.argv[3])

    with open(output_file, 'w') as output_file:

        csv_writer = csv.writer(output_file)

        total_positive_features = 0
        total_negative_features = 0

        prev_post = None
        for i, post in enumerate(get_posts(input_file)):
        
            if i % 1000 == 0:
                print 'Processed %d posts [%d%%]' % (i, int(100.0 * float(i) / TOTAL_POSTS))
            
            for answer in post.answers:
                for method in extract_methods(answer.content):
                    
                    print "post: %s, answer: %s, method: %s" % (post.question.id, answer.id, method.name)
                    feature_positive_vector = extract_feature_vector(method, post, answer)
                    write_dataset_record(csv_writer, feature_positive_vector, label = 1)
                    total_positive_features += 1
                    
                    if prev_post is not None:
                        print "post: %s, answer: %s, method: %s" % (prev_post.question.id, answer.id, method.name)
                        feature_negative_vector = extract_feature_vector(method, prev_post, answer)
                        write_dataset_record(csv_writer, feature_negative_vector, label = 0)
                        total_negative_features += 1

            prev_post = post

        print "total of positive features: %d" % total_positive_features
        print "total of negative features: %d" % total_negative_features