import os, json
from lxml import etree

DIR = r'C://downloads/code_project/'
RAW_XML_PATH = os.path.join(DIR, 'Posts.xml')

MAX_ID = 40000000

total_taken_posts = 0
required_post_ids = set()

def parse_tags(raw_tags):
    return list(set(raw_tags[1:-1].split('><')))

def should_take(row):
    if row.attrib['PostTypeId'] == '1':
        if 'java' in parse_tags(row.attrib['Tags']):
            required_post_ids.add(row.attrib['Id'])
            return True
        else:
            return False
    elif row.attrib['PostTypeId'] == '2':
        return row.attrib['ParentId'] in required_post_ids
    else:
        return False

with open(os.path.join(DIR, 'filtered_posts.json'), 'w') as output:
    
    entries_context = etree.iterparse(RAW_XML_PATH, events = ['end'], tag = 'row')
    
    for i, (event, row) in enumerate(entries_context):
        
        if i % 1000 == 0:
            print 'Took %d posts' % total_taken_posts
            print 'Current ID: %s (%d%%)' % (row.attrib['Id'], int(100.0 * float(row.attrib['Id']) / MAX_ID))
            
        if should_take(row):
            total_taken_posts += 1
            json.dump(dict(row.attrib), output)
            output.write('\n')
        
        del event
        row.clear()
        del row
        
    del entries_context
