import javalang


class Argument(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type

class Method(object):
    def __init__(self, name, return_type, arguments, throws):
        self.name = name
        self.return_type = return_type
        self.arguments = arguments
        self.throws = throws


def is_legitimate_method(method):
    return "public static main" not in method.name

# Parsing methods

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
        return 'throws ' + str(throws)



def parse_method(method_node):
    return Method(method_node.name, (parse_type(
        method_node.return_type)),
                  parse_parameters(method_node.parameters),
                  parse_throws(method_node.throws))

# Tester
# with open(r'example2.java', 'r') as f:
#     code = f.read()
#     tree = javalang.parse.parse(code)
#     for i, (path, node) in enumerate(tree):
#         if isinstance(node, javalang.tree.MethodDeclaration):
#             method = parse_method(node)
