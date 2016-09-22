import javalang
import re

class Argument(object):
    def __init__(self, type, name):
        self.name = name
        self.type = type
    def __str__(self):
        return '%s %s' % (self.type, self.name)

class Method(object):
    def __init__(self, name, return_type, arguments, throws):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.throws = throws
    def __str__(self):
        return '%s %s(%s) %s' % (self.return_type, self.name, ', '.join(map(str, self.arguments)), self.throws)

def is_legitimate_method(method):
    return method.name != 'main'

def parse_type(type):
    if type is None:
        return 'void'
    else:
        return type.name + (len(type.dimensions) * '[]')

def parse_parameters(parameters):
    return [Argument(parse_type(param.type), param.name) for param in parameters]

def parse_throws(throws):
    if throws is None:
        return ''
    else:
        return 'throws ' + str(throws)

def parse_method(method_node):
    return Method(method_node.name, parse_type(method_node.return_type), parse_parameters(method_node.parameters), parse_throws(method_node.throws))

def extract_methods(contentArray):
    '''
    return function daclerations as methods
    '''
    methodsArr = []
    for data_type, data_content in contentArray:
        if data_type == "code":
            try:
                if 'class' not in data_content:
                    data_content = "public class module {\n" + data_content + "\n}"
                tree = javalang.parse.parse(data_content)
                for path, node in tree:
                    if isinstance(node, javalang.tree.MethodDeclaration):
                        method = parse_method(node)
                        if is_legitimate_method(method):
                            methodsArr.append(method)
            except:
                continue  # if code is written with mistakes - skip to the
                # next code line. todo specificity in order to extand.
    return methodsArr

# with open(r'example2.java', 'r') as f:
#     code = f.read()
#     tree = javalang.parse.parse(code)
#     for i, (path, node) in enumerate(tree):
#         if isinstance(node, javalang.tree.MethodDeclaration):
#             method = parse_method(node)


