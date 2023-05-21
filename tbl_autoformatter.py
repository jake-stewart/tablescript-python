from tbl_table import Table
from tbl_cell import Cell
from tbl_style import HorizontalAlignment
import re
import copy

NUMBER_REGEX = r"\s*\$?[0-9]+(\.[0-9]+)?\s*";

class TableAutoFormatter:
    def __init__(self, table: Table):
        self._table = table;

    def format(self):
        for i, row in enumerate(self._table):
            for j, cell in enumerate(row):
                if not cell.merge and not self._table[i].borderBottom:
                    if cell.colspan > 1 or cell.rowspan > 1:
                        self._table[i].borderBottom = 1;
                        if i > 0 and not self._table[i - 1].borderBottom:
                            self._table[i - 1].borderBottom = 1;
                if cell.style != Cell.defaultStyle:
                    continue;
                self._formatCell(cell);

    def _formatCell(self, cell: Cell):
        if len(cell.lines) != 1:
            return;
        if re.match(NUMBER_REGEX, cell.lines[0]):
            cell.style = copy.copy(Cell.defaultStyle);
            cell.style.align = HorizontalAlignment.RIGHT;

