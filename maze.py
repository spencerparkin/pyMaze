# maze.py -- Generate random rectangular mazes.

import random
import argparse

class MazeFlag:
    UP = 0x01
    DOWN = 0x02
    LEFT = 0x04
    RIGHT = 0x08

class MazeNode(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.rep = None
        self.flags = 0

    def find_representative(self):
        if self.rep is None:
            return self
        found_rep = self.rep.find_representative()
        self.rep = found_rep
        return found_rep

    def is_connected_with(self, node):
        return True if self.find_representative() is node.find_representative() else False

    def connect_with(self, node):
        if not self.is_connected_with(node):
            rep_a = self.find_representative()
            rep_b = node.find_representative()
            rep_a.rep = rep_b
        if self.row - 1 == node.row:
            self.flags |= MazeFlag.UP
        elif self.row + 1 == node.row:
            self.flags |= MazeFlag.DOWN
        elif self.col - 1 == node.col:
            self.flags |= MazeFlag.LEFT
        elif self.col + 1 == node.col:
            self.flags |= MazeFlag.RIGHT

    def reset(self):
        self.flags = 0
        self.rep = None

class MazeEdge(object):
    def __init__(self, node_a, node_b):
        self.node_a = node_a
        self.node_b = node_b

    def make_connection(self):
        self.node_a.connect_with(self.node_b)
        self.node_b.connect_with(self.node_a)

class Maze(object):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.matrix = [[MazeNode(i, j) for j in range(cols)] for i in range(rows)]
        self.edge_list = []
        for i in range(rows - 1):
            for j in range(cols):
                self.edge_list.append(MazeEdge(self.matrix[i][j], self.matrix[i + 1][j]))
        for j in range(cols - 1):
            for i in range(rows):
                self.edge_list.append(MazeEdge(self.matrix[i][j], self.matrix[i][j + 1]))

    def generate(self, seed=None):
        if seed is not None:
            random.seed(seed)
        for i in range(self.rows):
            for j in range(self.cols):
                self.matrix[i][j].reset()
        count = self.rows * self.cols
        random.shuffle(self.edge_list)
        for i in range(len(self.edge_list)):
            edge = self.edge_list[i]
            if not edge.node_a.is_connected_with(edge.node_b):
                edge.make_connection()
                count -= 1
                if count == 1:
                    break

    @staticmethod
    def print_flag_matrix(flag_matrix, rows, cols):
        ascii_map = {
            0x00: ' ',
            MazeFlag.RIGHT: u'\u2550',
            MazeFlag.LEFT: u'\u2550',
            MazeFlag.LEFT | MazeFlag.RIGHT: u'\u2550',
            MazeFlag.UP: u'\u2551',
            MazeFlag.DOWN: u'\u2551',
            MazeFlag.UP | MazeFlag.DOWN: u'\u2551',
            MazeFlag.RIGHT | MazeFlag.UP: u'\u255a',
            MazeFlag.UP | MazeFlag.LEFT: u'\u255d',
            MazeFlag.LEFT | MazeFlag.DOWN: u'\u2557',
            MazeFlag.DOWN | MazeFlag.RIGHT: u'\u2554',
            MazeFlag.LEFT | MazeFlag.RIGHT | MazeFlag.DOWN: u'\u2566',
            MazeFlag.LEFT | MazeFlag.RIGHT | MazeFlag.UP: u'\u2569',
            MazeFlag.LEFT | MazeFlag.UP | MazeFlag.DOWN: u'\u2563',
            MazeFlag.RIGHT | MazeFlag.UP | MazeFlag.DOWN: u'\u2560',
            MazeFlag.LEFT | MazeFlag.RIGHT | MazeFlag.UP | MazeFlag.DOWN: u'\u256c'
        }
        buffer = ''
        for i in range(rows):
            for j in range(cols):
                buffer += ascii_map[flag_matrix[i][j]]
            buffer += '\n'
        return buffer

    def print(self, pathways=False):
        if pathways:
            return self.print_flag_matrix(
                [[self.matrix[i][j].flags for j in range(self.cols)] for i in range(self.rows)], self.rows, self.cols)
        else:
            flag_matrix = [[0 for j in range(self.cols * 2 + 1)] for i in range(self.rows * 2 + 1)]
            for i in range(self.rows * 2 + 1):
                for j in range(self.cols * 2 + 1):
                    if i % 2 == 1 and j % 2 == 1:
                        flags = 0
                    else:
                        flags = MazeFlag.LEFT | MazeFlag.RIGHT | MazeFlag.UP | MazeFlag.DOWN
                        if i == 0:
                            flags &= ~MazeFlag.UP
                        elif i == self.rows * 2:
                            flags &= ~MazeFlag.DOWN
                        if j == 0:
                            flags &= ~MazeFlag.LEFT
                        elif j == self.cols * 2:
                            flags &= ~MazeFlag.RIGHT
                        if i % 2 == 1 and j % 2 == 0:
                            flags &= ~(MazeFlag.LEFT | MazeFlag.RIGHT)
                        elif i % 2 == 0 and j % 2 == 1:
                            flags &= ~(MazeFlag.UP | MazeFlag.DOWN)
                    flag_matrix[i][j] = flags
            for i in range(self.rows):
                for j in range(self.cols):
                    node = self.matrix[i][j]
                    if node.flags & MazeFlag.RIGHT:
                        flag_matrix[i * 2 + 1][j * 2 + 2] = 0
                        flag_matrix[i * 2 + 0][j * 2 + 2] &= ~MazeFlag.DOWN
                        flag_matrix[i * 2 + 2][j * 2 + 2] &= ~MazeFlag.UP
                    if node.flags & MazeFlag.LEFT:
                        flag_matrix[i * 2 + 1][j * 2 + 0] = 0
                        flag_matrix[i * 2 + 0][j * 2 + 0] &= ~MazeFlag.DOWN
                        flag_matrix[i * 2 + 2][j * 2 + 0] &= ~MazeFlag.UP
                    if node.flags & MazeFlag.UP:
                        flag_matrix[i * 2 + 0][j * 2 + 1] = 0
                        flag_matrix[i * 2 + 0][j * 2 + 0] &= ~MazeFlag.RIGHT
                        flag_matrix[i * 2 + 0][j * 2 + 2] &= ~MazeFlag.LEFT
                    if node.flags & MazeFlag.DOWN:
                        flag_matrix[i * 2 + 2][j * 2 + 1] = 0
                        flag_matrix[i * 2 + 2][j * 2 + 0] &= ~MazeFlag.RIGHT
                        flag_matrix[i * 2 + 2][j * 2 + 2] &= ~MazeFlag.LEFT
            flag_matrix[0][1] = 0
            flag_matrix[self.rows * 2][self.cols * 2 - 1] = 0
            return self.print_flag_matrix(flag_matrix, self.rows * 2 + 1, self.cols * 2 + 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', help='How many rows in the rectangular maze. Default is 20', type=str)
    parser.add_argument('--cols', help='How many columns in the rectangular maze. Default is 20', type=str)
    parser.add_argument('--seed', help='Provide random number generator seed.', type=str)
    args = parser.parse_args()
    
    # TODO: Add an optional command-line argument that, if given, will show the maze solution.
    
    rows = int(args.rows) if args.rows else 20
    cols = int(args.cols) if args.cols else 20
    seed = int(args.seed) if args.seed else None
    
    maze = Maze(rows, cols)
    maze.generate(seed)
    print(maze.print())