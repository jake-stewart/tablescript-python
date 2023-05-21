from tbl_style import CellStyle, VerticalAlignment, HorizontalAlignment
from tbl_cell import Cell
import copy
from typing import Dict, Callable

class CellStyleParser:
    _configLookup: Dict[str, Callable];
    _style: CellStyle;

    def __init__(self):
        self._configLookup = {
            "l": self._leftAlign,
            "r": self._rightAlign,
            "c": self._centerAlign,
            "t": self._topAlign,
            "m": self._middleAlign,
            "b": self._bottomAlign,
        };

    def parse(self, schema: str) -> CellStyle:
        self._style = copy.copy(Cell.defaultStyle);
        for c in schema:
            callback = self._configLookup.get(c, None);
            if callback:
                callback();
        return self._style;

    def _leftAlign(self):
        self._style.align = HorizontalAlignment.LEFT;

    def _rightAlign(self):
        self._style.align = HorizontalAlignment.RIGHT;

    def _centerAlign(self):
        self._style.align = HorizontalAlignment.CENTER;

    def _topAlign(self):
        self._style.valign = VerticalAlignment.TOP;

    def _middleAlign(self):
        self._style.valign = VerticalAlignment.MIDDLE;

    def _bottomAlign(self):
        self._style.valign = VerticalAlignment.BOTTOM;
