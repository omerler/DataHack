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
from collections import defaultdict

import scipy

from create_corpus_tokens import tokenize_text

ANSWERS_TO_TAKE = 3

token_to_global_freq = # a dictionary mapping tokens to frequency (0 to 1 float)
token_to_vector = # a dictionary mapping tokens to their vector representation as np.array objects (Based on GLOVE)

def choose_two_different_indices(length):
    
     i = random.randint(0, length - 1)
     j = i
     
     while j == i:
        j = random.randint(0, length - 1)
        
    return i, j
    
def get_tokens_frequency_of_text(text):
    # TODO
    
def get_tokens_frequency_in_stackoverflow_message(message):
    # TODO
    return {token1: freq1, token2: freq2, ...}
    
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
    
token_to_indicativity_scores = calculate_tokens_indicativity_scores()

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
    
def get_distance_metrics(query_tokens, reference_tokens, pairs_to_take):
    
    '''
    query_tokens and reference_tokens are {token --> freq} dictionaries.
    '''
    
    distance_metrics = [get_distance_metrics_for_pair_of_tokens(query_token, query_token_freq, reference_token, reference_token_freq) for \
            query_token, query_token_freq in query_tokens.items() for reference_token, reference_token_freq in reference_tokens.items()]
    distance_metrics = list(sorted(distance_metrics, reverse = True))[:pairs_to_take]
    
    if len(distance_metrics) < pairs_to_take:
        distance_metrics += (pairs_to_take - len(distance_metrics)) * [DUMMY_PAIR_DISTANCE_METRICS]
        
    return [len(query_tokens), len(reference_tokens)] + [metric for metric_group in distance_metrics for metric in metric_group]
    
def extract_feature_vector(method, post, answer_to_remove = None):
    
    features = []
    method_name_tokens = get_tokens_frequency_of_text(method.name)
    
    answers = [answer for post.answers if answer is not answer_to_remove]
    answers = sorted(answers, key = lambda answer: answer.votes, reverse = True)[:ANSWERS_TO_TAKE]
    answers_tokens = map(get_tokens_frequency_in_stackoverflow_message, answers)
    distance_metrics_between_method_name_to_answers = [get_distance_metrics(method_name_tokens, answer_tokens, pairs_to_take = 10) for \
            answer_tokens in answers_tokens]
    if len(distance_metrics_between_method_name_to_answers) < ANSWERS_TO_TAKE:
        distance_metrics_between_method_name_to_answers += (ANSWERS_TO_TAKE - len(distance_metrics_between_method_name_to_answers)) * \
                get_distance_metrics([], [], pairs_to_take = 10)
    features += [feature for feature_group in distance_metrics_between_method_name_to_answers for feature in feature_group]
    
    features += get_distance_metrics(method_name_tokens, get_tokens_frequency_in_stackoverflow_message(post.question), pairs_to_take = 20)
    features += get_distance_metrics(method_name_tokens, get_tokens_frequency_in_stackoverflow_message(post.title), pairs_to_take = 6)
    
    tags_tokens = {tag: 1.0 / len(post.tags) for tag in post.tags}
    features += get_distance_metrics(method_name_tokens, tags_tokens, pairs_to_take = 4)

    return features