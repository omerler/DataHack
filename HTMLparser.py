import re

def HTMLtoCodeAndTextParser(HtmlText):
    # The function get a string represent HTML lines and an array with a tag
    #  ("code" or "text"), when single word code are exclude
    outputArray = []
    HtmlText = HtmlText.replace('</code></pre>', '\n').replace('<pre><code>',
         '\n<pre><code>').replace('<p>', '').replace('</p>',
         '').replace(' <code>', ' ').replace('</code>', ' ').splitlines()
    for line in HtmlText:
        if line.startswith('<pre><code>'):
            outputArray.append(("code", line))
        else:
            outputArray.append(("text", line))
    cleanCode = []
    for element in outputArray:
        element = (element[0], re.sub(r'<[\w/]*>', '', element[1]))
        cleanCode.append(element)
    cleanCode[:] = [item for item in cleanCode if item[1] != '']
    return cleanCode
