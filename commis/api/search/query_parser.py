#
# lucene_grammar.py
#
# Copyright 2011, Paul McGuire
#
# implementation of Lucene grammar, as decribed
# at http://svn.apache.org/viewvc/lucene/dev/trunk/lucene/docs/queryparsersyntax.html
#

from pyparsing import (Literal, CaselessKeyword, Forward, Regex, QuotedString, Suppress,
    Optional, Group, FollowedBy, operatorPrecedence, opAssoc, ParseException, ParserElement)
ParserElement.enablePackrat()

COLON,LBRACK,RBRACK,LBRACE,RBRACE,TILDE,CARAT = map(Literal,":[]{}~^")
LPAR,RPAR = map(Suppress,"()")
and_ = CaselessKeyword("AND")
or_ = CaselessKeyword("OR")
not_ = CaselessKeyword("NOT")
to_ = CaselessKeyword("TO")
keyword = and_ | or_ | not_

expression = Forward()

valid_word = Regex(r'([a-zA-Z0-9*_+.-]|\\[!(){}\[\]^"~*?\\:])+').setName("word")
valid_word.setParseAction(
    lambda t : t[0].replace('\\\\',chr(127)).replace('\\','').replace(chr(127),'\\')
    )

string = QuotedString('"')

required_modifier = Literal("+")("required")
prohibit_modifier = Literal("-")("prohibit")
integer = Regex(r"\d+").setParseAction(lambda t:int(t[0]))
proximity_modifier = Group(TILDE + integer("proximity"))
number = Regex(r'\d+(\.\d+)?').setParseAction(lambda t:float(t[0]))
fuzzy_modifier = (Group(TILDE + number) | TILDE)("fuzzy")

term = Forward()
field_name = valid_word.copy().setName("fieldname")
incl_range_search = Group(LBRACK + term("lower") + to_ + term("upper") + RBRACK)
excl_range_search = Group(LBRACE + term("lower") + to_ + term("upper") + RBRACE)
range_search = incl_range_search("incl_range") | excl_range_search("excl_range")
boost = (CARAT + number("boost"))

string_expr = Group(string + proximity_modifier) | string
word_expr = Group(valid_word + fuzzy_modifier) | valid_word
term << (Optional(field_name("field") + COLON) + 
         (word_expr("value") | string_expr("value") | range_search | Group(LPAR + expression + RPAR)) +
         Optional(boost))
term.setParseAction(lambda t:[t] if 'field' in t or 'boost' in t else None)

expression << operatorPrecedence(term,
    [
    (required_modifier | prohibit_modifier, 1, opAssoc.RIGHT),
    ((not_ | '!').setParseAction(lambda:"NOT")("not"), 1, opAssoc.RIGHT),
    ((and_ | '&&').setParseAction(lambda:"AND")("and"), 2, opAssoc.LEFT),
    (Optional(or_ | '||').setParseAction(lambda:"OR")("or"), 2, opAssoc.LEFT),
    ])
