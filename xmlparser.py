import os, json
from lxml import etree

RAW_XML_PATH = os.path.join('/media/zivlit/Seagate Expansion Drive/Projects/', 'Posts.xml')
required = []

with open('output.json', 'w') as output:
    entries_context = etree.iterparse(RAW_XML_PATH, events = ['end'], tag = 'row')
    for i, (event, row) in enumerate(entries_context):
        if i%1000 == 0:
            print row.attrib['Id']
        if 'ParentId' in row.attrib:
            if row.attrib['ParentId'] in required:
                json.dump(dict(row.attrib), output)
                output.write('\n')
        else:
            if 'java' in str(row.attrib['Tags']):
                # print row.attrib['Id']
                required.append(row.attrib['Id'])
                json.dump(dict(row.attrib), output)
                output.write('\n')
        del row
