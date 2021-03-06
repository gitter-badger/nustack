#!python3
# Nustack tokenizer/parser

import re, pprint
LEGAL_IDS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&()*+,-./:;<=>?@\\^_|~'
COMMENT = re.compile(r"(?:/\*.+?\*/)|(?:[ \t\n\r\x0b\x0c]+)", re.DOTALL)
INT     = re.compile(r"\d+(?!\.)")
FLOAT   = re.compile(r"\d*\.\d+")
BOOL    = re.compile("#t|#f")
STRING  = re.compile(r"('.*?(?<!\\)')|(\".*?(?<!\\)\")")
SYMBOL  = re.compile(r"`[%s]+" % LEGAL_IDS)
CALL    = re.compile(r"[%s]+" % LEGAL_IDS)

class TokenizeError(Exception): pass

class Token:
    def __init__(self, type, val):
        self.type = type
        self.val  = val
    def __repr__(self):
        return "Token(type=%s, val=%s)" % (repr(self.type), repr(self.val),)

def tokenize(code):
    tokens = []
    while code:
        commentmatch = COMMENT.match(code)
        intmatch = INT.match(code)
        floatmatch = FLOAT.match(code)
        boolmatch = BOOL.match(code)
        stringmatch = STRING.match(code)
        symbolmatch = SYMBOL.match(code)
        callmatch = CALL.match(code)
        if commentmatch:
            commentend = commentmatch.span()[1]
            code = code[commentend:]
        elif intmatch:
            span = intmatch.span()[1]
            n = code[:span]
            n = int(n)
            tokens.append(Token("lit_int", n))
            code = code[span:]
        elif floatmatch:
            span = floatmatch.span()[1]
            n = code[:span]
            n = float(n)
            tokens.append(Token("lit_float", n))
            code = code[span:]
        elif boolmatch:
            span = boolmatch.span()[1]
            b = code[:span]
            if b == "#t":
                bool = True
            else:
                bool = False
            code = code[span:]
            tokens.append(Token("lit_bool", bool))
        elif stringmatch:
            span = stringmatch.span()[1]
            s = code[:span]
            tokens.append(Token("lit_string", s[1:-1]))
            code = code[span:]
        elif code[0] == "[":
            tokens.append(Token("lit_liststart","["))
            code = code[1:]
        elif code[0] == "]":
            tokens.append(Token("listend", "]"))
            code = code[1:]
        elif code[0] == "{":
            tokens.append(Token("codestart", "{"))
            code = code[1:]
        elif code[0] == "}":
            subcode = []
            while True:
                t = tokens.pop()
                if t.type == "codestart":
                    break
                subcode.append(t)
            tokens.append(Token("lit_code", list(reversed(subcode))))
            code = code[1:]
        elif callmatch:
            span = callmatch.span()[1]
            sym = code[:span]
            code = code[span:]
            tokens.append(Token("call", sym))
        elif symbolmatch:
            span = symbolmatch.span()[1]
            sym = code[1:span]
            code = code[span:]
            tokens.append(Token("lit_symbol", sym))
        else:
            print(code)
            raise TokenizeError("Can not find a token!")
    return tokens

if __name__ == '__main__':
    code = input("Enter code: ")
    for token in tokenize(code):
        print(token)
