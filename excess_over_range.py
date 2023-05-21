from typing import List, Tuple

# This function evenly distributes excess height to cells within multiple
# ranges. Cells can be covered by one or more ranges, and cells covered by more
# ranges receive higher priority for height increase. The objective is to
# minimize the number of affected cells while successfully distributing the
# excess height across all ranges. The function returns the updated heights of
# all cells after the distribution process.

def excessOverRanges(
        ranges: List[Tuple[Tuple[int, int], int]],
        numCells: int) -> List[int]:
    cells = [0] * numCells
    while ranges:
        chosenCell = -1;
        maxTimesInRange = -1;

        for cell in range(numCells):
            timesInRange = 0
            for range_cells, excess_height in ranges:
                if cell in range(range_cells[0], range_cells[1]):
                    timesInRange += 1
            if timesInRange > maxTimesInRange:
                chosenCell = cell
                maxTimesInRange = timesInRange;
            elif timesInRange == maxTimesInRange:
                if cells[chosenCell] > cells[cell]:
                    chosenCell = cell

        assert chosenCell != -1
        cells[chosenCell] += 1
        for i in reversed(range(len(ranges))):
            if chosenCell in range(ranges[i][0][0], ranges[i][0][1]):
                ranges[i] = (ranges[i][0], ranges[i][1] - 1);
                if ranges[i][1] == 0:
                    del ranges[i]
    return cells
