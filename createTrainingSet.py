import os, sys, csv
from collections import defaultdict
from parsingMethods import extract_methods
from stackoverflow import get_posts
from semantics import extract_feature_vector


def write_dataset_record(csv_writer, feature_vector, label):
    csv_writer.writerow(map(str, [label] + feature_vector))


if __name__ == "__main__":

    input_file = os.path.join(sys.argv[1], sys.argv[2])
    output_file = os.path.join(sys.argv[1], sys.argv[3])

    with open(output_file, 'w') as output_file:
        methods_per_posts = defaultdict(list)
        csv_writer = csv.writer(output_file)

        # TODO do something with duplicates

        prev_post = None
        for post in get_posts(input_file):
            for answer in post.answers:
                for method in extract_methods(answer.content):
                    feature_positive_vector = extract_feature_vector(method, post, answer)
                    write_dataset_record(csv_writer, feature_positive_vector, label = 1)
                    if prev_post is not None:
                        feature_negative_vector = extract_feature_vector(method, prev_post, answer)
                        write_dataset_record(csv_writer, feature_negative_vector, label = 0)
                    methods_per_posts[post] += [method]
            prev_post = post

        all_posts_with_methods = list(methods_per_posts.keys())
