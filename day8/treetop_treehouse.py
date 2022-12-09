#!/usr/bin/env python3
import sys
import typing


class Grid:
    def __init__(self):
        self.rows: typing.List[typing.List[int]] = []

    def add_row(self, row: typing.List[int]):
        self.rows.append(row)

    def get_cell(self, row_num, col) -> int:
        if row_num >= len(self.rows) or col >= len(self.rows[0]):
            raise IndexError("Invalid cell")
        return self.rows[row_num][col]

    @property
    def row_count(self):
        return len(self.rows)

    @property
    def column_count(self):
        return len(self.rows[0])

    def edge_cell(self, row_index, col_index):
        return row_index == 0 or row_index == self.row_count - 1 or col_index == 0 or col_index == self.column_count - 1

    def visible_from_left(self, row_index, col_index):
        start = col_index - 1
        row = self.rows[row_index]
        while start >= 0:
            if row[start] >= row[col_index]:
                return False
            start -= 1
        return True

    def visible_from_right(self, row_index, col_index):
        start = col_index + 1
        row = self.rows[row_index]
        while start < len(row):
            if row[start] >= row[col_index]:
                return False
            start += 1
        return True

    def visible_from_top(self, row_index, col_index):
        start = row_index - 1
        val = self.rows[row_index][col_index]
        while start >= 0:
            if self.rows[start][col_index] >= val:
                return False
            start -= 1
        return True

    def visible_from_below(self, row_index, col_index):
        start = row_index + 1
        val = self.rows[row_index][col_index]
        while start < self.row_count:
            if self.rows[start][col_index] >= val:
                return False
            start += 1
        return True

    def is_cell_visible(self, row_index, col_index):
        return self.edge_cell(row_index, col_index) or self.visible_from_right(row_index, col_index) or \
               self.visible_from_left(row_index, col_index) or self.visible_from_below(row_index, col_index) or \
               self.visible_from_top(row_index, col_index)

    def count_visible_cells(self):
        # assuming a perfect square
        visible = self.row_count * 2 + (self.row_count - 2) * 2  # total number of cells on outer grid
        row = 1
        while row < self.row_count - 1:
            col = 1  # skip first col
            while col < self.column_count - 1:  # skip last column
                if self.is_cell_visible(row, col):
                    visible += 1
                col += 1
            row += 1
        return visible

    def cell_scenic_score(self, row_index, col_index):
        total_scenic_score = 1
        val = self.rows[row_index][col_index]

        # looking below
        start = row_index + 1
        sc = 0
        while start < self.row_count:
            sc += 1
            if self.rows[start][col_index] >= val:
                break
            start += 1
        total_scenic_score *= sc

        # looking above
        start = row_index - 1
        sc = 0
        while start >= 0:
            sc += 1
            if self.rows[start][col_index] >= val:
                break
            start -= 1
        total_scenic_score *= sc

        # looking from right
        start = col_index + 1
        row = self.rows[row_index]
        sc = 0
        while start < len(row):
            sc += 1
            if row[start] >= row[col_index]:
                break
            start += 1
        total_scenic_score *= sc

        # looking from left
        start = col_index - 1
        row = self.rows[row_index]
        sc = 0
        while start >= 0:
            sc += 1
            if row[start] >= row[col_index]:
                break
            start -= 1
        total_scenic_score *= sc

        return total_scenic_score

    def best_scenic_score(self):
        best_scenic_score = 0
        row = 1
        while row < self.row_count - 1:
            col = 1  # skip first col
            while col < self.column_count - 1:  # skip last column
                sc = self.cell_scenic_score(row, col)
                if sc > best_scenic_score:
                    best_scenic_score = sc
                col += 1
            row += 1
        return best_scenic_score


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ./treetop.py input.txt")
        exit(1)

    input_text = sys.argv[1]
    grid = Grid()

    for line in open(input_text, "r"):
        row = [int(num) for num in line.strip("\n")]
        grid.add_row(row)

    print(grid.count_visible_cells())
    print(grid.best_scenic_score())
