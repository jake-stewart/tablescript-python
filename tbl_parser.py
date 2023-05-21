from typing import List
from tbl_builder import TableBuilder
from tbl_table import Table
from tbl_style_parser import CellStyleParser
from tbl_cell import Cell, Content
from tbl_token import Token, TokenType

class Parser:
    _builder: TableBuilder;
    _tokens: List[Token];
    _styleParser: CellStyleParser;
    _idx: int;
    _row: int;
    _col: int;

    def parse(self, tokens: List[Token]) -> Table:
        self._row = 0;
        self._col = 0;
        self._idx = 0;
        self._tokens = tokens;
        self._builder = TableBuilder();
        self._styleParser = CellStyleParser();
        self._parse();
        self._builder.fixFullMerges();
        return self._builder.getTable();

    def _parse(self):
        while (token := self._next()) is not None:
            if token.type == TokenType.TEXT:
                if token.value:
                    content = Content(token.value)
                    self._builder.addCellContent(self._row, self._col, content)
            elif token.type == TokenType.CODE:
                if token.value:
                    content = Content(token.value, True)
                    self._builder.addCellContent(self._row, self._col, content)
            elif token.type == TokenType.STYLE and token.value:
                self._parseStyleSchema(token.value);
            elif token.type == TokenType.COL_SEP:
                self._col += 1;
            elif token.type == TokenType.ROW_SEP:
                self._col = 0;
                self._row += 1;
                while (token := self._peek()) is not None \
                        and token.type == TokenType.ROW_SEP:
                    self._next()
            elif token.type == TokenType.H_MERGE:
                self._builder.mergeCellWithLeft(self._row, self._col)
            elif token.type == TokenType.V_MERGE:
                self._builder.mergeCellWithAbove(self._row, self._col)
            elif token.type == TokenType.H_BORDER:
                self._builder.addHorizontalBorder(self._row - 1);
            elif token.type == TokenType.THICK_H_BORDER:
                self._builder.addThickHorizontalBorder(self._row - 1);
            else:
                raise Exception("Unrecognized token")

    def _peek(self) -> Token | None:
        if self._idx >= len(self._tokens):
            return None;
        return self._tokens[self._idx];

    def _next(self) -> Token | None:
        self._idx += 1;
        if self._idx > len(self._tokens):
            return None;
        return self._tokens[self._idx - 1];

    def _parseStyleSchema(self, schema: str) -> None:
        style = self._styleParser.parse(schema);
        self._builder.addCellStyle(self._row, self._col, style);

