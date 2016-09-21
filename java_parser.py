import javalang

with open(r'c://downloads/code_project/example.java', 'r') as f:
    code = f.read()
    
# Full parsing
    
tree = javalang.parse.parse(code)

for i, (path, node) in enumerate(tree):
    print '%s [%s]' % (str(node), str(type(node)))
    for attr in dir(node):
        if '__' not in attr:
            print '\t' + '%s: %s' % (attr, str(getattr(node, attr)))
    if i > 50:
        break
        
# Just tokenizing

tokens = list(javalang.tokenizer.tokenize(code))

print '\n'.join(map(str, {type(t): t for t in tokens}.items()))
print '*' * 50
print set([t.value for t in tokens if isinstance(t, javalang.tokenizer.Identifier)]) | \
        set([t.value for t in tokens if isinstance(t, javalang.tokenizer.BasicType)])
print '*' * 50
print set([t.value for t in tokens if isinstance(t, javalang.tokenizer.String)])