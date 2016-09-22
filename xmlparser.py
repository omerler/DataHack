import os, json
from lxml import etree

DIR = r'/media/zivlit/Seagate Expansion Drive/Projects/'
RAW_XML_PATH = os.path.join(DIR, 'Posts.xml')

MAX_ID = 40000000

total_taken_posts = 0
required_post_ids = {}


def parse_tags(raw_tags):
    return list(set(raw_tags[1:-1].split('><')))


def filtering(row):
    id = row.attrib['Id']
    if row.attrib['PostTypeId'] == '1': # Query
        tags = parse_tags(row.attrib['Tags'])
        if 'java' in tags and 'android' not in tags:
            required_post_ids[id] = {'query': dict(row.attrib), 'count': int(row.attrib['AnswerCount']), 'answers': []}
    elif row.attrib['PostTypeId'] == '2':   # Answer
        parent_id = row.attrib['ParentId']
        if parent_id in required_post_ids:
            required_post_ids[parent_id]['answers'].append(dict(row.attrib))
            required_post_ids[parent_id]['count'] -= 1
            if required_post_ids[parent_id]['count'] == 0:
                ans = required_post_ids[parent_id]['query']
                ans['answers'] = required_post_ids[parent_id]['answers']
                del required_post_ids[parent_id]
                return ans
    return False

with open(os.path.join('./', 'output.json'), 'w') as output:
    
    entries_context = etree.iterparse(RAW_XML_PATH, events = ['end'], tag = 'row')
    
    for i, (event, row) in enumerate(entries_context):
        
        if i % 1000 == 0:
            print 'Took %d posts' % total_taken_posts
            print 'Current ID: %s (%d%%)' % (row.attrib['Id'], int(100.0 * float(row.attrib['Id']) / MAX_ID))
            
        record = filtering(row)
        if record:
            total_taken_posts += 1
            json.dump(record, output)
            output.write('\n')
        
        del event
        row.clear()
        del row

    del entries_context
