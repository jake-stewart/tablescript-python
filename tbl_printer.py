from typing import List, Tuple
from tbl_style import HorizontalAlignment, VerticalAlignment
from tbl_cell import Cell
from tbl_table import Table
from tbl_border import Border, BorderStyle

class ColumnInfo:
    rowSpanProgress: int;
    effectiveRow: int;
    line: int;
    cell: Cell;
    col: int;
    width: int;
    height: int;

    def __init__(self, col, cell: Cell):
        self.col = col;
        self.cell = cell;
        self.rowSpanProgress = 0;
        self.effectiveRow = 0;
        self.line = 0;

class TablePrinter:
    _table: Table;
    _widths: List[int];
    _heights: List[int];
    _columnInfos: List[ColumnInfo];
    _border: Border;
    _pad: str;

    def __init__(self, table: Table):
        self._table = table;
        self._pad = table.padding * " ";

    def setBorder(self, border: Border):
        self._border = border;

    def print(self):
        self._populateColumnInfo();
        self._printTopBorder();
        for row in range(len(self._heights)):
            self._printRow(row);
            if row < len(self._table) - 1:
                self._printRowBorder(row);
                self._prepareRow(row + 1);
        self._printBottomBorder();

    def setDimensions(self, widths: List[int], heights: List[int]):
        self._widths = widths;
        self._heights = heights;

    def _resetColumnInfo(self, info: ColumnInfo, row: int):
        info.rowSpanProgress = 0;
        info.cell = self._table[row][info.col];
        info.width = sum(
                self._widths[info.col:info.col + info.cell.colspan]);
        info.width += info.cell.colspan - 1;
        info.width += info.cell.colspan * self._table.padding * 2;
        info.height = sum(self._heights[row:row + info.cell.rowspan]);
        info.height += info.cell.rowspan - 1;

        if info.cell.style.valign == VerticalAlignment.TOP:
            info.line = 0
        elif info.cell.style.valign == VerticalAlignment.BOTTOM:
            info.line = -(info.height - len(info.cell.lines));
        elif info.cell.style.valign == VerticalAlignment.MIDDLE:
            info.line = -(info.height - len(info.cell.lines)) // 2

    def _populateColumnInfo(self):
        self._columnInfos = []
        for i in range(len(self._table[0])):
            info = ColumnInfo(i, self._table[0][i]);
            self._resetColumnInfo(info, 0);
            self._columnInfos.append(info);

    def _printTopBorder(self):
        thick = self._table.topBorder == 2;
        print(self._border.topLeft(thick), end="");
        col = 0;
        for info in self._columnInfos:
            if info.cell.merge:
                continue;
            char = self._border.horizontal(thick);
            print(char * info.width, end="");
            col += info.cell.colspan;
            if col < len(self._columnInfos):
                print(self._border.top(thick), end="");
        print(self._border.topRight(thick), end="");
        print();

    def _printBottomBorder(self):
        thick = self._table.rows[-1].borderBottom == 2;
        col = 0;
        print(self._border.bottomLeft(thick), end="");
        for info in self._columnInfos:
            if info.cell.merge:
                continue;
            char = self._border.horizontal(thick);
            print(char * info.width, end="");
            col += info.cell.colspan;
            if col < len(self._columnInfos):
                print(self._border.bottom(thick), end="");
        print(self._border.bottomRight(thick));

    def _printRow(self, row: int):
        for i in range(self._heights[row]):
            for info in self._columnInfos:
                if info.cell.merge:
                    continue;
                print(self._border.vertical(), end="");
                self._printCellContent(info);
            print(self._border.vertical());

    def _printCellContent(self, info: ColumnInfo):
        if 0 <= info.line < len(info.cell.lines):
            line = info.cell.lines[info.line];
        else:
            line = "";
        if info.cell.style.align == HorizontalAlignment.LEFT:
            print(self._pad + line.ljust(info.width - self._table.padding * 2), end=self._pad);
        elif info.cell.style.align == HorizontalAlignment.RIGHT:
            print(self._pad + line.rjust(info.width - self._table.padding * 2), end=self._pad);
        elif info.cell.style.align == HorizontalAlignment.CENTER:
            width = info.width - self._table.padding * 2;
            padLeft = (width - len(line)) // 2;
            padRight = width - len(line) - padLeft;
            print(self._pad + padLeft * " " + line + padRight * " ", end=self._pad);
        info.line += 1;

    def _printRowBorderSegment(self, row: int, col: int, thick: bool):
        info = self._columnInfos[col];
        char = self._border.horizontal(thick);
        print(char * (self._widths[info.col] + self._table.padding * 2), end="");
        if col >= len(self._columnInfos) - 1:
            print(self._border.right(thick), end="");
            return;
        nextInfo = self._columnInfos[col + 1];
        if nextInfo.rowSpanProgress != nextInfo.cell.rowspan - 1:
            print(self._border.right(thick), end="");
            return;
        nextCell = self._table[row + 1][info.col + 1];
        if (nextInfo.cell.merge):
            if nextCell.merge:
                print(self._border.horizontal(thick), end="");
            else:
                print(self._border.top(thick), end="");
        else:
            if nextCell.merge:
                print(self._border.bottom(thick), end="");
            else:
                print(self._border.middle(thick), end="");

    def _printRowBorderContent(self, info: ColumnInfo, thick: bool):
        self._printCellContent(info);
        if info.col < len(self._columnInfos) - 1:
            nextInfo = self._columnInfos[info.col + 1];
            while nextInfo.cell.merge:
                nextInfo = self._columnInfos[nextInfo.col + 1];
            if nextInfo.rowSpanProgress + 1 == nextInfo.cell.rowspan:
                print(self._border.left(thick), end="");
            else:
                print(self._border.vertical(thick), end="");
        else:
            print(self._border.vertical(thick), end="");

    def _printRowBorder(self, row: int):
        if not self._table[row].borderBottom:
            return;
        thick = self._table[row].borderBottom == 2;
        info = self._columnInfos[0];
        if info.rowSpanProgress == info.cell.rowspan - 1:
            print(self._border.left(thick), end="");
        else:
            print(self._border.vertical(thick), end="");

        col = 0;
        while col < len(self._columnInfos):
            info = self._columnInfos[col];
            if info.cell.rowspan == info.rowSpanProgress + 1:
                self._printRowBorderSegment(row, col, thick);
                col += 1;
            elif info.cell.merge:
                col += 1;
            else:
                self._printRowBorderContent(info, thick);
                col += info.cell.colspan;
        print()

    def _prepareRow(self, row: int):
        if row >= len(self._table):
            return;
        for info in self._columnInfos:
            info.rowSpanProgress += 1;
            if info.cell.rowspan == info.rowSpanProgress:
                self._resetColumnInfo(info, row);


