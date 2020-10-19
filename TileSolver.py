'''
To implement Uniform-Cost Search (UCS), Best-First Search (BFS), and A* Algorithm to
solve the following problems (i.e. find the goal):


1) 8 Puzzle Problem:
The 8 puzzle consists of eight numbered, movable tiles set in a 3x3 frame. One cell of the frame is
always empty thus making it possible to move an adjacent numbered tile into the empty cell. Start
with a random state (cannot be fixed). The goal state is listed below.
1 2 3
8   4
7 6 5
The program is to change the initial configuration into the goal configuration. A solution to the
problem is an appropriate sequence of moves.
'''

import random
from tkinter import *
import colors as c
import itertools
import collections
import _thread
import random
import time
import numpy as np


class Node:

    def __init__(self, puzzle, parent=None, action=None):
        self.puzzle = puzzle  # - 'puzzle' is a Puzzle instance
        self.parent = parent  # - 'parent' is the preceding node generated by the solver, if any
        self.action = action  # - 'action' is the action taken to produce puzzle, if any
        if self.parent is not None:
            self.g = parent.g + 1
        else:
            self.g = 0

    @property
    def score(self):
        return self.g + self.h

    @property
    def state(self):
        return str(self)  # Return a hashable representation of self

    @property
    def path(self):
        node, p = self, []
        while node:
            p.append(node)
            node = node.parent
        yield from reversed(p)  # Reconstruct a path from to the root 'parent'

    @property
    def solved(self):
        return self.puzzle.solved  # Wrapper to check if 'puzzle' is solved

    @property
    def actions(self):
        return self.puzzle.actions  # Wrapper for 'actions' accessible at current state

    @property
    def h(self):
        return self.puzzle.manhattan  # Return the manhattan distance of the node

    @property
    def f(self):
        return self.h + self.g

    def __str__(self):
        return str(self.puzzle)


class Solver:
    # An '8-puzzle' solver
    def __init__(self, start):
        # Start is the initial matrix state from which
        # The puzzle will be solved
        self.start = start

    def solve_a_star(self):
        # Perform A* search and return a path to the solution, if it exists
        queue = collections.deque([Node(self.start)])
        seen = set()
        seen.add(queue[0].state)
        while queue:
            # Sorts the queue based on Lowest cost of both Heuristic and Manhattan distance combine
            queue = collections.deque(sorted(list(queue), key=lambda node: node.f))
            node = queue.popleft()
            if node.solved:
                return node.path

            for move, action in node.actions:
                child = Node(move(), node, action)

                if child.state not in seen:
                    queue.appendleft(child)
                    seen.add(child.state)

    def solve_uniform_cost(self):
        # Perform Uniform Cost search and return a path to the solution, if it exists
        queue = collections.deque([Node(self.start)])
        seen = set()
        seen.add(queue[0].state)
        while queue:
            # Sorts the queue based on Lowest cost(in this case, steps taken to reach node)
            queue = collections.deque(sorted(list(queue), key=lambda node: node.g))
            node = queue.popleft()
            if node.solved:
                return node.path

            for move, action in node.actions:
                child = Node(move(), node, action)

                if child.state not in seen:
                    queue.appendleft(child)
                    seen.add(child.state)

    def solve_best_first_search(self):
        # Perform best first search and return a path to the solution, if it exists
        queue = collections.deque([Node(self.start)])
        seen = set()
        seen.add(queue[0].state)
        while queue:
            # Sorts the queue based on the heuristic score of each node (in this case the manhattan distance)
            queue = collections.deque(sorted(list(queue), key=lambda node: node.h))
            node = queue.popleft()
            if node.solved:
                return node.path

            for move, action in node.actions:
                child = Node(move(), node, action)

                if child.state not in seen:
                    queue.appendleft(child)
                    seen.add(child.state)


class Puzzle:
    # A class representing an '8-puzzle'.
    def __init__(self, board):
        self.width = len(board[0])
        # Input Starting Node
        self.board = board
        # Initializing a Global Goal State
        self.goal_state = np.array([
            [1, 2, 3],
            [8, 0, 4],
            [7, 6, 5]])

    @property
    def solved(self):
        # Solution is found if the flattened matrix are equal to 123804765
        return str(self) == '123804765'

    @property
    def actions(self):
        # Returns a list of move/action sequences. Move results in the child node where
        # '0' is sliding in one of the possible directions
        def create_move(at, to):
            return lambda: self._move(at, to)

        moves = []
        for i, j in itertools.product(range(self.width),
                                      range(self.width)):
            direcs = {'R': (i, j - 1),
                      'L': (i, j + 1),
                      'D': (i - 1, j),
                      'U': (i + 1, j)}

            for action, (r, c) in direcs.items():
                if 0 <= r < self.width and 0 <= c < self.width and self.board[r][c] == 0:
                    move = create_move((i, j), (r, c)), action
                    moves.append(move)
        return moves

    @property
    def manhattan(self):
        # Calculates the sum of distances of each
        # tiles current location from goal state location
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] != 0:
                    # Get the coordinates for item at node[i][j] in goal state position
                    goal_state_coordinate = np.where(self.goal_state == self.board[i][j])
                    # Calculate the Manhattan distance of each point on the node (except 0)
                    distance += abs(goal_state_coordinate[0][0] - i) + abs(goal_state_coordinate[1][0] - j)
        return distance

    def copy(self):
        # Return a new puzzle with the same board as 'self'
        board = []
        for row in self.board:
            board.append([x for x in row])
        return Puzzle(board)

    def _move(self, at, to):
        # Return a new puzzle where 'at' and 'to' tiles have been swapped.
        copy = self.copy()
        i, j = at
        r, c = to
        copy.board[i][j], copy.board[r][c] = copy.board[r][c], copy.board[i][j]
        return copy

    def pprint(self):
        # Used for testing. Prints each child node
        for row in self.board:
            print(row)
        print()

    def __str__(self):
        return ''.join(map(str, self))

    def __iter__(self):
        for row in self.board:
            yield from row


class Game(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.grid()
        self.master.title('AI 8 Puzzle Solver')

        self.main_grid = Frame(self, bg=c.GRID_COLOR, bd=3, width=600, height=600)
        self.main_grid.grid(pady=(100, 0))
        self.make_GUI()
        self.matrix = []
        self.mainloop()

    def make_GUI(self):
        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                cell_frame = Frame(self.main_grid, bg=c.EMPTY_CELL_COLOR, width=150, height=150)
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                cell_number = Label(self.main_grid, bg=c.EMPTY_CELL_COLOR)
                cell_number.grid(row=i, column=j)
                cell_data = {"frame": cell_frame, "number": cell_number}
                row.append(cell_data)
            self.cells.append(row)

        score_frame = Frame(self)
        score_frame.place(relx=0.5, y=45, anchor='center')

        Label(score_frame, text='Enter Matrix', font=c.SCORE_LABEL_FONT).grid(row=0)
        self.matrix_input = Entry(score_frame, borderwidth=5)
        self.matrix_input.grid(row=1)


        def button_click():
            # Get the initial Matrix order that the AI will solve
            # In the format of '123456780' or some order there of
            input_str = str(self.matrix_input.get())
            self.matrix_input.delete(0, END)  # clears the input box
            # self.matrix.clear()  # clears the default matrix before inserting puzzle
            # Creates the Matrix Puzzle
            '''self.run(input_str)'''
            try:
                _thread.start_new_thread(self.run(input_str))
            finally:
                print("Finished")

        self.start_ai_btn = Button(score_frame, text='Start Algorithm',
                                   font=c.BUTTON_FONT, command=lambda: button_click())
        self.start_ai_btn.grid(row=0, column=3, padx=50, pady=10, rowspan=2)

    def run(self, input_str):
        for index in range(len(input_str)):
            if index % 3 == 0:
                sub = input_str[index:index + 3]
                lst = []
                for j in sub:
                    lst.append(j)
                self.matrix.append(lst)

        # Convert Matrix of Strings to Integers for conversion
        for n, i in enumerate(self.matrix):
            for k, j in enumerate(i):
                self.matrix[n][k] = int(j)

        puzzle = Puzzle(self.matrix)
        s = Solver(puzzle)
        tic = time.perf_counter()
        p = s.solve_a_star()
        toc = time.perf_counter()

        steps = -1
        for node in p:
            for row in range(3):
                for col in range(3):
                    if node.puzzle.board[row][col] == 0:
                        self.cells[row][col]['number'].configure(
                            text=str('  '),
                            font=c.CELL_NUMBER_FONTS)
                    else:
                        self.cells[row][col]['number'].configure(
                            text=str(node.puzzle.board[row][col]),
                            font=c.CELL_NUMBER_FONTS)
            # node.puzzle.pprint()
            steps += 1
            self.update_idletasks()
            time.sleep(1)
        self.update_idletasks()


Game()
