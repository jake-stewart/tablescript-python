from constants import *

class TablescriptLexer:
    def reset(self):
        self.current_lex = START_LEX
        self.lexemes = [START_LEX]
        self.tokens = []
        self.token = ""
        self.escape = False

    def set_lex(self, lex):
        self.current_lex = lex
        self.lexemes.append(lex)
        self.tokens.append(self.token)
        self.token = ""
        self.escape = False

    def clear_lex(self):
        self.current_lex = None

    def change_lex(self, lex):
        self.lexemes[-1] = lex

    def parse(self, script):
        self.reset()

        comment = False
        self.current_lex = NEWLINE_LEX
        for char in script:
            if comment:
                if char == "\n":
                    comment = False
                continue
            if self.current_lex == CODE_LEX:
                if char == CODE_END_OP:
                    self.clear_lex()
                else:
                    self.token += char
                continue

            elif self.current_lex == NEWLINE_LEX:
                if char == "\n" or char == " " or char == "\t":
                    continue
                elif char == COMMENT_OP:
                    comment = True
                    continue
                elif char == V_MERGE_OP:
                    self.set_lex(V_MERGE_LEX)
                    continue
                elif char == CONFIG_OP:
                    self.set_lex(CONFIG_LEX)
                    continue
                self.clear_lex()

            elif self.current_lex == CONFIG_LEX:
                if char == " " or char == "\t":
                    self.clear_lex()
                    continue
                elif char == "\n":
                    self.set_lex(NEWLINE_LEX)
                elif char == SEPARATOR_OP:
                    self.set_lex(SEPARATOR_LEX)
                    continue
                else:
                    self.token += char
                    continue

            elif self.current_lex == SEPARATOR_LEX:
                if char == " " or char == "\t":
                    continue
                elif char == H_MERGE_OP:
                    self.set_lex(H_MERGE_LEX)
                    continue
                elif char == V_MERGE_OP:
                    self.set_lex(V_MERGE_LEX)
                    self.clear_lex()
                    continue
                elif char == CONFIG_OP:
                    self.set_lex(CONFIG_LEX)
                    continue
                else:
                    self.clear_lex()

            elif self.current_lex == V_MERGE_LEX:
                self.clear_lex()

            elif self.current_lex == H_MERGE_LEX:
                self.clear_lex()

            if not self.current_lex:
                if char == CODE_BEGIN_OP:
                    self.set_lex(CODE_LEX)
                    continue
                elif char == SEPARATOR_OP:
                    self.set_lex(SEPARATOR_LEX)
                    continue
                elif char == "\n":
                    if self.current_lex != START_LEX:
                        self.set_lex(NEWLINE_LEX)
                    continue
                else:
                    self.set_lex(STRING_LEX)

            if self.escape:
                self.escape = False
                if char == "n":
                    self.token += " \n "
                elif char == " ":
                    self.token += UNWRAPPABLE_SPACE_CHAR
                else:
                    self.token += char
                continue

            elif char == "\\":
                self.escape = True

            elif char == SEPARATOR_OP:
                self.set_lex(SEPARATOR_LEX)

            elif char == CODE_BEGIN_OP:
                self.set_lex(CODE_LEX)

            elif char == "\n":
                self.set_lex(NEWLINE_LEX)

            elif char == "\t":
                self.token += " "

            else:
                self.token += char

        self.change_lex(END_LEX)
        self.set_lex(None)

        return self.lexemes, self.tokens

if __name__ == "__main__":
    import sys

    helper = {
        0: "START_LEX",
        1: "NEWLINE_LEX",
        2: "STRING_LEX",
        3: "SEPARATOR_LEX",
        4: "H_MERGE_LEX",
        5: "V_MERGE_LEX",
        6: "CODE_LEX",
        7: "CONFIG_LEX",
        8: "END_LEX"
    }

    if len(sys.argv) == 1:
        print("usage: tablescript_lexer.py <table.tbl>")
        exit(1)

    try:
        with open(sys.argv[1]) as f:
            script = f.read()
    except FileNotFoundError:
        print(sys.argv[1], "not found.")

    ts_lexer = TablescriptLexer()
    lexemes, tokens = ts_lexer.parse(script)
    for lexeme, token in zip(lexemes, tokens):
        print(helper[lexeme] + ":", repr(token))
