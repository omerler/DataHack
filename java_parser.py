import javalang

with open(r'c://downloads/code_project/example.java', 'r') as f:
    code = f.read()
    
# Parsing methods
    
tree = javalang.parse.parse(code)

def parse_type(type):
    if type is None:
        return 'void'
    else:
        return type.name + (len(type.dimensions) * '[]')
        
def parse_parameters(parameters):
    return ', '.join(['%s %s' % (parse_type(param.type), param.name) for param in parameters])
    
def parse_throws(throws):
    if throws is None:
        return ''
    else:
        return ' throws ' + str(throws)

def parse_method(method_node):
    print '%s %s(%s)%s' % (parse_type(method_node.return_type), method_node.name, \
            parse_parameters(method_node.parameters), parse_throws(method_node.throws))

for i, (path, node) in enumerate(tree):
    if isinstance(node, javalang.tree.MethodDeclaration):
        parse_method(node)
        
# Just tokenizing

tokens = list(javalang.tokenizer.tokenize(code))

print '\n'.join(map(str, {type(t): t for t in tokens}.items()))
print '*' * 50
print set([t.value for t in tokens if isinstance(t, javalang.tokenizer.Identifier)]) | \
        set([t.value for t in tokens if isinstance(t, javalang.tokenizer.BasicType)])
print '*' * 50
print set([t.value for t in tokens if isinstance(t, javalang.tokenizer.String)])