import os
import json
from collections import defaultdict, Counter
import constants

from create_corpus_tokens import DELIMITER_TOKEN

def cache(f):

    _cache = {}
    
    def _wraped(*args):
        
        if args not in _cache:
            _cache[args] = f(*args)
            
        return _cache[args]
    
    return _wraped

def read_tokens():

    BUFFER_SIZE = 10 ** 5

    with open(constants.GLOBAL_TOKENS, 'r') as f:
    
        token = ''
    
        while True:
        
            buffer = f.read(BUFFER_SIZE)
            
            if len(buffer) == 0:
                break
        
            for c in buffer:
                if c == ' ':
                    yield token
                    token = ''
                else:
                    token += c
                    
def create_token_freqs(min_occurances = 10):
    
    token_occurances = Counter()
    
    for token in read_tokens():
        if token != DELIMITER_TOKEN:
            token_occurances[token] += 1
    
    all_tokens = len(token_occurances)
    token_occurances = {token: occurances for token, occurances in token_occurances.items() if occurances >= min_occurances}
    remained_tokens = len(token_occurances)
    
    print 'Filtered %d of %d tokens.' % (remained_tokens, all_tokens)
    return token_occurances
    
def index_tokens(max_processed_tokens = 50 * (10 ** 6)):
    
    print 'Indexing tokens...'
    token_to_id = {token: id for id, token in enumerate(tokens_sorted_by_freq)}
    tokens = []
    tokens_index = defaultdict(list)
    total_processed_tokens = 0
    
    for token in read_tokens():
        if token == DELIMITER_TOKEN:
            tokens += [[]]
        elif token in token_to_id:

            token_id = token_to_id[token]
            tokens[-1] += [token_id]
            tokens_index[token_id] += [(len(tokens) - 1, len(tokens[-1]) - 1)]
            
            total_processed_tokens += 1
            
            if total_processed_tokens % 1000000 == 0:
                print 'Processed tokens: %d' % total_processed_tokens
                
            if total_processed_tokens >= max_processed_tokens:
                break
    
    print 'Indexed tokens.'
    return tokens, tokens_index

def create_token_vectors(max_distance = 7, filter_threshold = 1, max_vector_size = 500):

    tokens, tokens_index = index_tokens()
    
    def _create_token_vector(token_id):
    
        if token_id < 500 or token_id % 500 == 0:
            print 'Created vector for %d tokens.' % token_id
    
        vector = Counter()
        
        for document_index, index_in_document in tokens_index[token_id]:
            document = tokens[document_index]
            windows_start_index = max(index_in_document - max_distance, 0)
            windows_end_index = min(index_in_document + max_distance, len(document) - 1)
            vector.update(document[windows_start_index:index_in_document])
            vector.update(document[(index_in_document + 1):(windows_end_index + 1)])
        
        norm = float(sum([value ** 2 for value in vector.values()])) ** 0.5
        vector = {key: float(value) / norm for key, value in vector.items() if value >= filter_threshold}
        return dict(sorted(vector.items(), key = lambda item: item[1], reverse = True)[:max_vector_size])
    
    return {token: _create_token_vector(token_id) for token_id, token in enumerate(tokens_sorted_by_freq)}
    
def get_or_create(file_path, creation_method, what_creating):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        
        print 'Creating %s...' % what_creating
        created_object = creation_method()
        print 'Created %s.' % what_creating
        
        with open(file_path, 'w') as f:
            json.dump(created_object, f)
            
        return created_object
    
def get_token_freqs():
    return get_or_create(constants.TOKEN_FREQUENCIES, create_token_freqs, 'token freuqencies')
        
def get_token_vectors():
    return get_or_create(constants.TOKEN_VECTORS, create_token_vectors, 'vector representation')

@cache
def calc_distnace(token1, token2):
    if token1 == token2:
        return 0
    else:
        vector1 = token_to_vector[token1]
        vector2 = token_to_vector[token2]
        cosine = sum([vector1[key] * vector2.get(key, 0) for key in vector1.keys()])
        return 1 - cosine

token_to_global_freq = get_token_freqs()
print 'There are %d tokens' % len(token_to_global_freq)
tokens_sorted_by_freq = list(sorted(token_to_global_freq.keys(), key = lambda token: token_to_global_freq[token], reverse = True))

token_to_vector = get_token_vectors()
print 'There are %d token vectors' % len(token_to_vector)
