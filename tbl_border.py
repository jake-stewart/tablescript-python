from typing import List, Dict
from enum import IntEnum

class BorderStyle(IntEnum):
    SINGLE = 0;
    DOUBLE = 1;
    THICK = 2;
    ASCII = 3;
    THICK_ASCII = 4;
    DOTTED = 5;
    ROUND = 6;
    BLOCK = 7;
    DASHED = 8;
    THICK_DASHED = 9;

class BorderType:
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3
    LEFT = 4
    RIGHT = 5
    TOP = 6
    BOTTOM = 7
    MIDDLE = 8
    HORIZONTAL = 9
    VERTICAL = 10

STYLES: Dict[BorderStyle, Dict[BorderStyle, List[str]]] = {
    BorderStyle.SINGLE: {
        BorderStyle.SINGLE: ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "─", "│"],
        BorderStyle.DOUBLE: ["╒", "╕", "╘", "╛", "╞", "╡", "╤", "╧", "╪", "═", "│"],
        BorderStyle.THICK: ["┍", "┑", "┕", "┙", "┝", "┥", "┯", "┷", "┿", "━", "│"],
    },
    BorderStyle.THICK: {
        BorderStyle.THICK: ["┏", "┓", "┗", "┛", "┣", "┫", "┳", "┻", "╋", "━", "┃"],
        BorderStyle.SINGLE: ["┎", "┒", "┖", "┚", "┠", "┨", "┰", "┸", "╂", "─", "┃"],
    },
    BorderStyle.DOUBLE: {
        BorderStyle.DOUBLE: ["╔", "╗", "╚", "╝", "╠", "╣", "╦", "╩", "╬", "═", "║"],
        BorderStyle.SINGLE: ["╓", "╖", "╙", "╜", "╟", "╢", "╥", "╨", "╫", "─", "║"],
    },
    BorderStyle.ROUND: {
        BorderStyle.ROUND: ["╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼", "─", "│"],
        BorderStyle.SINGLE: ["╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼", "─", "│"],
        BorderStyle.DOUBLE: ["╒", "╕", "╘", "╛", "╞", "╡", "╤", "╧", "╪", "═", "│"],
        BorderStyle.THICK: ["┍", "┑", "┕", "┙", "┝", "┥", "┯", "┷", "┿", "━", "│"],
    },
    BorderStyle.ASCII: {
        BorderStyle.ASCII: ["+", "+", "+", "+", "+", "+", "+", "+", "+", "-", "|"],
    },
    BorderStyle.THICK_ASCII: {
        BorderStyle.THICK_ASCII: ["+", "+", "+", "+", "+", "+", "+", "+", "+", "=", "|"],
    },
    BorderStyle.DOTTED: {
        BorderStyle.DOTTED: [".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ":"],
        BorderStyle.ASCII: ["+", "+", "+", "+", "+", "+", "+", "+", "+", "-", ":"],
        BorderStyle.THICK_ASCII: ["+", "+", "+", "+", "+", "+", "+", "+", "+", "=", ":"],
    },
    BorderStyle.DASHED: {
        BorderStyle.DASHED: ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼", "╌", "┆"],
    },
    BorderStyle.THICK_DASHED: {
        BorderStyle.THICK_DASHED: ["┏", "┓", "┗", "┛", "┣", "┫", "┳", "┻", "╋", "╍", "┇"],
    },
    BorderStyle.BLOCK: {
        BorderStyle.BLOCK: ["█", "█", "▀", "▀", "█", "█", "█", "▀", "█", "▀", "█"],
    },
}

class Border:
    _chars: List[List[str]];
    _styleLookup: Dict[BorderStyle, List[str]];
    _style: BorderStyle;

    def __init__(self, style: BorderStyle):
        self._styleLookup = STYLES[style];
        self._chars = [self._styleLookup[style]] * 2;
        self._style = style;

    def setSeparatorStyle(self, separatorStyle: BorderStyle) -> None:
        if separatorStyle in self._styleLookup:
            self._chars[1] = self._styleLookup[separatorStyle];
        else:
            self._chars[1] = STYLES[separatorStyle][separatorStyle];
            self._chars[1][BorderType.VERTICAL] = self._chars[0][BorderType.VERTICAL]
            self._chars[1][BorderType.LEFT] = self._chars[0][BorderType.LEFT]
            self._chars[1][BorderType.RIGHT] = self._chars[0][BorderType.RIGHT]

    def topLeft(self, separator=False):
        return self._chars[separator][BorderType.TOP_LEFT];

    def topRight(self, separator=False):
        return self._chars[separator][BorderType.TOP_RIGHT];

    def bottomLeft(self, separator=False):
        return self._chars[separator][BorderType.BOTTOM_LEFT];

    def bottomRight(self, separator=False):
        return self._chars[separator][BorderType.BOTTOM_RIGHT];

    def left(self, separator=False):
        return self._chars[separator][BorderType.LEFT];

    def right(self, separator=False):
        return self._chars[separator][BorderType.RIGHT];

    def top(self, separator=False):
        return self._chars[separator][BorderType.TOP];

    def bottom(self, separator=False):
        return self._chars[separator][BorderType.BOTTOM];

    def middle(self, separator=False):
        return self._chars[separator][BorderType.MIDDLE];

    def horizontal(self, separator=False):
        return self._chars[separator][BorderType.HORIZONTAL];

    def vertical(self, separator=False):
        return self._chars[separator][BorderType.VERTICAL];
