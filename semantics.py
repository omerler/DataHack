'''
indicativity of a token = correlation between its appearance in various parts of the post (e.g. different answers)

relationship between query and reference token:
1. The distance between their vector representation
2. frequency of the query token
3. indicativity of the query token
4. frequency of the reference token
5. indicativity of the reference token

distance between query tokens (query_token[1],..., query_token[k]) to reference tokens (reference_token[1],..., reference_token[r]):
- Find the M closest pairs of ([j])
'''

import random
from collections import defaultdict, Counter

import numpy as np
import scipy
import scipy.spatial

from create_corpus_tokens import tokenize_text, get_stackoverflow_message_text, DELIMITER_TOKEN

def choose_two_different_indices(length):
    
     i = random.randint(0, length - 1)
     j = i
     
     while j == i:
        j = random.randint(0, length - 1)
        
     return i, j
    
def normalize(counter):
    total = float(sum(counter.values()))
    return {key: value / total for key, value in counter.items()}
    
def get_tokens_frequency(tokens):
    return normalize(Counter(tokens))
    
def get_tokens_frequency_of_text(text):
    return get_tokens_frequency(tokenize_text(text))
    
def get_tokens_frequency_in_stackoverflow_message(message):
    return get_tokens_frequency_of_text(get_stackoverflow_message_text(message))
    
def read_tokens():

    BUFFER_SIZE = 10 ** 5

    with open(r'C://downloads/code_project/tokens.txt', 'r') as f:
    
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

def create_token_freqs_and_vectors(max_distance = 7):
    
    token_occurances = Counter()
    token_cooccurances = Counter()
    last_tokens = []
    
    for token in read_tokens():
    
        if token == DELIMITER_TOKEN:
            last_tokens = []
            continue
        
        token_occurances[token] += 1
        
        for prefix_token in last_tokens:
            token_cooccurances[(token, prefix_token)] += 1
        
        if len(last_tokens) > max_distance:
            last_tokens.pop(0)

        last_tokens += [token]
    
    token_freqs = normalize(token_occurances)
    token_list = list(token_occurances.keys())
    token_vectors = {token: np.array([token_cooccurances[(token, other_token)] + token_cooccurances[(other_token, token)] for \
            other_token in token_list], dtype = float) for token in token_list}
    return token_freqs, token_vectors

print 'Building vector representation...'
token_to_global_freq, token_to_vector = create_token_freqs_and_vectors()
print 'Built vector representation.'
    
def calculate_tokens_indicativity_scores():
    
    token_cofreqs = defaultdict(list) 
    
    for post in posts:
        if len(post.answers) > 1:
            
            answer_index1, answer_index2 = choose_two_different_indices(len(post.answers))
            answer1_token_freqs = get_tokens_frequency_in_stackoverflow_message(post.answers[answer_index1])
            answer2_token_freqs = get_tokens_frequency_in_stackoverflow_message(post.answers[answer_index2])
            
            for token in answer1_token_freqs.keys() | answer2_token_freqs.keys():
                token_cofreqs[token] += [(answer1_token_freqs.get(token, 0), answer2_token_freqs.get(token, 0))]
    
    return {token: scipy.stats.pearsonr(zip(*cofreqs)) for token, cofreqs in token_cofreqs.items()}

print 'Creating indicativity scores...'
token_to_indicativity_scores = calculate_tokens_indicativity_scores()
print 'Created indicativity scores.'

def get_freq_distance(freq1, freq2):
    return min(freq1, freq2) / max(freq1, freq2)

def get_distance_metrics_for_pair_of_tokens(token1, freq1, token2, freq2):
    distance = scipy.spatial.distance.cosine(token_to_vector[token1], token_to_vector[token2])
    global_freq1 = token_to_global_freq[token1]
    indicativity_coef1, indicativity_pval1 = token_to_indicativity_scores[token1]
    global_freq2 = token_to_global_freq[token2]
    indicativity_coef2, indicativity_pval2 = token_to_indicativity_scores[token2]
    return distance, freq1, global_freq1, indicativity_coef1, indicativity_pval1, freq2, global_freq2, indicativity_coef2, indicativity_pval2, \
            get_freq_distance(freq1, global_freq1), get_freq_distance(freq2, global_freq2), get_freq_distance(freq1, freq2), \
            get_freq_distance(global_freq1, global_freq2), 
    
DUMMY_PAIR_DISTANCE_METRICS = (10,) + 12 * (0,)
    
def get_distance_metrics_between_qeuery_and_reference(query_tokens, reference_tokens, pairs_to_take):
    
    '''
    query_tokens and reference_tokens are {token --> freq} dictionaries.
    Will take exactly 'pairs_to_take' pairs, each with a unique query and reference token.
    '''
    
    result = []
    optional_distance_metrics = {(query_token, reference_token): get_distance_metrics_for_pair_of_tokens(query_token, query_token_freq, \
            reference_token, reference_token_freq) for query_token, query_token_freq in query_tokens.items() for reference_token, reference_token_freq \
            in reference_tokens.items()}
    
    while len(result) < pairs_to_take and len(optional_distance_metrics) > 0:
        (query_token, reference_token), distance_metrics = sorted(optional_distance_metrics.items(), key = lambda item: item[1][0], reverse = True)[0]
        result += [distance_metrics]
        optional_distance_metrics = {key: value for key, value in optional_distance_metrics.items() if key[0] != query_token and key[1] != reference_token}
                
    if len(result) < pairs_to_take:
        result += (pairs_to_take - len(result)) * [DUMMY_PAIR_DISTANCE_METRICS]
        
    return [len(query_tokens), len(reference_tokens)] + [metric for metric_group in result for metric in metric_group]
    
def get_distance_metrics_between_qeuery_and_references(query_tokens, references_tokens, references_to_take, pairs_per_reference_to_take):
    distance_metric_groups = [get_distance_metrics_between_qeuery_and_reference(query_tokens, reference_tokens, pairs_per_reference_to_take) for \
            reference_tokens in references_tokens]
    if len(distance_metric_groups) < references_to_take:
        distance_metric_groups += (references_to_take - len(distance_metric_groups)) * \
                get_distance_metrics_between_qeuery_and_reference([], [], pairs_per_reference_to_take)
    return [metric for metric_group in distance_metric_groups for metric in metric_group]
    
def extract_feature_vector(method, post, answer_to_remove = None):
    
    method_name_tokens = get_tokens_frequency_of_text(method.name)
    method_arg_name_tokens = get_tokens_frequency([argument.name for argument in method.arguments])
    method_arg_type_tokens = get_tokens_frequency([argument.type for argument in method.arguments])
    method_return_type_token = {method.return_type: 1.0}
    
    question_tokens = get_tokens_frequency_in_stackoverflow_message(post.question)
    title_tokens = get_tokens_frequency_in_stackoverflow_message(post.title)
    tags_tokens = {tag: 1.0 / len(post.tags) for tag in post.tags}
    
    answers = [answer for answer in post.answers if answer is not answer_to_remove]
    answers = sorted(answers, key = lambda answer: answer.votes, reverse = True)[:ANSWERS_TO_TAKE]
    answers_tokens = map(get_tokens_frequency_in_stackoverflow_message, answers)
    
    features = []
    
    def _add_features_for_method_tokens(method_tokens, answers_to_take, pairs_per_answer, question_pairs, title_pairs, tag_pairs):
        features += get_distance_metrics_between_qeuery_and_references(method_tokens, answers_tokens, references_to_take = answers_to_take, \
                pairs_per_reference_to_take = pairs_per_answer)
        features += get_distance_metrics_between_qeuery_and_reference(method_tokens, question_tokens, pairs_to_take = question_pairs)
        features += get_distance_metrics_between_qeuery_and_reference(method_tokens, title_tokens, pairs_to_take = title_pairs)
        features += get_distance_metrics_between_qeuery_and_reference(method_tokens, tags_tokens, pairs_to_take = tag_pairs)
        
    _add_features_for_method_tokens(method_name_tokens, answers_to_take = 5, pairs_per_answer = 10, question_pairs = 20, title_pairs = 6, tag_pairs = 4)
    _add_features_for_method_tokens(method_arg_name_tokens, answers_to_take = 2, pairs_per_answer = 3, question_pairs = 3, title_pairs = 2, tag_pairs = 2)
    _add_features_for_method_tokens(method_arg_type_tokens, answers_to_take = 2, pairs_per_answer = 3, question_pairs = 3, title_pairs = 2, tag_pairs = 2)
    _add_features_for_method_tokens(method_return_type_token, answers_to_take = 2, pairs_per_answer = 1, question_pairs = 1, title_pairs = 1, tag_pairs = 1)

    return features
