import fileinput
from tbl_table import Table
from tbl_lexer import Lexer
from tbl_parser import Parser
from tbl_border import Border, BorderStyle
from tbl_executor import TableExecutor
from tbl_autoformatter import TableAutoFormatter
from tbl_sizer import TableSizer
from tbl_word_wrapper import TableWordWrapper
from tbl_printer import TablePrinter
import sys

if len(sys.argv) == 1:
    try:
        script = ""
        for line in fileinput.input(encoding="utf-8"):
            script += line
    except KeyboardInterrupt:
        print()
        exit()
elif len(sys.argv) == 2:
    try:
        with open(sys.argv[1]) as f:
            script = f.read();
    except:
        print("Could not read file '%s'" % sys.argv[1])
        exit()
else:
    print("Usage: %s [file.tbl]" % sys.argv[0])
    exit()

lexer = Lexer()
tokens = lexer.lex(script)

parser = Parser()
table = parser.parse(tokens)

if len(table.rows) == 0:
    exit()

def debugPrintTable(table: Table):
    print();
    for row in table.rows:
        for cell in row.cells:
            print(cell.debug_str());
        print();

executor = TableExecutor(table);
executor.maxWidths = None;
executor.widths = None;
executor.maxWidth = 80;
executor.width = None;
executor.padding = None;
executor.border = None;
executor.separator = None;
executor.execute();

if executor.padding is not None:
    table.padding = executor.padding;

sizer = TableSizer(table);
wordWrapper = TableWordWrapper(table);
widths = None

if executor.widths:
    widths = [20] * len(table[0]);
    for i in range(min(len(table[0]), len(executor.widths))):
        width = executor.widths[i];
        if width > 0:
            widths[i] = width;
    wordWrapper.wrap(widths);
else:
    maxWidths = [80] * len(table[0]);
    if executor.maxWidths:
        for i in range(min(len(table[0]), len(executor.maxWidths))):
            width = executor.maxWidths[i];
            if width > 0:
                maxWidths[i] = width;
            else:
                maxWidths[i] = 1_000_000;

    wordWrapper.wrap(maxWidths);

    sizer.setDesiredWidth(executor.width);
    sizer.setMaxWidth(executor.maxWidth);
    widths = maxWidths
    widths = sizer.calculateWidths();
    if widths != maxWidths:
        wordWrapper.wrap(widths);

def deleteEmptyRows():
    for i in reversed(range(len(table))):
        canDelete = True
        for j, cell in enumerate(table[i]):
            if cell.lines or (cell.merge and cell.merge[0] != i or cell.rowspan > 1):
                canDelete = False
                break
        if canDelete:
            if i == 0:
                if table.rows[i].borderBottom:
                    table.topBorder = table.rows[i].borderBottom
            else:
                if table.rows[i].borderBottom:
                    table.rows[i - 1].borderBottom = \
                            table.rows[i].borderBottom
            del table.rows[i]

deleteEmptyRows()
heights = sizer.calculateHeights();

formatter = TableAutoFormatter(table);
formatter.format();

printer = TablePrinter(table);
printer.setDimensions(widths, heights);

if executor.border in (BorderStyle.ASCII,
                       BorderStyle.THICK_ASCII):
    if executor.separator is None:
        executor.separator = BorderStyle.THICK_ASCII
if executor.border == BorderStyle.DOTTED:
    if executor.separator is None:
        executor.separator = BorderStyle.ASCII
borderStyle = executor.border if executor.border \
        is not None else BorderStyle.SINGLE;
separatorStyle = executor.separator if executor.separator \
        is not None else BorderStyle.DOUBLE;

border = Border(borderStyle);
border.setSeparatorStyle(separatorStyle);
printer.setBorder(border);


printer.print()


