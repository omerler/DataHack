
def HTMLtoCodeAndTextParser(HtmlText):
    # The function get a string represent HTML lines and Return two array:
    # First - clean java code (exclude one word code)
    # Second - answer text in strings (include one word code)
    text = []
    code = []
    HtmlText = HtmlText.replace('</code></pre>', '\n').replace('<pre><code>',
         '\n<pre><code>').replace('<p>', '').replace('</p>',
         '').replace(' <code>', ' ').replace('</code>', ' ').splitlines()
    for line in HtmlText:                                                                                                                                                            
        if line.startswith('<pre><code>'):
            code.append(line)
        else:
            text.append(line)
    cleanCode = []
    for element in code:
        element = element.replace('<pre><code>', "")
        cleanCode.append(element)
    return cleanCode, text
