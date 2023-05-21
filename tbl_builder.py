from typing import List, Tuple, Dict
from tbl_table import Table, Row
from tbl_style import CellStyle
from tbl_cell import Cell, Content

class TableBuilder:
    _script: str | None;
    _table: Table;

    def __init__(self):
        self._table = Table();

    def getTable(self) -> Table:
        return self._table;

    def setScript(self, script: str | None):
        self._table.script = script;

    def addCellContent(self, row: int, col: int, content: Content):
        self._expandToFit(row, col);
        self._table[row][col].contents.append(content);

    def addCellStyle(self, row: int, col: int, style: CellStyle):
        self._expandToFit(row, col);
        self._table[row][col].style = style;

    def addHorizontalBorder(self, row: int):
        if row == -1:
            self._table.topBorder = 1;
        else:
            self._table[row].borderBottom = 1;

    def addThickHorizontalBorder(self, row: int):
        if row == -1:
            self._table.topBorder = 2;
        else:
            self._table[row].borderBottom = 2;

    def mergeCellWithAbove(self, row: int, col: int) -> None:
        if row == 0:
            return;
        self._merge((row, col), (row - 1, col));

    def mergeCellWithLeft(self, row: int, col: int) -> None:
        if col == 0:
            return;
        self._merge((row, col), (row, col - 1));

    def _merge(self, a: Tuple[int, int], b: Tuple[int, int]) -> None:
        topLeft = min(a, b);
        bottomRight = max(a, b);
        self._expandToFit(bottomRight[0], bottomRight[1]);
        topLeftCell = self._table[topLeft[0]][topLeft[1]];
        if (topLeftCell.merge):
            topLeft = topLeftCell.merge;
            topLeftCell = self._table[topLeft[0]][topLeft[1]];
        topLeftCell.rowspan = max(topLeftCell.rowspan,
                                  bottomRight[0] - topLeft[0] + 1)
        topLeftCell.colspan = max(topLeftCell.colspan,
                                  bottomRight[1] - topLeft[1] + 1)
        for i in range(0, topLeftCell.rowspan):
            for j in range(0, topLeftCell.colspan):
                if i == 0 and j == 0:
                    continue
                mergedCell = self._table[topLeft[0] + i][topLeft[1] + j];
                mergedCell.merge = topLeft;

        for i in range(topLeft[0], topLeft[0] + topLeftCell.rowspan):
            for j in range(topLeft[1], topLeft[1] + topLeftCell.colspan):
                if (i, j) == topLeft:
                    continue
                self._table[i][j].merge = topLeft;

    def _expandToFit(self, row: int, col: int) -> None:
        while row >= len(self._table):
            self._addRow();
        while col >= len(self._table[0]):
            self._addCol();

    def _addRow(self) -> None:
        row = Row();
        cells = row.cells;
        self._table.append(row);
        for _ in range(len(self._table[0])):
            cells.append(Cell());

    def _addCol(self) -> None:
        for row in self._table:
            row.cells.append(Cell());

    def fixFullMerges(self) -> None:
        if len(self._table) == 0:
            return
        self._fixFullRowMerges();
        self._fixFullColumnMerges();

    def _fixFullRowMerges(self) -> None:
        for i in reversed(range(len(self._table))):
            fullMerge = True
            for j in range(len(self._table[0])):
                if not self._table[i][j].merge:
                    fullMerge = False
                    break;
            if fullMerge:
                affectedCells = set();
                for j in range(len(self._table[0])):
                    row, col = self._table[i][j].merge;
                    affectedCells.add(self._table[row][col]);
                del self._table.rows[i];
                for affectedCell in affectedCells:
                    affectedCell.rowspan -= 1

    def _fixFullColumnMerges(self) -> None:
        for i in reversed(range(len(self._table[0]))):
            fullMerge = True
            for j in range(len(self._table)):
                if not self._table[j][i].merge:
                    fullMerge = False
                    break;
            if fullMerge:
                affectedCells = set();
                for j in range(len(self._table)):
                    row, col = self._table[j][i].merge;
                    affectedCells.add(self._table[row][col]);
                    del self._table.rows[j].cells[i];
                for affectedCell in affectedCells:
                    affectedCell.colspan -= 1

