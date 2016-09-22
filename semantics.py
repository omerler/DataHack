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
import scipy.stats

from stackoverflow import get_posts
from create_corpus_tokens import tokenize_text, get_stackoverflow_message_text, DELIMITER_TOKEN
from word_to_vec import token_to_global_freq, calc_distnace, get_or_create

TOTAL_POSTS = 856000

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
    
def calculate_tokens_indicativity_scores():
    
    token_cofreqs = defaultdict(list) 
    
    for i, post in enumerate(get_posts(r'C://downloads/code_project/filtered_posts.json')):
    
        if i % 5000 == 0:
            print 'Processed %d posts [%d%%]' % (i, int(100.0 * float(i) / TOTAL_POSTS))
        
        if len(post.answers) > 1:
            
            answer_index1, answer_index2 = choose_two_different_indices(len(post.answers))
            answer1_token_freqs = get_tokens_frequency_in_stackoverflow_message(post.answers[answer_index1])
            answer2_token_freqs = get_tokens_frequency_in_stackoverflow_message(post.answers[answer_index2])
            
            for token in set(answer1_token_freqs.keys()) | set(answer2_token_freqs.keys()):
                token_cofreqs[token] += [(answer1_token_freqs.get(token, 0), answer2_token_freqs.get(token, 0))]
    
    token, cofreqs = token_cofreqs.items()[0]
    indicativity_scores = {token: scipy.stats.pearsonr(*zip(*cofreqs)) for token, cofreqs in token_cofreqs.items() if len(cofreqs) > 1}
    indicativity_scores = {token: scores for token, scores in indicativity_scores.items() if not np.isnan(scores[0]) and not np.isnan(scores[1])}
    return indicativity_scores
    
def get_tokens_indicativity_scores():
    return get_or_create(r'C://downloads/code_project/token_indicativity_scores.json', calculate_tokens_indicativity_scores, 'token indicativity scores')

token_to_indicativity_scores = get_tokens_indicativity_scores()
print 'There are %d indicativity scores' % len(token_to_indicativity_scores)

def get_freq_distance(freq1, freq2):
    return min(freq1, freq2) / max(freq1, freq2)
    
DUMMY_PAIR_DISTANCE_METRICS = (10,) + 12 * (0,)

def get_distance_metrics_for_pair_of_tokens(token1, freq1, token2, freq2):

    if token1 == token2:
        distance = 0
    elif token1 in token_to_global_freq and token2 in token_to_global_freq:
        distance = calc_distnace(token1, token2)
    else:
        return DUMMY_PAIR_DISTANCE_METRICS
    
    global_freq1 = token_to_global_freq[token1]
    indicativity_coef1, indicativity_pval1 = token_to_indicativity_scores.get(token1, (0, 1))
    global_freq2 = token_to_global_freq[token2]
    indicativity_coef2, indicativity_pval2 = token_to_indicativity_scores.get(token2, (0, 1))
    return distance, freq1, global_freq1, indicativity_coef1, indicativity_pval1, freq2, global_freq2, indicativity_coef2, indicativity_pval2, \
            get_freq_distance(freq1, global_freq1), get_freq_distance(freq2, global_freq2), get_freq_distance(freq1, freq2), \
            get_freq_distance(global_freq1, global_freq2), 
    
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
