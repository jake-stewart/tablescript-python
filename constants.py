BORDER_STYLES = [
    [" ", " "],
    ["─", "│"],
    ["━", "┃"],
    ["═", "║"],
    ["-", "|"],
    ["─", "│"],
    ["╌", "┆"],
    ["╍", "┇"],
    ["▀", "█"],
    ["═", "│"],
    ["─", "║"],
]

CORNER_STYLES = [
    [" ", " ", " ", " ", " ", " ", " ", " ", " "],
    ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼"],
    ["┏", "┓", "┗", "┛", "┣", "┫", "┳", "┻", "╋"],
    ["╔", "╗", "╚", "╝", "╠", "╣", "╦", "╩", "╬"],
    ["+", "+", "+", "+", "+", "+", "+", "+", "+"],
    ["╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼"],
    ["┌", "┐", "└", "┘", "├", "┤", "┬", "┴", "┼"],
    ["┏", "┓", "┗", "┛", "┣", "┫", "┳", "┻", "╋"],
    ["█", "█", "▀", "▀", "█", "█", "█", "▀", "█"],
    ["╒", "╕", "╘", "╛", "╞", "╡", "╤", "╧", "╪"],
    ["╓", "╖", "╙", "╜", "╟", "╢", "╥", "╨", "╫"],
]

CONFIG_OP     = "?"
SEPARATOR_OP  = "|"
CODE_BEGIN_OP = "`"
CODE_END_OP   = "`"
ESCAPE_OP     = "\\"
V_MERGE_OP    = "^"
H_MERGE_OP    = "<"
COMMENT_OP    = "#"

SPACE = " "  # space character between words. useful to change to dots if application condenses whitespace
WORD_BREAK_CHAR = "-"

UNWRAPPABLE_SPACE_CHAR = "\s"

NUMBER_REGEX = r"\$?[0-9]+(\.[0-9]+)?"

NUMS = set(
    "0123456789"
)

DEFAULT_MAX_WIDTH  = 50
DEFAULT_MIN_HEIGHT = 1
DEFAULT_MIN_WIDTH  = 1
START_WIDTH        = 0  # XXX: UNUSED

DEFAULT_CONFIG = [
    0,  # h align (0=left, 1=center, 2=right)
    0,  # v align (0=top,  1=middle, 2=bottom)
    1,  # padding left
    1,  # padding right
    1,  # separated (1 = true, 0 = false)
    0,  # column span
    0,  # row span
]

# enum for cell config indexes
H_ALIGN         = 0
V_ALIGN         = 1
L_PAD           = 2
R_PAD           = 3
SEPARATED       = 4
COLUMN_SPAN     = 5
ROW_SPAN        = 6

# enum for vertical text alignment
LEFT_ALIGN      = 0
CENTER_ALIGN    = 1
RIGHT_ALIGN     = 2

# enum for vertical text alignment
TOP_ALIGN       = 0
MIDDLE_ALIGN    = 1
BOTTOM_ALIGN    = 2

# enum for config spans
CELL_SPAN       = 0
COLUMN_SPAN     = 1
ROW_SPAN        = 2
COLUMN_ROW_SPAN = 3

# enum for lexemes
START_LEX = 0
NEWLINE_LEX = 1
STRING_LEX = 2
SEPARATOR_LEX = 3
H_MERGE_LEX = 4
V_MERGE_LEX = 5
CODE_LEX = 6
CONFIG_LEX = 7
END_LEX = 8

# enum for styles
INVISIBLE_STYLE         = 0
DEFAULT_STYLE           = 1
THICK_STYLE             = 2
DOUBLE_STYLE            = 3
ASCII_STYLE             = 4
ROUND_STYLE             = 5
DOTTED_STYLE            = 6
THICK_DOTTED_STYLE      = 7
BLOCK_STYLE             = 8
DOUBLE_HORIZONTAL_STYLE = 9
DOUBLE_VERTICAL_STYLE   = 10
