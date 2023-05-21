from tbl_cell import Cell
from typing import List

class Row:
    cells: List[Cell];
    borderBottom: int;

    def __init__(self):
        self.cells = [];
        self.borderBottom = False;

    def __getitem__(self, idx: int) -> Cell:
        return self.cells[idx];

    def __iter__(self):
        return self.cells.__iter__();

    def __len__(self) -> int:
        return len(self.cells);

class Table:
    rows: List[Row];
    script: str | None;
    padding: int;
    topBorder: int;

    def __init__(self):
        self.script = None;
        self.topBorder = 1;
        self.padding = 1;
        self.rows = [];

    def __len__(self) -> int:
        return len(self.rows);

    def __getitem__(self, idx: int) -> Row:
        return self.rows[idx];

    def __iter__(self):
        return self.rows.__iter__();

    def append(self, row: Row) -> None:
        self.rows.append(row);
