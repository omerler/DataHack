import re
from HTMLParser import HTMLParser

from lxml import etree
from StringIO import StringIO
from io import BytesIO

def HTMLtoCodeAndTextParser(HtmlText):
    entries_context = etree.iterparse(BytesIO(HtmlText.encode('utf-8')),
                                      html = True, events = ['end'])
    text = ''
    textArr = []
    for i, (event, row) in enumerate(entries_context):
        if row.tag == 'code' and row.text and ' ' in row.text:
            if text:
                textArr.append(('text', text))
            textArr.append(('code', row.text))
            text = ''
        elif row.text:
            text += row.text
        del event
        row.clear()
        del row

    if text:
        textArr.append(('text', text))

    del entries_context
    return textArr