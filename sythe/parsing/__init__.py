import tokenizer
import nodes

def parse_rules_from_string(rules_string):
    tokens = tokenizer.tokenize_string(rules_string)

    rules = []
    while len(tokens) > 0:
        rule = nodes.RuleNode(tokens)
        rules.append(rule)

    return rules
