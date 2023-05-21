from typing import List, Dict, Any
from tbl_cell import Cell, Content
from tbl_table import Table
from tbl_border import BorderStyle
import re
import random
import money
import math
from exec_with_return import exec_with_return

NUMBER_REGEX = r"\$?[0-9]+(\.[0-9]+)?"

class TableExecutor:
    _table: Table;
    _user_functions: Dict[str, Any];
    _globals: Dict[str, Any];
    _locals: Dict[str, Any];
    _col: int;
    _row: int;

    maxWidths: List[int] | None;
    widths: List[int] | None;
    maxWidth: int | None;
    width: int | None;
    padding: int | None;
    border: int | None;
    separator: int | None;

    def execute(self):
        if (self._table.script):
            result = self._execute(self._table.script);
        for i in range(len(self._table)):
            for j in range(len(self._table[0])):
                self._executeCell(i, j);

    def _executeCell(self, row, col):
        self._row = row;
        self._col = col;
        cell = self._table[row][col];
        output = []
        for content in cell.contents:
            if content.isScript:
                result = self._execute(content.text);
                if result is not None:
                    output.append(str(result));
            else:
                output.append(content.text);
        cell.output = "".join(output);

    def __init__(self, table: Table):
        self._table = table;
        borderTypes = {
                "SINGLE": BorderStyle.SINGLE,
                "DOUBLE": BorderStyle.DOUBLE,
                "THICK": BorderStyle.THICK,
                "ASCII": BorderStyle.ASCII,
                "THICK_ASCII": BorderStyle.THICK_ASCII,
                "DOTTED": BorderStyle.DOTTED,
                "ROUND": BorderStyle.ROUND,
                "BLOCK": BorderStyle.BLOCK,
                "DASHED": BorderStyle.DASHED,
                "THICK_DASHED": BorderStyle.THICK_DASHED,
        };
        self._user_functions = {
             **borderTypes,
             "maxwidths": self._funcMaxWidths,
             "widths": self._funcWidths,
             "maxwidth": self._funcMaxWidth,
             "width": self._funcWidth,
             "padding": self._funcPadding,
             "colsum": self._funcColSum,
             "rowsum": self._funcRowSum,
             "colprod": self._funcColProd,
             "rowprod": self._funcRowProd,
             "cell": self._funcCell,
             "colavg": self._funcColAvg,
             "rowavg": self._funcRowAvg,
             "colrange": self._funcColRange,
             "rowrange": self._funcRowRange,
             "border": self._funcBorder,
             "separator": self._funcSeparator,
             "round": round,
             "range": range,
             "min": min,
             "max": max,
             "sum": sum,
             "str": str,
             "int": int,
             "float": float,
             "list": list,
             "dict": dict,
             "input": input,
             "random": random,
             "math": math,
             "randint": random.randint,
             "money": money.Money,
             "map": map,
             "filter": filter,
             "any": any,
             "all": all,
         }
        self._globals = {"__builtins__": self._user_functions}
        self._locals = self._globals.copy()
        self.maxWidths = None;
        self.maxWidth = None;
        self.width = None;

    def _execute(self, code):
        try:
            return exec_with_return(code, self._globals, self._globals)
        except Exception as e:
            return e.__class__.__name__ + ": " + str(e)

    def _funcCell(self, col, row):
        if col < 1 or row < 1 or row > len(self._table) or col > len(self._table[0]):
            raise IndexError("Cell of bounds")
        cell = self._table[row - 1][col - 1];
        return self._extractNumber(cell);

    def _funcMaxWidths(self, *args):
        maxWidths = [];
        for arg in args:
            maxWidths.append(int(arg));
        self.maxWidths = maxWidths;

    def _funcWidths(self, *args):
        widths = [];
        for arg in args:
            widths.append(int(arg));
        self.widths = widths;

    def _funcMaxWidth(self, maxWidth):
        maxWidth = int(maxWidth)
        if maxWidth > 0:
            self.maxWidth = maxWidth;

    def _funcWidth(self, width):
        width = int(width)
        if width > 0:
            self.width = width;

    def _funcPadding(self, padding):
        if padding is None:
            padding = 0
        self.padding = int(padding);

    def _funcRowRange(self, n_columns=0):
        n_columns = abs(n_columns);
        if not n_columns:
            n_columns = len(self._table[0]);
        nums = [];
        col = self._col;
        while col and n_columns > 0:
            col -= 1
            cell = self._table[self._row][col];
            if cell.merge:
                continue;
            num = self._extractNumber(cell);
            if num is not None:
                nums.append(num);
            n_columns -= 1;
        for num in reversed(nums):
            yield num;

    def _funcColRange(self, n_rows=0):
        n_rows = abs(n_rows);
        if not n_rows:
            n_rows = len(self._table);
        nums = [];
        row = self._row;
        while row and n_rows > 0:
            row -= 1;
            cell = self._table[row][self._col];
            if cell.merge:
                continue;
            num = self._extractNumber(cell);
            if num is not None:
                nums.append(num);
            n_rows -= 1;
        for num in reversed(nums):
            yield num;

    def _extractNumberFromString(self, string: str) -> None | money.Money | int | float:
        match = re.search(NUMBER_REGEX, string);
        if not match:
            return;
        number = match.group(0);
        if "$" in number:
            return money.Money(number[1:]);
        elif "." in number:
            return float(number);
        else:
            return int(number);

    def _extractNumber(self, cell: Cell) -> None | money.Money | int | float:
        if cell.output:
            num = self._extractNumberFromString(cell.output);
            if num is not None:
                return num
        for content in cell.contents:
            if content.isScript:
                continue;
            num = self._extractNumberFromString(content.text);
            if num is not None:
                return num

    def _funcColSum(self, n=0):
        return sum(self._funcColRange(n));

    def _funcColProd(self, n=0):
        return math.prod(self._funcColRange(n));

    def _funcColAvg(self, n=0):
        total = 0;
        i = 0;
        for i, val in enumerate(self._funcColRange(n)):
            total += val;
        return total / (i + 1);

    def _funcRowAvg(self, n=0):
        total = 0;
        i = 0;
        for i, val in enumerate(self._funcRowRange(n)):
            total += val;
        return total / (i + 1);

    def _funcRowSum(self, n=0):
        return sum(self._funcRowRange(n))

    def _funcRowProd(self, n=0):
        return math.prod(self._funcRowRange(n))

    def _funcBorder(self, border):
        border = int(border)
        if not 0 <= border < len(BorderStyle):
            raise KeyError("Invalid border")
        self.border = border

    def _funcSeparator(self, separator):
        separator = int(separator)
        if not 0 <= separator < len(BorderStyle):
            raise KeyError("Invalid separator")
        self.separator = separator
