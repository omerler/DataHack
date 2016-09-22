import re, os, sys
from stackoverflow import get_posts

DELIMITER_TOKEN = '$$$'

def tokenize_word(raw_word):
    '''
    Handles Camel Case.
    '''
    tokens = []
    last_lower = False
    for i, c in enumerate(raw_word):
        if i == 0 or (c.isupper() and last_lower):
            tokens += [c.lower()]
        else:
            tokens[-1] += c.lower()
        last_lower = c.islower()
    return tokens

def tokenize_text(raw_text):
    return [token for word in re.split('[^a-zA-Z]+', raw_text) for token in tokenize_word(word)]

def write_tokens(output_file, raw_text):
    tokens = tokenize_text(raw_text)
    output_file.write(' ' + ' '.join(tokens + [DELIMITER_TOKEN]))


def get_stackoverflow_message_text(message):
    return ' '.join([element_content for element_type, element_content in message.content])


if __name__ == "__main__":
    
    input_file = os.path.join(sys.argv[1], sys.argv[2])
    output_file = os.path.join(sys.argv[1], sys.argv[3])

    with open(output_file, 'w') as output_file:

        output_file.write(DELIMITER_TOKEN)

        for i, post in enumerate(get_posts(input_file)):
            post_texts = [post.title] + [get_stackoverflow_message_text(
                post.question)] + [get_stackoverflow_message_text(answer) for answer in post.answers]
            for text in post_texts:
                write_tokens(output_file, text)
            if i % 1000 == 0:
                print 'Post %d' % i
