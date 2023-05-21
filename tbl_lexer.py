from typing import List
from enum import Enum
from tbl_token import Token
from tbl_token_type import TokenType

class Symbol:
    COL_SEP = "|";
    ROW_SEP = "\n";
    H_BORDER = "-";
    THICK_H_BORDER = "=";
    H_MERGE = "<";
    V_MERGE = "^";
    STYLE = "?";
    CODE = "`";

class Lexer:
    _script: str;
    _idx: int;
    _tokens: List[Token];

    def lex(self, script: str) -> List[Token]:
        self._script = script;
        self._tokens = [];
        self._idx = 0;
        self._lex();
        return self._tokens;

    def _lex(self):
        while True:
            self._skipWhitespace();
            if (char := self._peek()) is None or \
                    char != Symbol.ROW_SEP:
                break;
            self._next();
        while True:
            self._parseBorders()
            if self._peek() == Symbol.STYLE:
                self._parseStyle();
            elif self._peek() == Symbol.V_MERGE:
                self._tokens.append(Token(TokenType.V_MERGE));
                self._next()
            self._lexRow();
            self._next();
            if self._peek() == None:
                break;
            self._tokens.append(Token(TokenType.ROW_SEP));
            self._skipWhitespace();

    def _peek(self) -> str | None:
        if self._idx >= len(self._script):
            return None;
        return self._script[self._idx];

    def _next(self) -> str | None:
        self._idx += 1;
        if self._idx > len(self._script):
            return None;
        return self._script[self._idx - 1];

    def _skipWhitespace(self) -> None:
        while self._peek() in (" ", "\t"):
            self._next();
    
    def _lexRow(self) -> None:
        c: str | None;
        text: str = "";
        while (c := self._peek()) not in (Symbol.ROW_SEP, None):
            if c == Symbol.COL_SEP:
                if text:
                    self._tokens.append(Token(TokenType.TEXT, text));
                    text = "";
                self._parseSeparator();
            elif c == Symbol.CODE:
                if text:
                    self._tokens.append(Token(TokenType.TEXT, text));
                    text = "";
                self._parseCode();
            elif c == "\\":
                self._next();
                c = self._next();
                if c == "n":
                    text += "\n";
                elif c is not None:
                    text += c;
            else:
                text += c;
                self._next();
        if text:
            self._tokens.append(Token(TokenType.TEXT, text));

    def _parseSeparator(self) -> None:
        assert self._peek() == Symbol.COL_SEP;
        self._tokens.append(Token(TokenType.COL_SEP));
        self._next();
        self._skipWhitespace();
        if self._peek() == Symbol.H_MERGE:
            self._tokens.append(Token(TokenType.H_MERGE));
            self._next()
        elif self._peek() == Symbol.V_MERGE:
            self._tokens.append(Token(TokenType.V_MERGE));
            self._next()
        elif self._peek() == Symbol.STYLE:
            self._parseStyle();
            self._skipWhitespace();

    def _parseStyle(self) -> None:
        assert self._peek() == Symbol.STYLE;
        self._next();
        style = "";
        while (c := self._peek()) is not None and c.isalpha():
            style += c;
            self._next();
        self._tokens.append(Token(TokenType.STYLE, style));

    def _parseCode(self) -> None:
        assert self._peek() == Symbol.CODE;
        self._next();
        code = "";
        while (c := self._peek()) is not None and c != Symbol.CODE:
            self._next();
            code += c;
        self._next();
        self._tokens.append(Token(TokenType.CODE, code));

    def _parseBorder(self, symbol: str, tokenType: TokenType) -> bool:
        while self._idx >= len(self._script):
            return False;
        idx = self._idx;
        while idx < len(self._script):
            if self._script[idx] == symbol:
                idx += 1
                continue
            if self._script[idx] == Symbol.ROW_SEP:
                break
            return False;
        self._tokens.append(Token(tokenType));
        self._idx = idx + 1;
        return True;

    def _parseBorders(self) -> None:
        while True:
            hasBorder = False
            if self._peek() == Symbol.H_BORDER:
                hasBorder = self._parseBorder(Symbol.H_BORDER, TokenType.H_BORDER);
                if hasBorder:
                    continue
            if self._peek() == Symbol.THICK_H_BORDER:
                hasBorder = self._parseBorder(Symbol.THICK_H_BORDER, TokenType.THICK_H_BORDER);
            if not hasBorder:
                break;
