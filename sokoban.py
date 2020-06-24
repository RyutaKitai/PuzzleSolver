
'''
The main class is the Wareshouse class.
An instance of this class can read a text file coding a Sokoban puzzle,
and  store information about the positions of the walls, boxes and targets 
list. See the header comment of the Warehouse class for details

'''

import operator
import functools


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                           UTILS
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def find_1D_iterator(line, char):
    pos = 0
    # To see the doc of the string method 'find',  type  help(''.find)
    pos = line.find(char, pos)
    while pos != -1:
        yield pos
        pos = line.find(char, pos+1)


def find_2D_iterator(lines, char):
    for y, line in enumerate(lines):
        for x in find_1D_iterator(line, char):
            yield (x,y)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Warehouse:
    def copy(self, worker = None, boxes = None):
        clone = Warehouse()
        clone.worker = worker or self.worker
        clone.boxes = boxes or self.boxes
        clone.targets = self.targets
        clone.walls = self.walls
        clone.ncols = self.ncols
        clone.nrows = self.nrows
        return clone

    def from_string(self, warehouse_str):
        lines = warehouse_str.split(sep='\n')
        self.from_lines(lines)

    def load_warehouse(self, filePath):
        with open(filePath, 'r') as f:
            # 'lines' is a list of strings (rows of the puzzle) 
            lines = f.readlines() 
        self.from_lines(lines)
            
    def from_lines(self, lines):
        # Put the warehouse in a canonical format
        # where row 0 and column 0 have both at least one brick.
        first_row_brick, first_column_brick = None, None
        for row, line in enumerate(lines):
            brick_column = line.find('#')
            if brick_column>=0: 
                if  first_row_brick is None:
                    first_row_brick = row # found first row with a brick
                if first_column_brick is None:
                    first_column_brick = brick_column
                else:
                    first_column_brick = min(first_column_brick, brick_column)
        if first_row_brick is None:
            raise ValueError('Warehouse with no walls!')
        # compute the canonical representation
        # keep only the lines that contain walls
        canonical_lines = [line[first_column_brick:] 
                           for line in lines[first_row_brick:] if line.find('#')>=0]
        
        self.ncols = 1+max(line.rfind('#') for line in canonical_lines)
        self.nrows = len(canonical_lines)
        self.extract_locations(canonical_lines)                
    
    def save_warehouse(self, filePath):
        with open(filePath, 'w') as f:
            f.write(self.__str__())

    def extract_locations(self, lines):
        workers =  list(find_2D_iterator(lines, "@"))  # workers on a free cell
        workers_on_a_target = list(find_2D_iterator(lines, "!"))
        # Check that we have exactly one agent
        assert len(workers)+len(workers_on_a_target) == 1 
        if len(workers) == 1:
            self.worker = workers[0]
        self.boxes = list(find_2D_iterator(lines, "$")) # crate/box
        self.targets = list(find_2D_iterator(lines, ".")) # empty target
        targets_with_boxes = list(find_2D_iterator(lines, "*")) # box on target
        self.boxes += targets_with_boxes
        self.targets += targets_with_boxes
        if len(workers_on_a_target) == 1:
            self.worker = workers_on_a_target[0]
            self.targets.append(self.worker) 
        self.walls = list(find_2D_iterator(lines, "#")) # set(find_2D_iterator(lines, "#"))
        assert len(self.boxes) == len(self.targets)

    def __str__(self):
        X,Y = zip(*self.walls) # pythonic version of the above
        x_size, y_size = 1+max(X), 1+max(Y)
        
        vis = [[" "] * x_size for y in range(y_size)]
        for (x,y) in self.walls:
            vis[y][x] = "#"
        for (x,y) in self.targets:
            vis[y][x] = "."
        if vis[self.worker[1]][self.worker[0]] == ".": # Note y is worker[1], x is worker[0]
            vis[self.worker[1]][self.worker[0]] = "!"
        else:
            vis[self.worker[1]][self.worker[0]] = "@"
        for (x,y) in self.boxes:
            if vis[y][x] == ".": # if on target
                vis[y][x] = "*"
            else:
                vis[y][x] = "$"
        return "\n".join(["".join(line) for line in vis])

    def __eq__(self, other):
        return self.worker == other.worker and \
               self.boxes == other.boxes

    def __hash__(self):
        return hash(self.worker) ^ functools.reduce(operator.xor, [hash(box) for box in self.boxes])
    
if __name__ == "__main__":
    wh = Warehouse()
    wh.load_warehouse("./warehouses/warehouse_01.txt")
#    field.save_warehouse("./F_01.txt")

    print(wh)   # this calls    wh.__str__()


# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + 
#                              CODE CEMETARY
# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + +


