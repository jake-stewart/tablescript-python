from typing import List, Tuple
from tbl_style import CellStyle, HorizontalAlignment, VerticalAlignment
import copy

class Content:
    isScript: bool;
    text: str;

    def __init__(self, text: str, isScript=False):
        self.text = text;
        self.isScript = isScript;

    def __str__(self):
        return "Content(%s, isScript=%d)" % (self.text, self.isScript);

class Cell:
    merge: None | Tuple[int, int];
    rowspan: int;
    colspan: int;
    content: List[Content];
    output: str;
    lines: List[str];
    style: CellStyle;

    defaultStyle: CellStyle = CellStyle();
    defaultStyle.align = HorizontalAlignment.LEFT;
    defaultStyle.valign = VerticalAlignment.TOP;
    defaultStyle.padding = 1;

    def __init__(self):
        self.merge = None
        self.lines = []
        self.contents = []
        self.output = "";
        self.rowspan = 1
        self.colspan = 1
        self.style = self.defaultStyle;

    def debug_str(self) -> str:
        fmt = "Cell(merge=%s, lines=%s, rowspan=%d, " + \
                "colspan=%d, style=%s, contents=%s)";
        contents = "";
        for content in self.contents:
            if content.isScript:
                contents += "{" + content.text + "}";
            else:
                contents += content.text
        return fmt % (str(self.merge), str(self.lines), self.rowspan, self.colspan,
                      str(self.style), "'" + contents + "'")

