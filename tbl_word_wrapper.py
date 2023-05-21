from typing import List
import textwrap
from tbl_cell import Cell
from tbl_table import Table

class TableWordWrapper:
    _table: Table;
    _columnWidths: List[int];

    def __init__(self, table: Table):
        self._table = table;

    def wrap(self, columnWidths: List[int]):
        self._columnWidths = columnWidths;
        for i in range(len(self._table)):
            for j in range(len(self._table[i])):
                self._wrapCell(i, j);

    def _wrapCell(self, row: int, col: int):
        cell = self._table[row][col];
        width = sum(self._columnWidths[col:col+cell.colspan]) + cell.colspan - 1 + \
                (cell.colspan - 1) * self._table.padding * 2;
        joined = cell.output;
        i = 0;
        deleteTil = 0;
        while i < len(joined):
            if joined[i] == " ":
                i += 1;
            elif joined[i] == "\n":
                deleteTil = i + 1
                i += 1
            else:
                break;
        if deleteTil:
            joined = joined[deleteTil:]; 
        paragraphs = joined.rstrip().split("\n");
        cell.lines = []
        for paragraph in paragraphs:
            if paragraph:
                wrapped = textwrap.wrap(paragraph, width);
                cell.lines += wrapped;

