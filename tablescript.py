#!/bin/python3

from money import Money
from constants import *
from tablescript_lexer import TablescriptLexer
from exec_with_return import exec_with_return
import re
from math import prod
from random import random, randint

def extract_number(string):
    match = re.search(NUMBER_REGEX, string)
    if not match:
        return 0

    number = match.group(0)
    if "$" in number:
        return Money(number[1:])
    elif "." in number:
        return float(number)
    else:
        return int(number)

class TablescriptParser:
    def __init__(self):
        self.lexer = TablescriptLexer()

        # dict of allowed functions used in scripting
        self.user_functions = {
              "col_sum": self.col_sum,      "row_sum": self.row_sum,
             "col_prod": self.col_prod,    "row_prod": self.row_prod,
                  "col": self.col,              "row": self.row,
              "col_avg": self.col_avg,      "row_avg": self.row_avg,
            "col_range": self.col_range,  "row_range": self.row_range,
                "round": round,               "range": range,
                  "min": min,                   "max": max,
                  "sum": sum,                   "str": str,
                  "int": int,                 "float": float,
                 "list": list,                 "dict": dict,
                "input": input,              "random": random,
              "randint": randint,             "money": Money,
                  "map": map
        }

    def parse(self, script):
        debug = False
        empty = True
        self.reset()
        self.add_row()

        for lexeme, token in zip(*self.lexer.parse(script)):
            if lexeme == STRING_LEX:
                if debug: print("string:", token)

                empty = False
                self.contents += token

            elif lexeme == SEPARATOR_LEX:
                if debug: print("separator")

                self.add_cell()

            elif lexeme == NEWLINE_LEX:
                if debug: print("new line")

                if not empty:
                    self.add_cell()
                    self.finish_row()
                    self.add_row()
                empty = True

            elif lexeme == H_MERGE_LEX:
                if debug: print("horizontal merge")

                if self.allowed_h_merge:
                    self.horizontal_merge = True
                else:
                    self.contents += H_MERGE_OP

            elif lexeme == V_MERGE_LEX:
                if debug: print("vertical merge")

                if self.allowed_v_merges[self.column_n]:
                    self.vertical_merge = True
                else:
                    self.contents += V_MERGE_OP

            elif lexeme == CONFIG_LEX:
                if debug: print("config:", token)

                self.parse_config(token)
            
            elif lexeme == CODE_LEX:
                if debug: print("code:", token)

                output = self.run_code(token)
                if output is not None:
                    empty = False
                    self.contents += output
            
            elif lexeme == END_LEX:
                if debug: print("end")
                if self.n_rows == 1 and self.n_columns == 0 and empty:
                    self.n_rows -= 1
                self.add_cell()
                self.finish_row()


        self.apply_word_wrap()
        return self.construct_table()

    def run_code(self, code):
        try:
            output = exec_with_return(code, self.globals, self.globals)
        except Exception as e:
            return e.__class__.__name__ + ": " + str(e)

        if output is None:
            return output

        output = str(output)

        start_idx = 0
        while output[start_idx] == "\n":
            start_idx += 1

        end_idx = len(output) - 1
        while output[end_idx] == "\n":
            end_idx -= 1

        formatted_output = ""
        for line in str(output[start_idx:end_idx + 1]).split("\n"):
            if not line:
                formatted_output += " \n "
                continue
            i = 0
            while line[i] == " ":
                i += 1
            formatted_output += i * "\\s" + line[i:] + " \n "
        return formatted_output[:-3]

    def add_cell_text(self, text):
        self.cell_contents[self.column_n][-1] += text

    def finish_row(self):
        for column_n in range(self.column_n, self.n_columns):
            self.add_cell()

    def reset(self):
        self.char = ""

        # keeps track of current character in string for parsing through it
        self.index = 0


        self.globals = {"__builtins__": self.user_functions}
        self.locals = self.globals.copy()

        self.column_n = 0
        self.word = ""
        self.contents = ""

        self.iterations = 0

        self.full_merge = False

        # each cell will have a default configuration
        self.default_config = DEFAULT_CONFIG.copy()

        self.config = DEFAULT_CONFIG.copy()

        self.row_config_exists = True

        # however, if you apply a configuration along all cells in a column,
        # it will use the column's default config as its default config
        # this is a list of lists, one list for each column
        self.default_column_configs = [self.default_config.copy()]

        # the same applies applying configuration along rows
        # however, we only need to remember the current row default config
        # since we parse one row at a time.
        self.row_config = [None, None, None, None, None]

        # this contains a list of lists, one for each column.
        # each sublist contains the configuration for each cell of each column
        self.cell_configs = []

        # this contains a list of lists, one for each column.
        # each sublist contains the words contained in each cell of each column
        # self.column_words = []
        self.cell_contents = []

        # this contains a list of lists, one for each column.
        # each sublist contains the lines generated after word wrapping for
        # each cell of each column
        self.cell_lines = []

        # TODO: is this correct?
        # list of lists, one for each row. stores how many columns each cell spans
        self.column_spans = []

        # TODO: is this correct?
        # list of lists, one for each column. stores how many rows each cell spans
        self.row_spans = []

        self.default_min_height = DEFAULT_MIN_HEIGHT
        self.min_heights = [self.default_min_height]
        self.max_widths = [0]

        self.words = []

        self.starter_width = 0
        self.vertical_merge = False
        self.horizontal_merge = False

        self.allowed_v_merges = [False, False]
        self.allowed_h_merge = False

        self.border_style = DEFAULT_STYLE
        self.corner_style = DEFAULT_STYLE

        self.n_columns = 0
        self.n_rows = 0

    def apply_config(self, setting, span, value):
        # self.cell_configs[self.column_n][-1][setting] = value
        self.config[setting] = value

        if span == COLUMN_SPAN:
            self.default_column_configs[self.column_n][setting] = value

        elif span == ROW_SPAN:
            if not self.row_config_exists:
                self.row_config_exists = True
                self.clear_row_config()
            self.row_config[setting] = value

        elif span == COLUMN_ROW_SPAN:
            for column_n in range(self.column_n, self.n_columns):
                self.default_column_configs[column_n][setting] = value
            self.default_config[setting] = value

    def clear_row_config(self):
        for i in range(len(self.row_config)):
            self.row_config[i] = None

    def add_cell(self):
        if self.column_n == self.n_columns:
            self.allowed_v_merges.append(False)

            self.default_column_configs.append(self.default_config.copy())

            new_rows = self.n_rows - 1
            self.iterations += new_rows
            self.cell_contents.append(["" for i in range(new_rows)])
            self.row_spans.append([0 for i in range(new_rows)])
            self.column_spans.append([0 for i in range(new_rows)])
            self.cell_configs.append([self.default_config.copy() for i in range(new_rows)])
            self.max_widths.append(self.starter_width)
            self.n_columns += 1

        if self.vertical_merge:
            if self.contents.strip():
                self.cell_contents[self.column_n][-1] += " \n " + self.contents
            self.row_spans[self.column_n][-1] += 1
            self.column_n += self.column_spans[self.column_n][-1] + 1

        elif self.horizontal_merge:
            if self.contents.strip():
                self.cell_contents[self.column_n - 1][-1] += " " + self.contents
            self.column_spans[self.last_column][-1] += 1
            self.allowed_v_merges[self.column_n] = False
            self.column_n += 1

        else:
            self.cell_configs[self.column_n].append(
                self.config
            )
            self.full_merge = False
            self.row_spans[self.column_n].append(0)
            self.column_spans[self.column_n].append(0)
            self.last_column = self.column_n
            self.cell_contents[self.column_n].append(self.contents)
            self.allowed_h_merge = True
            self.allowed_v_merges[self.column_n] = True
            self.column_n += 1
            self.iterations += 1
            self.config = self.default_column_configs[self.column_n].copy()
            if self.row_config_exists:
                for i, option in enumerate(self.row_config):
                    if option == None:
                        continue
                    self.config[i] = option

        self.horizontal_merge = False
        self.vertical_merge = False
        self.contents = ""
        self.allowed_h_merge = True

    def add_row(self):
        if self.full_merge:
            column_n = 0
            while column_n < self.n_columns:
                self.row_spans[column_n][-1] -= 1
                column_n += self.column_spans[column_n][-1] + 1
        else:
            self.n_rows += 1

        self.row_config_exists = False
        self.full_merge = True
        self.column_n = 0
        self.config = self.default_column_configs[0].copy()
        self.allowed_h_merge = False
        self.min_heights.append(self.default_min_height)

    def parse_config(self, config):
        span = CELL_SPAN
        last_span = CELL_SPAN

        # an argument that can affect configurations.
        # e.g., 4B will set the border config to value of 4
        num_arg = "0"

        for char in config:
            if char in NUMS:
                num_arg += char

            else:
                num = int(num_arg)
                num_arg = "0"

                if char == ">":
                    if last_span == COLUMN_SPAN:
                        span = COLUMN_ROW_SPAN
                    else:
                        span = ROW_SPAN
                    last_span = ROW_SPAN

                elif char == "v":
                    if last_span == ROW_SPAN:
                        span = COLUMN_ROW_SPAN
                    else:
                        span = COLUMN_SPAN
                    last_span = COLUMN_SPAN

                elif char == "?":
                    span = CELL_SPAN
                    last_span = CELL_SPAN

                else:
                    last_span = CELL_SPAN

                    if char == "B":
                        self.set_border_style(num)
                        self.set_corner_style(num)

                    elif char == "C":
                        self.set_corner_style(num)

                    elif char == "w":
                        self.set_width(span, num)

                    elif char == "h":
                        self.set_height(span, num)

                    # d stands for default config
                    elif char == "d":
                        self.reset_config(span)

                    elif char == "l":
                        self.apply_config(H_ALIGN, span, LEFT_ALIGN)

                    elif char == "c":
                        self.apply_config(H_ALIGN, span, CENTER_ALIGN)

                    elif char == "r":
                        self.apply_config(H_ALIGN, span, RIGHT_ALIGN)

                    elif char == "t":
                        self.apply_config(V_ALIGN, span, TOP_ALIGN)

                    elif char == "m":
                        self.apply_config(V_ALIGN, span, MIDDLE_ALIGN)

                    elif char == "b":
                        self.apply_config(V_ALIGN, span, BOTTOM_ALIGN)

                    elif char == "L":
                        self.apply_config(L_PAD, span, num)

                    elif char == "R":
                        self.apply_config(R_PAD, span, num)

                    elif char == "s":
                        self.apply_config(SEPARATED, span, 1)

                    elif char == "j":
                        self.apply_config(SEPARATED, span, 0)


    def reset_config(self, span):
        self.min_heights[-1] = DEFAULT_MIN_HEIGHT
        self.config = DEFAULT_CONFIG.copy()

        if span == COLUMN_SPAN:
            self.default_column_configs[column_n] = DEFAULT_CONFIG.copy()

        elif span == ROW_SPAN:
            self.row_config = DEFAULT_CONFIG.copy()
            self.row_config_exists = True

        elif span == COLUMN_ROW_SPAN:
            # why n columns + 1? because there should always exist a  config for the next column so when a cell
            # is created it can use its default config of that column
            self.default_column_configs = [DEFAULT_CONFIG.copy() for i in range(self.n_columns + 1)]
            self.default_config = DEFAULT_CONFIG.copy()
            self.default_min_height = DEFAULT_MIN_HEIGHT

    def set_height(self, span, height):
        self.min_heights[-1] = height
        if span == ROW_SPAN or span == COLUMN_ROW_SPAN:
            self.default_min_height = height

    def set_width(self, span, width):
        if span == ROW_SPAN or span == COLUMN_ROW_SPAN:
            for i in range(self.column_n, len(self.max_widths)):
                self.max_widths[i] = width
                self.starter_width = width
        else:
            self.max_widths[self.column_n] = width

    def set_corner_style(self, style_idx):
        self.corner_style = style_idx

    def set_border_style(self, style_idx):
        self.border_style = style_idx

    # XXX: this method is a huge mess and needs to be cleaned up
    def apply_word_wrap(self):
        self.heights = []
        for i, min_height in enumerate(self.min_heights):
            if min_height <= 0:
                self.heights.append(default_min_height)
            else:
                self.heights.append(min_height)

        self.widths = []
        for i, max_width in enumerate(self.max_widths):
            if max_width <= 0:
                self.max_widths[i] = DEFAULT_MAX_WIDTH
                self.widths.append(DEFAULT_MIN_WIDTH)
            else:
                self.widths.append(max_width)

        self.cell_lines = [[[] for cell_n in range(len(self.row_spans[column_n]))] for column_n in range(self.n_columns)]
        column_span_cells = [[] for i in range(self.n_columns)]
        row_span_cells = []

        row_pointers = [0 for i in range(self.n_columns)]
        cell_pointers = [0 for i in range(self.n_columns)]


        self.full_joins = [1 for i in range(self.n_rows)]

        for row_n in range(self.n_rows):
            for column_n in range(self.n_columns):
                if row_n != row_pointers[column_n]:
                    continue

                cell_n = cell_pointers[column_n]
                cell_pointers[column_n] += 1

                column_span = self.column_spans[column_n][cell_n]
                if column_span:
                    if self.cell_configs[column_n][cell_n][SEPARATED]:
                        self.full_joins[row_n] = 0
                    column_span_cells[column_n].append((column_n, row_n, cell_n))
                    row_span = self.row_spans[column_n][cell_n] + 1
                    for column_span_n in range(column_span + 1):
                        row_pointers[column_n + column_span_n] += row_span
                    continue

                row_pointers[column_n] += 1

                words = []


                height = 0
                l_pad = self.cell_configs[column_n][cell_n][L_PAD]
                r_pad = self.cell_configs[column_n][cell_n][R_PAD]
                max_width = self.max_widths[column_n]
                pad = l_pad + r_pad
                width = pad
                inner_width = max_width - 1 - pad

                word_break_char = WORD_BREAK_CHAR
                new_word_new_line = False
                if inner_width < 0:
                    self.cell_configs[column_n][cell_n][L_PAD] = 0
                    self.cell_configs[column_n][cell_n][R_PAD] = 0
                    pad = 0
                    width = 0
                    inner_width = max_width - 1

                if inner_width == 0:
                    inner_width += 1
                    new_word_new_line = True
                    word_break_char = ""

                if not words:
                    line = ""


                for word in self.cell_contents[column_n][cell_n].split(" "):
                    if not word:
                        continue
                    word = word.replace("\s", " ")
                    if word == "\n":
                        self.cell_lines[column_n][cell_n].append(line)
                        height += 1
                        if pad + len(line) > self.widths[column_n]:
                             self.widths[column_n] = pad + len(line)
                        line = ""
                        width = pad
                        continue

                    if width > pad:
                        new_width = width + len(word) + 1
                    else:
                        new_width = pad + len(word)

                    if new_width <= max_width:
                        if width > pad:
                            line = line + SPACE + word
                        else:
                            line = word
                        width = new_width
                        continue
                    
                    if width > pad:
                        self.cell_lines[column_n][cell_n].append(line)
                        if new_word_new_line:
                            self.cell_lines[column_n][cell_n].append("")
                            height += 1
                        height += 1
                        if width > self.widths[column_n]:
                             self.widths[column_n] = width
                        line = ""

                    width = pad + len(word)

                    while width > max_width:
                        self.widths[column_n] = max_width
                        line, word = word[:inner_width], word[inner_width:]
                        height += 1
                        self.cell_lines[column_n][cell_n].append(line + word_break_char)
                        width = pad + len(word)

                    if word:
                        line = word

                self.cell_lines[column_n][cell_n].append(line)
                height += 1
                if width > self.widths[column_n]:
                     self.widths[column_n] = width
                row_span = self.row_spans[column_n][cell_n]
                if row_span:
                    row_span_cells.append((column_n, row_n, cell_n))
                    row_pointers[column_n] += row_span
                else:
                    if self.cell_configs[column_n][cell_n][SEPARATED]:
                        self.full_joins[row_n] = 0
                    if height > self.heights[row_n]:
                        self.heights[row_n] = height


        for column in reversed(column_span_cells):
            for column_n, row_n, cell_n in column:
                height = 0

                l_pad = self.cell_configs[column_n][cell_n][L_PAD]
                r_pad = self.cell_configs[column_n][cell_n][R_PAD]
                pad = l_pad + r_pad
                width = pad

                if not words:
                    line = ""

                column_span = self.column_spans[column_n][cell_n]
                min_width = column_span + sum(self.widths[column_n:column_n + column_span + 1])
                max_width = min_width + self.max_widths[column_n] - self.widths[column_n]
                extra_space = self.max_widths[column_n] - (max_width - min_width)
                inner_width = max_width - 1 - pad


                word_break_char = WORD_BREAK_CHAR
                new_word_new_line = False
                if inner_width < 0:
                    self.cell_configs[column_n][cell_n][L_PAD] = 0
                    self.cell_configs[column_n][cell_n][R_PAD] = 0
                    pad = 0
                    width = 0
                    inner_width = max_width - 1

                if inner_width == 0:
                    inner_width += 1
                    new_word_new_line = True
                    word_break_char = ""

                for word in self.cell_contents[column_n][cell_n].split(" "):
                    if not word:
                        continue
                    word = word.replace("\s", " ")
                    if word == "\n":
                        self.cell_lines[column_n][cell_n].append(line)
                        height += 1
                        used_extra_space = width - min_width
                        if used_extra_space > 0:
                            self.widths[column_n] += used_extra_space
                            min_width += used_extra_space
                        line = ""
                        width = pad
                        continue

                    if width > pad:
                        new_width = width + len(word) + 1
                    else:
                        new_width = pad + len(word)

                    if new_width <= max_width:
                        if width > pad:
                            line = line + SPACE + word
                        else:
                            line = word
                        width = new_width
                        continue
                    
                    if width > pad:
                        self.cell_lines[column_n][cell_n].append(line)
                        if new_word_new_line:
                            self.cell_lines[column_n][cell_n].append("")
                            height += 1
                        height += 1
                        used_extra_space = width - min_width
                        if used_extra_space > 0:
                            self.widths[column_n] += used_extra_space
                            min_width += used_extra_space
                        line = ""

                    width = pad + len(word)

                    while width > max_width:
                        self.widths[column_n] = self.max_widths[column_n]
                        line, word = word[:inner_width], word[inner_width:]
                        height += 1
                        self.cell_lines[column_n][cell_n].append(line + word_break_char)
                        width = pad + len(word)

                    if word:
                        line = word

                if line:
                    self.cell_lines[column_n][cell_n].append(line)
                    height += 1
                used_extra_space = width - min_width
                if used_extra_space > 0:
                    self.widths[column_n] += used_extra_space
                    min_width += used_extra_space
                if height > self.heights[row_n]:
                    self.heights[row_n] = height

        for column_n, row_n, cell_n in row_span_cells:
            row_span = self.row_spans[column_n][cell_n]
            # height = row_span
            height = 0
            if self.cell_configs[column_n][cell_n][SEPARATED]:
                self.full_joins[row_n] = 0

            for row_span_n in range(row_span + 1):
                height += self.heights[row_n + row_span_n]

            for row_span_n in range(row_span):
                if not self.full_joins[row_n + row_span_n + 1]:
                    height += 1

            n_lines = len(self.cell_lines[column_n][cell_n])
            if height < n_lines:
                self.heights[row_n] += n_lines - height

    # XXX: this method is a huge mess and needs to be cleaned up
    def construct_table(self):
        cell_pointers = [0 for i in range(self.n_columns)]
        width_pointers = cell_pointers.copy()
        height_pointers = cell_pointers.copy()
        border_pointers = cell_pointers.copy()
        row_pointers = cell_pointers.copy()
        spacing_pointers = cell_pointers.copy()
        line_pointers = [-1 for i in range(self.n_columns)]

        column_n = 0
        cell_n = 0

        if self.border_style >= len(BORDER_STYLES):
            border_n = DEFAULT_BORDER_STYLE
        if self.corner_style >= len(CORNER_STYLES):
            corner_n = DEFAULT_BORDER_STYLE

        border_style = BORDER_STYLES[self.border_style]
        corner_style = CORNER_STYLES[self.corner_style]

        string = corner_style[0]

        # full_joins = [0 for i in range(self.n_rows)]

        while column_n < self.n_columns:
            column_span = self.column_spans[column_n][0] + 1
            width = sum(self.widths[column_n:column_n + column_span]) + column_span - 1
            width_pointers[column_n] = width

            row_span = self.row_spans[column_n][0] + 1
            height = sum(self.heights[0:row_span]) - 1
            for row_span_n in range(row_span - 1):
                if not self.full_joins[row_span_n + 1]:
                    height += 1
            height_pointers[column_n] = height

            v_align = self.cell_configs[column_n][0][V_ALIGN]
            if v_align == TOP_ALIGN:
                spacing_pointers[column_n] = 0
            elif v_align == MIDDLE_ALIGN:
                spacing = ((height + 1) - len(self.cell_lines[column_n][0])) // 2
                spacing_pointers[column_n] = spacing
            else:
                spacing = (height + 1) - len(self.cell_lines[column_n][0])
                spacing_pointers[column_n] = spacing

            line_pointers[column_n] = 0

            string += border_style[0] * width
            column_n += column_span
            if column_n == self.n_columns:
                string += corner_style[1] + "\n"
            else:
                string += corner_style[6]


        column_n = 0
        i = 0
        previous_border = False
        while i < self.iterations:
            cell_n = cell_pointers[column_n]

            column_span = self.column_spans[column_n][cell_n]
            next_column_n = column_n + column_span + 1

            if line_pointers[column_n] == -1:
                row_n = row_pointers[column_n]

                column_span += 1
                width = sum(self.widths[column_n:column_n + column_span]) + column_span - 1
                width_pointers[column_n] = width

                row_span = self.row_spans[column_n][cell_n] + 1
                height = sum(self.heights[row_n:row_n + row_span]) - 1
                for row_span_n in range(row_span - 1):
                    if not self.full_joins[row_n + row_span_n + 1]:
                        height += 1
                height_pointers[column_n] = height

                v_align = self.cell_configs[column_n][cell_n][V_ALIGN]
                if v_align == 0:
                    spacing_pointers[column_n] = 0
                elif v_align == 1:
                    spacing = ((height + 1) - len(self.cell_lines[column_n][cell_n])) // 2
                    spacing_pointers[column_n] = spacing
                else:
                    spacing = (height + 1) - len(self.cell_lines[column_n][cell_n])
                    spacing_pointers[column_n] = spacing
                line_pointers[column_n] += 1
                if self.full_joins[row_n]:
                    continue
                above = border_pointers[column_n]
                if above: 
                    if previous_border:
                        if self.cell_configs[column_n][cell_n][SEPARATED]:
                            string += corner_style[8]
                        else:
                            string += corner_style[5]
                    else:
                        if self.cell_configs[column_n][cell_n][SEPARATED]:
                            string += corner_style[4]
                        else:
                            string += border_style[1]
                else: string += corner_style[6]
                #string += "X"
                if self.cell_configs[column_n][cell_n][SEPARATED]:
                    string += border_style[0] * self.widths[column_n]
                    previous_border = True
                else:
                    string += SPACE * self.widths[column_n]
                    previous_border = False
                for column_span_n in range(column_span - 1):
                    above = border_pointers[column_n + column_span_n + 1]
                    if above: string += corner_style[7]
                    else: string += border_style[0]
                    string += border_style[0] * self.widths[column_n + column_span_n + 1]

            else:
                border_pointers[column_n] = 1
                for column_span_n in range(column_span):
                    border_pointers[column_n + column_span_n + 1] = 0

                if previous_border:
                    string += corner_style[5]
                else:
                    string += border_style[1]

                width = width_pointers[column_n]
                line_n = line_pointers[column_n]

                spacing = spacing_pointers[column_n]
                if line_n >= spacing:
                    try:
                        line = self.cell_lines[column_n][cell_n][line_n - spacing]
                    except IndexError:
                        line = ""
                else:
                    line = ""

                l_pad = self.cell_configs[column_n][cell_n][L_PAD]
                r_pad = self.cell_configs[column_n][cell_n][R_PAD]
                align = self.cell_configs[column_n][cell_n][H_ALIGN]
                if align == 0:
                    spacing = width_pointers[column_n] - len(line) - l_pad
                    string += l_pad * SPACE + line + spacing * SPACE
                elif align == 1:
                    spacing = width_pointers[column_n] - len(line) - l_pad - r_pad
                    spacing_left = spacing // 2
                    spacing_right = spacing - spacing_left
                    string += (l_pad + spacing_left) * SPACE + line + (spacing_right + r_pad) * SPACE
                else:
                    spacing = width_pointers[column_n] - len(line) - r_pad
                    string += spacing * SPACE + line + r_pad * SPACE
                if line_pointers[column_n] == height_pointers[column_n]:
                    row_span = self.row_spans[column_n][cell_n] + 1
                    for column_span_n in range(column_span + 1):
                        row_pointers[column_n + column_span_n] += row_span
                    line_pointers[column_n] = -1
                    cell_pointers[column_n] += 1
                    i += 1
                else:
                    line_pointers[column_n] += 1
                previous_border = False

            column_n = next_column_n

            if column_n == self.n_columns:
                column_n = 0
                if previous_border:
                    string += corner_style[5] + "\n"
                else:
                    string += border_style[1] + "\n"
                previous_border = False

        string += corner_style[2]
        while column_n < self.n_columns:
            #string += "X"
            string += border_style[0] * width_pointers[column_n]
            column_n += self.column_spans[column_n][-1] + 1
            if column_n == self.n_columns:
                string += corner_style[3]
            else:
                string += corner_style[7]

        return string

    def row_range(self, n_columns=0):
        n_columns = abs(n_columns)

        if not n_columns:
            n_columns = self.n_columns

        nums = []
        col = self.column_n
        while col and n_columns > 0:
            col -= 1
            if not self.row_spans[col][-1]:
                contents = self.cell_contents[col][-1]
                nums.append(extract_number(contents))
                n_columns -= 1

        for num in reversed(nums):
            yield num

    def col_range(self, n=0):
        n_rows = len(self.cell_contents[self.column_n])
        n = abs(n)

        if not n or n > n_rows:
            n = n_rows

        for row in range(n_rows - n, n_rows):
            contents = self.cell_contents[self.column_n][row]
            yield extract_number(contents)

    def col_sum(self, n=0):
        return sum(self.col_range(n))

    def col_prod(self, n=0):
        return prod(self.col_range(n))

    def col_avg(self, n=0):
        total = 0
        for i, val in enumerate(self.col_range(n)):
            total += val
        return total / (i + 1)

    def row_avg(self, n=0):
        total = 0
        for i, val in enumerate(self.row_range(n)):
            total += val
        return total / (i + 1)

    def row_sum(self, n=0):
        return sum(self.row_range(n))

    def row_prod(self, n=0, precise=False):
        return prod(self.row_range(n))

    def col(self, n=0):
        n = abs(n)
        if not n:
            n = 1

        contents = self.cell_contents[self.column_n - n][-1]
        return extract_number(contents)


    def row(self, n=0):
        if not n:
            n = 1
        val = self.column_words[-1][-n][0]
        if val.startswith("$"):
            val = val[1:]
        if "." in val:
            return float(val)
        return int(val)



if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        print("usage: tablescript.py <table.tbl>")
        exit(1)

    try:
        with open(sys.argv[1]) as f:
            script = f.read()
    except FileNotFoundError:
        print(sys.argv[1], "not found.")

    ts_parser = TablescriptParser()
    table = ts_parser.parse(script)
    print(table)
