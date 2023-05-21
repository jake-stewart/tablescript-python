from enum import IntEnum

class HorizontalAlignment(IntEnum):
    LEFT = 0;
    CENTER = 1;
    RIGHT = 2;

class VerticalAlignment(IntEnum):
    TOP = 0;
    MIDDLE = 1;
    BOTTOM = 2;

class CellStyle:
    align: HorizontalAlignment;
    valign: VerticalAlignment;
