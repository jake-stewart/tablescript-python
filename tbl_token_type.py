from enum import Enum

class TokenType(Enum):
    TEXT = 0;
    COL_SEP = 1;
    ROW_SEP = 2;
    H_MERGE = 3;
    V_MERGE = 4;
    STYLE = 5;
    CODE = 6;
    H_BORDER = 7;
    THICK_H_BORDER = 8;
