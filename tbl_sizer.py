from typing import List
from tbl_cell import Cell
from tbl_table import Table
from excess_over_range import excessOverRanges

class TableSizer:
    _table: Table;
    _desiredWidth: int | None;
    _maxWidth: int | None;

    def __init__(self, table: Table):
        self._table = table;
        self._desiredWidth = None;
        self._maxWidth = None;

    def setDesiredWidth(self, desiredWidth: int | None):
        self._desiredWidth = desiredWidth;

    def setMaxWidth(self, maxWidth: int | None):
        self._maxWidth = maxWidth;

    def calculateWidths(self) -> List[int]:
        maxColumnWidths = [0] * len(self._table[0]);
        for i, row in enumerate(self._table):
            for j, cell in enumerate(row):
                if cell.colspan > 1:
                    continue;
                for line in cell.lines:
                    maxColumnWidths[j] = max(maxColumnWidths[j], len(line));
        for i, row in enumerate(self._table):
            for j, cell in enumerate(row):
                if cell.colspan <= 1:
                    continue;
                longestLine = 0
                for line in cell.lines:
                    longestLine = max(longestLine, len(line));
                available = sum(maxColumnWidths[j:j+cell.colspan]) + cell.colspan - 1 \
                        + (cell.colspan - 1) * self._table.padding * 2;
                if longestLine <= available:
                    continue
                remaining = longestLine - available
                maxColumnWidths[j] += remaining

        if self._maxWidth == None and not self._desiredWidth:
            return maxColumnWidths;

        maxContent = sum(maxColumnWidths);
        numColumns = len(maxColumnWidths);

        if self._desiredWidth is not None:
            totalWidth = self._desiredWidth - numColumns - 1 \
                    - (numColumns * self._table.padding * 2);
            targetWidth = max(totalWidth // numColumns, 1);
        else:
            if self._maxWidth is None:
                return maxColumnWidths;
            totalWidth = self._maxWidth - numColumns - 1 \
                    - (numColumns * self._table.padding * 2);
            if maxContent <= totalWidth:
                return maxColumnWidths;
            targetWidth = max(min(totalWidth, maxContent) // numColumns, 1);
        
        newWidths = [min(targetWidth, width) for width in maxColumnWidths];
        remainingWidth = totalWidth - sum(newWidths);
        
        # Allocate remaining width to larger columns
        largerColumns = [i for i, width in enumerate(maxColumnWidths) if width > targetWidth];
        for column in largerColumns:
            ratio = maxColumnWidths[column] / maxContent;
            extraWidth = int(ratio * remainingWidth);
            newWidths[column] += extraWidth;
            if newWidths[column] < 1:
                newWidths[column] = 1;
            remainingWidth -= extraWidth;
        
        while remainingWidth > 0:
            largeColumnFound = False;
            for i in range(numColumns):
                if newWidths[i] < maxColumnWidths[i]:
                    largeColumnFound = True;
                    newWidths[i] += 1;
                    remainingWidth -= 1;
                    if remainingWidth == 0:
                        break;
            if not largeColumnFound:
                break;

        while remainingWidth > 0:
            for i in range(numColumns):
                newWidths[i] += 1;
                remainingWidth -= 1;
                if remainingWidth == 0:
                    break;
    
        return newWidths;

    def calculateHeights(self) -> List[int]:
        heights = [0] * len(self._table);
        row = 0;
        col = 0;
        while row < len(self._table):
            col = 0;
            while col < len(self._table[row]):
                cell = self._table[row][col];
                col += cell.colspan;
                if cell.merge or cell.rowspan > 1:
                    continue;
                heights[row] = max(heights[row], len(cell.lines));
            row += 1;

        ranges = [];
        row = 0;
        col = 0;
        while row < len(self._table):
            col = 0;
            while col < len(self._table[row]):
                cell = self._table[row][col];
                col += cell.colspan;
                if cell.merge or cell.rowspan == 1:
                    continue;
                totalHeight = sum(heights[row : row + cell.rowspan]);
                for i in range(row, row + cell.rowspan - 1):
                    if self._table[i].borderBottom:
                        totalHeight += 1;
                excessHeight = len(cell.lines) - totalHeight;
                if excessHeight > 0:
                    range_info = ((row, row + cell.rowspan), excessHeight);
                    ranges.append(range_info);
            row += 1;

        if ranges:
            increases = excessOverRanges(ranges, len(self._table));
            for i, height in enumerate(increases):
                heights[i] += height;

        return heights;

