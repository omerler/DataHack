import sys, os, json
from lxml import etree
from HTMLparser import HTMLtoCodeAndTextParser

MAX_ID = 40000000

total_taken_posts = 0
required_posts = {}


def parse_tags(raw_tags):
    return list(set(raw_tags[1:-1].split('><')))


def filtering(row):
    id = row.attrib['Id']
    if row.attrib['PostTypeId'] == '1': # Query
        tags = parse_tags(row.attrib['Tags'])
        if 'java' in tags and 'android' not in tags:
            required_posts[id] = {'query': dict(row.attrib), 'count': int(row.attrib['AnswerCount']), 'answers': []}
            required_posts[id]['query']['Body'] = HTMLtoCodeAndTextParser(required_posts[id]['query']['Body'])
    elif row.attrib['PostTypeId'] == '2':   # Answer
        parent_id = row.attrib['ParentId']
        if parent_id in required_posts:
            answer = dict(row.attrib)
            answer['Body'] = HTMLtoCodeAndTextParser(answer['Body'])
            required_posts[parent_id]['answers'].append(answer)
            required_posts[parent_id]['count'] -= 1
            if required_posts[parent_id]['count'] == 0:
                ans = required_posts[parent_id]['query']
                ans['answers'] = required_posts[parent_id]['answers']
                del required_posts[parent_id]
                return ans
    return False

if __name__ == "__main__":
    input_file = os.path.join(sys.argv[1], sys.argv[2])
    output_file = os.path.join(sys.argv[1], sys.argv[3])

    with open(output_file, 'w') as output:
        entries_context = etree.iterparse(input_file, events = ['end'], tag = 'row')

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
