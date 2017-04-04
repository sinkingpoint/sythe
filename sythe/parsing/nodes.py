import sythe.parsing.errors as errors
import regex

def expect(token, tokens):
    if tokens[0] != token:
        raise errors.ParsingError(
            'Invalid next token. Expected {}, got {}'.format(token, tokens[0])
        )
    tokens.pop(0)

class RuleNode:
    def __init__(self, tokens):
        try:
            self.resource = ResourceNode(tokens)
            condition_length = isolate_condition(tokens)
            condition_tokens = tokens[:condition_length]
            del tokens[:condition_length]
            self.condition = parse_condition(condition_tokens)
            expect('{', tokens)
            self.actions = []
            while tokens[0] != '}':
                self.actions.append(ActionNode(tokens))
            expect('}', tokens)
        except IndexError:
            raise errors.ParsingError('EOF found while parsing')

    def execute(self, resource):
        if self.condition.execute(resource):
            for action in self.actions:
                action.execute(resource)

    def __str__(self):
        actions_str = ['\n\t{}'.format(str(action)) for action in self.actions]
        return '{}({}){{{}\n}}'.format(self.resource, self.condition, ''.join(actions_str))

class ActionNode:
    def __init__(self, tokens):
        self.action_name = tokens.pop(0)
        expect('(', tokens)
        self.arguments = []
        while tokens[0] != ')':
            if not regex.match(r'^[a-zA-Z0-9]+:$', tokens[0]):
                raise errors.ParsingError(
                    'Invalid action parameter {}'.format(tokens[0])
                )
            argument_name = tokens.pop(0)[:-1]
            argument_value = parse_operand(tokens.pop(0))
            self.arguments.append((argument_name, argument_value))
            if tokens[0] != ')':
                expect(',', tokens)

        expect(')', tokens)

    def execute(self, resource):
        method = getattr(resource, self.action_name)
        if method == None:
            raise errors.ParsingError(
                'Invalid action \'{}\' on resource'.format(self.action_name)
            )
        method(self.arguments)

    def __str__(self):
        arguments_str = ['{}: {}'.format(arg_name, arg_value) for arg_name, arg_value in self.arguments]
        return '{}({})'.format(self.action_name, ', '.join(arguments_str))

class AndNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, resource):
        return self.left.execute(resource) and self.right.execute(resource)

    def __str__(self):
        return '({} & {})'.format(self.left, self.right)

class OrNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, resource):
        return self.left.execute(resource) or self.right.execute(resource)

    def __str__(self):
        return '({} | {})'.format(self.left, self.right)

class EqualsNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, resource):
        return self.left.execute(resource) == self.right.execute(resource)

    def __str__(self):
        return '({} = {})'.format(self.left, self.right)

class GreaterThanNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, resource):
        return self.left.execute(resource) > self.right.execute(resource)

    def __str__(self):
        return '({} > {})'.format(self.left, self.right)

class LessThanNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, resource):
        return self.left.execute(resource) < self.right.execute(resource)

    def __str__(self):
        return '({} < {})'.format(self.left, self.right)

def isolate_condition(tokens):
    if tokens[0] != '(':
        raise errors.ParsingError('Invalid start to condition: {}'.format(tokens[0]))

    open_brackets = 0
    i = 0
    end = -1
    for i in range(len(tokens)):
        if tokens[i] == '(':
            open_brackets += 1
        elif tokens[i] == ')':
            open_brackets -= 1

        if open_brackets == 0:
            end = i + 1
            break

    if open_brackets > 0:
        raise errors.ParsingError('Unmatched parenthesis in condition')

    return end

def parse_condition(tokens):
    condition = tokens[:isolate_condition(tokens)]
    operators = {
        '&': (12, 'left', AndNode),
        '|': (13, 'left', OrNode),
        '=': (8, 'left', EqualsNode),
        '>': (7, 'left', GreaterThanNode),
        '<': (7, 'left', LessThanNode)
    }

    operator_stack = []
    output_queue = []
    while len(condition) > 0:
        token = condition.pop(0)
        if token in operators:
            operator1 = operators[token]
            while operator_stack[-1] in operators and \
                ((operator1[1] == 'left' and operator1[0] >= operators[operator_stack[-1]][0]) or \
                 (operator1[1] == 'right' and operator1[0] > operators[operator_stack[-1]][0])):
                output_queue.append(operator_stack.pop())
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack[-1] != '(':
                operator = operator_stack.pop()
                if operator != '(' and len(operator_stack) == 0:
                    raise errors.ParsingError('Unmatched parenthesis in output')
                output_queue.append(operator)
            operator_stack.pop()
        else:
            output_queue.append(token)

    while len(operator_stack) > 0:
        token = operator_stack.pop()
        if token == '(' or token == ')':
            raise errors.ParsingError('Unmatched parenthesis in output')
        output_queue.append(token)

    ast = []
    for token in output_queue:
        if token in operators:
            operand1 = ast.pop()
            operand2 = ast.pop()
            ast.append(operators[token][2](operand2, operand1))
        else:
            ast.append(parse_operand(token))

    if len(ast) != 1:
        raise errors.ParsingError('Invalid expression')
    return ast[0]

def parse_operand(operand_token):
    if regex.match(r'^[0-9]+$', operand_token):
        return IntLiteralNode(operand_token)
    elif regex.match(r'^(".*")|(\'.*\')$', operand_token):
        return StringLiteralNode(operand_token)
    elif regex.match(r'^true|false$', operand_token):
        return BooleanLiteralNode(operand_token)
    elif regex.match(r'^[a-zA-Z0-9_:\.]+$', operand_token):
        return VariableNode(operand_token)
    else:
        raise errors.ParsingError('Invalid Operand: {}'.format(operand_token))

class IntLiteralNode:
    def __init__(self, token):
        try:
            self.value = int(token)
        except:
            raise errors.ParsingError('Invalid int literal: {}'.format(token))

    def execute(self, resource):
        return self.value

    def __str__(self):
        return '{}'.format(self.value)

class StringLiteralNode:
    def __init__(self, token):
        self.value = token[1:-1]

    def execute(self, resource):
        return self.value

    def __str__(self):
        return '"{}"'.format(self.value)

class BooleanLiteralNode:
    def __init__(self, token):
        if token == 'true':
            self.value = True
        elif token == 'false':
            self.value = False
        elif isinstance(token, bool):
            self.value = token
        else:
            raise errors.ParsingError('Invalid boolean literal: {}'.format(token))

    def execute(self, resource):
        return self.value

    def __str__(self):
        return '{}'.format(self.value)

class NoneNode:
    def execute(self, resource):
        return None

    def __str__(self):
        return 'None'

class VariableNode:
    def __init__(self, variable_name):
        self.variable_name = variable_name

    def execute(self, resource):
        path = self.variable_name.split('.')
        value = resource
        for path_item in path:
            try:
                value = value[path_item]
            except KeyError:
                value = None
                break

        allowed_types = [str, int, bool, type(None)]
        if type(value) in allowed_types:
            return value
        else:
            raise errors.ParsingError('Unknown datatype: {}'.format(type(value)))

    def __str__(self):
        return '{}'.format(self.variable_name)

class ResourceNode:
    def __init__(self, tokens):
        valid_resource_types = ['ec2_instance']
        resource = tokens[0]
        if resource in valid_resource_types:
            self.resource_name = resource
            tokens.pop(0)
        else:
            raise errors.ParsingError('Invalid resource type: {}'.format(tokens[0]))

    def get_resource_name(self):
        return self.resource_name

    def __str__(self):
        return self.resource_name
