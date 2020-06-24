
'''

    Sokoban Puzzle solver


'''

import search
import sokoban


from search import astar_graph_search


def is_corner_cell(warehouse, x, y):
    '''
    It is the helper function for Taboo_cells
    Define it is corner or not

    @param warehouse: The given map
    @param x, y: the coordinations to define

    @return
        True if it is corner cell
    '''

    d = 1 # The size of one cell

    if (x + d, y) in warehouse.walls and (x, y + d) in warehouse.walls:
        return 1 # Return true

    if (x - d, y) in warehouse.walls and (x, y + d) in warehouse.walls:
        return 1

    if (x - d, y) in warehouse.walls and (x, y - d) in warehouse.walls:
        return 1

    if (x + d, y) in warehouse.walls and (x, y - d) in warehouse.walls:
        return 1
        
    return 0 # Return false

def find_y_axic_pair(lists):
    pairs = []
    for i,cell in enumerate(lists):
        for check in lists[i:]:
            if check != cell:
                if cell[0] == check[0]:
                    pairs.append(((cell),(check)))
    return pairs

def find_x_axic_pair(lists):
    pairs = []
    for i,cell in enumerate(lists):
        for check in lists[i:]:
            if check != cell:
                if cell[1] == check[1]:
                    pairs.append(((cell),(check)))
    return pairs

def taboo_cells(warehouse):
    '''
    Identify the taboo cells of a warehouse. 
    '''

    cells = []

    w_str = str(warehouse) # Convert to string to remove some items in

    for c in ['$', '@']: # Remove the worker and the boxes
        w_str = w_str.replace(c, ' ')

    w_2d = [list(line) for line in w_str.split('\n')]
    y_size = len(w_2d)
    for y in range(1,y_size):
        outside = 1
        for x in range(0,len(w_2d[0])):
            if outside == 1:
                if w_2d[y][x] == "#":
                    outside = 0 # Define the cells are not on outside
            else:
                if all([empty == ' ' for empty in w_2d[y][x+1:]]):
                    break
                elif is_corner_cell(warehouse, x, y) and w_2d[y][x] != "." and w_2d[y][x] != "#" : # if the cell is on corner
                    cells.append((x, y)) # Add into array
                
    # print(cells)
    beside_wall = find_y_axic_pair(cells)
    on_wall = find_x_axic_pair(cells)
    
    for pair in on_wall:
        wallslen =[]
        on_walli = False
        for i in range(pair[0][0]+1,pair[1][0]):
            wallslen.append((i,pair[0][1]))
        for num in wallslen:
            if w_2d[num[1]-1][num[0]] == "#" or w_2d[num[1]+1][num[0]] == "#":
                on_walli = True
            else:
                on_walli = False
                break
            if w_2d[num[1]][num[0]] == ".":
                on_walli = False
                break
        if on_walli == True:
            cells = cells + wallslen
        else:
            continue
    # print(cells)
    for pair in beside_wall:
        wallslen =[]
        on_walli = True
        for i in range(pair[0][1]+1,pair[1][1]):
            wallslen.append((pair[0][0],i))
        for num in wallslen:
            if w_2d[num[1]][num[0]-1] == "#" or w_2d[num[1]][num[0]+1] == "#":
                on_walli = True
            else:
                on_walli = False
                break
            if w_2d[num[1]][num[0]] == ".":
                on_walli = False
                break
        if on_walli == True:
            cells = cells + wallslen
        else:
            continue
    
    for (x, y) in cells:
        w_2d[y][x] = "X" # Marking with X for taboo cell

    for (x, y) in warehouse.walls:
        w_2d[y][x] = "#" # Making clear every walls are printed

    for (x, y) in warehouse.targets:
        w_2d[y][x] = " " # Remove the targets

    return "\n".join(["".join(line) for line in w_2d]) # Re-join 2D array to print out


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# For can go there function
class SimpleAction(search.Problem):
    def __init__(self, warehouse, goal):
        # tuple state of worker
        self.initial = str(warehouse)
        self.warehouse = warehouse
        self.goal = goal
    def actions(self, state):
        
        currentwarehouse = state
        current2Dmap = list(currentwarehouse.split("\n"))
        ## setting current worker and boxes state
        for j,xs in enumerate(current2Dmap):
            if "@" in xs:
                worker_state = (j,xs.index("@"))
                break
        boxes = []
        for j in range(len(current2Dmap)):
            for i in range(len(current2Dmap[0])):
                if current2Dmap[j][i] == "$":
                    boxes.append((j,i))
                if current2Dmap[j][i] == "*":
                    boxes.append((j,i))
        
                        
        for dire in [(0,1),(0,-1),(1,0),(-1,0)]:
            if (worker_state[0]+dire[0],worker_state[1]+dire[1]) not in boxes and current2Dmap[worker_state[0]+dire[0]][worker_state[1]+dire[1]] != "#":
                yield dire
                
    def result(self, state, action):
        currentwarehouse = state
        current2Dmap = [list(i) for i in currentwarehouse.split("\n")]
        taboocell = True
        ## setting current worker and boxes state
        for j,xs in enumerate(current2Dmap):
            if "@" in xs:
                worker_state = (j,xs.index("@"))
                break 
        for j in range(len(current2Dmap)):
            for i in range(len(current2Dmap[0])):
                if current2Dmap[j][i] == "X":
                    taboocell = False
                    break
                
        if taboocell == False:
            taboo_cells = []
            initial_state = [list(i) for i in self.initial.split("\n")]
            for j in range(len(initial_state)):
                for i in range(len(initial_state[0])):
                    if initial_state[j][i] == "X":
                        taboo_cells.append((j,i))
                        
        current2Dmap[worker_state[0]][worker_state[1]] = " "
        current2Dmap[worker_state[0]+action[0]][worker_state[1]+action[1]] = "@"
        worker_state = (worker_state[0]+action[0], worker_state[1]+action[1])
        
        if taboocell == False:
            for cell in taboo_cells:
                if cell != worker_state:
                    current2Dmap[cell[0]][cell[1]] = "X"
        
        newstate = ""
        for i,xs in enumerate(current2Dmap):
            if i != len(current2Dmap)-1:
                newstate = newstate + "".join(xs) + "\n"
            else:
                newstate = newstate + "".join(xs)
        # print(action)
        # print(newstate)
        state = newstate
        return state
        
    def goal_test(self, state):
        currentwarehouse = state
        current2Dmap = [list(i) for i in currentwarehouse.split("\n")]
            
    
        goalalready = False
        ## setting current worker and boxes state
        for j,xs in enumerate(current2Dmap):
            if "@" in xs:
                worker_state = (j,xs.index("@"))
                break
            if j == len(current2Dmap)-1:
                if "@" not in current2Dmap[j]:
                    goalalready = True
                    
        if goalalready == True:
            return True
        else:
            return worker_state == self.goal
           
    def h(self, node):
        current2Dmap = [list(i) for i in node.state.split("\n")]
        for j,xs in enumerate(current2Dmap):
            if "@" in xs:
                worker_state = (j,xs.index("@"))
                break
        boxes = []
        for j in range(len(current2Dmap)):
            for i in range(len(current2Dmap[0])):
                if current2Dmap[j][i] == "$":
                    boxes.append((j,i),)
                    
        
        heuristicma = []
        for box in boxes:
            heuristicma.append(euclidean_dis(worker_state, box))
        if len(heuristicma) == 0:
            return 0
        else:
            # print(min(heuristicma))
            return min(heuristicma)


class SokobanPuzzle(search.Problem):
    '''
    representing SobanPuzzle problem       
    '''
    
    def __init__(self, macro, allow_taboo_push, warehouse):
        self.macro = macro
        self.allow_taboo_push = allow_taboo_push
        if self.allow_taboo_push == True:
            self.initial = str(warehouse)
            self.goal = str(warehouse).replace(".","*").replace("@"," ").replace("$"," ")
            self.warehouse = warehouse
        elif self.allow_taboo_push == False:
            taboo_warehouse = taboo_cells(warehouse) 
            w_2d = [list(line) for line in taboo_warehouse.split('\n')]
            w_2d[warehouse.worker[1]][warehouse.worker[0]] = "@"
            for target in warehouse.targets:
                w_2d[target[1]][target[0]] = "."
            for box in warehouse.boxes:
                w_2d[box[1]][box[0]] = "$"
                if box in warehouse.targets:
                    w_2d[box[1]][box[0]] = "*"
            str_warehouse = "\n".join(["".join(line) for line in w_2d])
            self.initial = str_warehouse
            self.goal = str_warehouse.replace(".","*").replace("@"," ").replace("$"," ")
            self.warehouse = warehouse
            
    def actions(self, state):
        if self.macro == False:
            
            currentwarehouse = state
            current2Dmap = list(currentwarehouse.split("\n"))
            
            ## setting current worker and boxes state
            for j,xs in enumerate(current2Dmap):
                if "@" in xs:
                    worker_state = (j,xs.index("@"))
                    break
                
            boxes = []
            for j in range(len(current2Dmap)):
                for i in range(len(current2Dmap[0])):
                    if current2Dmap[j][i] == "$":
                        boxes.append((j,i))
                    if current2Dmap[j][i] == "*":
                        boxes.append((j,i))
            
            list_action = []  # list of legal actions
                
            ##if worker_state not in boxes:
                # Left
            if current2Dmap[worker_state[0]][worker_state[1]-1] != "#" and (worker_state[0],worker_state[1]-1) not in boxes:
                list_action.append('Left')
                # Right 
            if current2Dmap[worker_state[0]][worker_state[1]+1] != "#" and (worker_state[0],worker_state[1]+1) not in boxes:
                list_action.append('Right')
                # Up
            if current2Dmap[worker_state[0]-1][worker_state[1]] != "#" and (worker_state[0]-1,worker_state[1]) not in boxes:
                list_action.append('Up')
                # Down
            if current2Dmap[worker_state[0]+1][worker_state[1]] != "#" and (worker_state[0]+1,worker_state[1]) not in boxes:
                list_action.append('Down')
            
            # all possible moving includingg taboo cells
            if self.allow_taboo_push == True:    
                ##if worker_state in boxes:
                    # Left
                if current2Dmap[worker_state[0]][worker_state[1]-1] != "#" and (worker_state[0],worker_state[1]-1) in boxes:
                    if (worker_state[0],worker_state[1]-2) not in boxes and current2Dmap[worker_state[0]][worker_state[1]-2] != "#":
                        list_action.append('Left')
                    # Right 
                if current2Dmap[worker_state[0]][worker_state[1]+1] != "#" and (worker_state[0],worker_state[1]+1) in boxes:
                   if (worker_state[0],worker_state[1]+2) not in boxes and current2Dmap[worker_state[0]][worker_state[1]+2] != "#":
                        list_action.append('Right')
                    # Up
                if current2Dmap[worker_state[0]-1][worker_state[1]] != "#" and (worker_state[0]-1,worker_state[1]) in boxes:
                    # print("noooo")
                    if (worker_state[0]-2,worker_state[1]) not in boxes and current2Dmap[worker_state[0]-2][worker_state[1]] != "#":
                        # print("noooo")
                        list_action.append('Up')
                    # Down
                if current2Dmap[worker_state[0]+1][worker_state[1]] != "#" and (worker_state[0]+1,worker_state[1]) in boxes:
                    if (worker_state[0]+2,worker_state[1]) not in boxes and current2Dmap[worker_state[0]+2][worker_state[1]] != "#":
                        list_action.append('Down')
                
            # moving except for taboo cells
            if self.allow_taboo_push == False:
                ##if worker_state in boxes:
                    # Left
                if current2Dmap[worker_state[0]][worker_state[1]-1] != "#" and (worker_state[0],worker_state[1]-1) in boxes:
                    if (worker_state[0],worker_state[1]-2) not in boxes and current2Dmap[worker_state[0]][worker_state[1]-2] != "X" and current2Dmap[worker_state[0]][worker_state[1]-2] != "#":
                        list_action.append('Left')
                    # Right 
                if current2Dmap[worker_state[0]][worker_state[1]+1] != "#" and (worker_state[0],worker_state[1]+1) in boxes:
                   if (worker_state[0],worker_state[1]+2) not in boxes and current2Dmap[worker_state[0]][worker_state[1]+2] != "X" and current2Dmap[worker_state[0]][worker_state[1]+2] != "#":
                        list_action.append('Right')
                    # U
                if current2Dmap[worker_state[0]-1][worker_state[1]] != "#" and (worker_state[0]-1,worker_state[1]) in boxes:
                    if (worker_state[0]-2,worker_state[1]) not in boxes and current2Dmap[worker_state[0]-2][worker_state[1]] != "X" and current2Dmap[worker_state[0]-2][worker_state[1]] != "#":
                        list_action.append('Up')
                    # Down
                if current2Dmap[worker_state[0]+1][worker_state[1]] != "#" and (worker_state[0]+1,worker_state[1]) in boxes:
                    if (worker_state[0]+2,worker_state[1]) not in boxes and current2Dmap[worker_state[0]+2][worker_state[1]] != "X" and current2Dmap[worker_state[0]+2][worker_state[1]] != "#":
                        list_action.append('Down')
            return list_action
        else:
            # print(state)
            macrocurrentwarehouse = state
            macro_current2Dmap = list(macrocurrentwarehouse.split("\n"))
            ## setting current worker and boxes state
            for j,xs in enumerate(macro_current2Dmap):
                if "@" in xs:
                    worker_state = (j,xs.index("@"))
                    break
                
            boxes = []
            for j in range(len(macro_current2Dmap)):
                for i in range(len(macro_current2Dmap[0])):
                    if macro_current2Dmap[j][i] == "$":
                        boxes.append((j,i))
                    if macro_current2Dmap[j][i] == "*":
                        boxes.append((j,i))
            
            
            if self.allow_taboo_push == True:
                macrolist_action = []  # list of legal actions
                for box in boxes:
                    if macro_current2Dmap[box[0]][box[1]+1] != "#" and (box[0],box[1]+1) not in boxes and can_go_there(macrocurrentwarehouse,(box[0],box[1]-1)):
                        macrolist_action.append((box,"Right"))
                    if macro_current2Dmap[box[0]][box[1]-1] != "#" and (box[0],box[1]-1) not in boxes and can_go_there(macrocurrentwarehouse,(box[0],box[1]+1)): 
                        macrolist_action.append((box,"Left"))
                    if macro_current2Dmap[box[0]+1][box[1]] != "#" and (box[0]+1,box[1]) not in boxes and can_go_there(macrocurrentwarehouse,(box[0]-1,box[1])):
                        macrolist_action.append((box,"Down"))
                    if macro_current2Dmap[box[0]-1][box[1]] != "#" and (box[0]-1,box[1]) not in boxes and can_go_there(macrocurrentwarehouse,(box[0]+1,box[1])):
                        macrolist_action.append((box,"Up"))
            if self.allow_taboo_push == False:
                macrolist_action = []  # list of legal actions
                for box in boxes:
                    if macro_current2Dmap[box[0]][box[1]+1] != "#" and macro_current2Dmap[box[0]][box[1]+1] != "X" and (box[0],box[1]+1) not in boxes:
                        if can_go_there(macrocurrentwarehouse,(box[0],box[1]-1)):
                            macrolist_action.append((box,"Right"))
                    if macro_current2Dmap[box[0]][box[1]-1] != "#" and macro_current2Dmap[box[0]][box[1]-1] != "X" and(box[0],box[1]-1) not in boxes and can_go_there(macrocurrentwarehouse,(box[0],box[1]+1)): 
                        if can_go_there(macrocurrentwarehouse,(box[0],box[1]+1)):
                            macrolist_action.append((box,"Left"))
                    if macro_current2Dmap[box[0]+1][box[1]] != "#" and macro_current2Dmap[box[0]+1][box[1]] != "X" and(box[0]+1,box[1]) not in boxes and can_go_there(macrocurrentwarehouse,(box[0]-1,box[1])):
                        if can_go_there(macrocurrentwarehouse,(box[0]-1,box[1])):
                            macrolist_action.append((box,"Down"))
                    if macro_current2Dmap[box[0]-1][box[1]] != "#" and macro_current2Dmap[box[0]-1][box[1]] != "X" and (box[0]-1,box[1]) not in boxes and can_go_there(macrocurrentwarehouse,(box[0]+1,box[1])):
                        if can_go_there(macrocurrentwarehouse,(box[0]+1,box[1])):
                            macrolist_action.append((box,"Up"))
            return macrolist_action
        
        
    def result(self, state, action):
        if self.macro == False:
            currentwarehouse = state
            current2Dmap = [list(i) for i in currentwarehouse.split("\n")]
            for n in current2Dmap:
                if n == "\n":
                    current2Dmap.remove("\n")
            
            ## setting current worker , targets and boxes state
            for j in range(len(current2Dmap)):
                for i in range(len(current2Dmap[0])):
                    if current2Dmap[j][i] == "@":
                        worker_state = (j,i)
            
            
            boxes = []
            for j in range(len(current2Dmap)):
                for i in range(len(current2Dmap[0])):
                    if current2Dmap[j][i] == "$":
                        boxes.append((j,i))
                    if current2Dmap[j][i] == "*":
                        boxes.append((j,i))
                        
            static_map = [list(i) for i in str(self.warehouse).split("\n")]
            targets = []
            for j in range(len(static_map)):
                for i in range(len(static_map[0])):
                    if static_map[j][i] == ".":
                        targets.append((j,i))
                    if static_map[j][i] == "*":
                        targets.append((j,i))
            if self.allow_taboo_push == False:
                initial_map = [list(i) for i in str(self.initial).split("\n")]
                taboo_cells = []
                for j in range(len(static_map)):
                    for i in range(len(static_map[0])):
                        if initial_map[j][i] == "X":
                            taboo_cells.append((j,i))
            
            if action == "Left":
                if (worker_state[0],worker_state[1]-1) not in boxes:
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]][worker_state[1]-1] = "@"
                    worker_state = (worker_state[0], worker_state[1]-1)
                    
                elif (worker_state[0],worker_state[1]-1) in boxes:
                    boxes.remove((worker_state[0],worker_state[1]-1))
                    boxes.append((worker_state[0],worker_state[1]-2))
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]][worker_state[1]-1] = "@"
                    current2Dmap[worker_state[0]][worker_state[1]-2] = "$"
                    worker_state = (worker_state[0], worker_state[1]-1)
                    
            if action == "Right":
                if (worker_state[0],worker_state[1]+1) not in boxes:
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]][worker_state[1]+1] = "@"
                    worker_state = (worker_state[0], worker_state[1]+1)
                    
                elif (worker_state[0],worker_state[1]+1) in boxes:
                    boxes.remove((worker_state[0],worker_state[1]+1))
                    boxes.append((worker_state[0],worker_state[1]+2))
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]][worker_state[1]+1] = "@"
                    current2Dmap[worker_state[0]][worker_state[1]+2] = "$" 
                    worker_state = (worker_state[0], worker_state[1]+1)
                
            if action == "Up":
                if (worker_state[0]-1,worker_state[1]) not in boxes:
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]-1][worker_state[1]] = "@"
                    worker_state = (worker_state[0]-1, worker_state[1])
                    
                elif (worker_state[0]-1,worker_state[1]) in boxes:
                    boxes.remove((worker_state[0]-1,worker_state[1]))
                    boxes.append((worker_state[0]-2,worker_state[1]))
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]-1][worker_state[1]] = "@"
                    current2Dmap[worker_state[0]-2][worker_state[1]] = "$"
                    worker_state = (worker_state[0]-1, worker_state[1])
                    
            if action == "Down":
                if (worker_state[0]+1,worker_state[1]) not in boxes:
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]+1][worker_state[1]] = "@"
                    worker_state = (worker_state[0]+1, worker_state[1])
                    
                elif (worker_state[0]+ 1,worker_state[1]) in boxes:
                    boxes.remove((worker_state[0]+1,worker_state[1]))
                    boxes.append((worker_state[0]+2,worker_state[1]))
                    current2Dmap[worker_state[0]][worker_state[1]] = " "
                    current2Dmap[worker_state[0]+1][worker_state[1]] = "@"
                    current2Dmap[worker_state[0]+2][worker_state[1]] = "$"
                    worker_state = (worker_state[0]+1, worker_state[1])
                    
            for target in targets:
                if target not in boxes and target != worker_state:
                    current2Dmap[target[0]][target[1]] = "."
                    
            for target in targets:
                for box in boxes:
                    if target == box:
                        current2Dmap[target[0]][target[1]] = "*"
                        # print("y")
            if self.allow_taboo_push == False:
                for cell in taboo_cells:
                    if worker_state != cell:
                        current2Dmap[cell[0]][cell[1]] = "X"
                        
            newstate = ""
            for i,xs in enumerate(current2Dmap):
                if i != len(current2Dmap)-1:
                    newstate = newstate + "".join(xs) + "\n"
                else:
                    newstate = newstate + "".join(xs)
            # print(action)
            # print(newstate)
            state = newstate
            return state
                
        else:
            macrocurrentwarehouse = state
            macrocurrent2Dmap = [list(i) for i in macrocurrentwarehouse.split("\n")]
            for n in macrocurrent2Dmap:
                if n == "\n":
                    macrocurrent2Dmap.remove("\n")
            
            ## setting current worker , targets and boxes state
            for j in range(len(macrocurrent2Dmap)):
                for i in range(len(macrocurrent2Dmap[0])):
                    if macrocurrent2Dmap[j][i] == "@":
                        worker_state = (j,i)
            
            
            macroboxes = []
            for j in range(len(macrocurrent2Dmap)):
                for i in range(len(macrocurrent2Dmap[0])):
                    if macrocurrent2Dmap[j][i] == "$":
                        macroboxes.append((j,i))
                    if macrocurrent2Dmap[j][i] == "*":
                        macroboxes.append((j,i))
                        
            static_map = [list(i) for i in str(self.warehouse).split("\n")]
            macrotargets = []
            for j in range(len(static_map)):
                for i in range(len(static_map[0])):
                    if static_map[j][i] == ".":
                        macrotargets.append((j,i))
                    if static_map[j][i] == "*":
                        macrotargets.append((j,i))
                        
            if self.allow_taboo_push == False:
                initial_map = [list(i) for i in str(self.initial).split("\n")]
                taboo_cells = []
                for j in range(len(static_map)):
                    for i in range(len(static_map[0])):
                        if initial_map[j][i] == "X":
                            taboo_cells.append((j,i))
            if action[1] == "Left":
                macrocurrent2Dmap[worker_state[0]][worker_state[1]] = " "
                macrocurrent2Dmap[action[0][0]][action[0][1]] = "@"
                macrocurrent2Dmap[action[0][0]][action[0][1]-1] = "$"
                macroboxes.remove((action[0][0],action[0][1]))
                macroboxes.append((action[0][0],action[0][1]-1))
                worker_state = (action[0][0],action[0][1])
            if action[1] == "Right":
                macrocurrent2Dmap[worker_state[0]][worker_state[1]] = " "
                macrocurrent2Dmap[action[0][0]][action[0][1]] = "@"
                macrocurrent2Dmap[action[0][0]][action[0][1]+1] = "$"
                macroboxes.remove((action[0][0],action[0][1]))
                macroboxes.append((action[0][0],action[0][1]+1))
                worker_state = (action[0][0],action[0][1])
            if action[1] == "Up":
                macrocurrent2Dmap[worker_state[0]][worker_state[1]] = " "
                macrocurrent2Dmap[action[0][0]][action[0][1]] = "@"
                macrocurrent2Dmap[action[0][0]-1][action[0][1]] = "$"
                macroboxes.remove((action[0][0],action[0][1]))
                macroboxes.append((action[0][0]-1,action[0][1]))
                worker_state = (action[0][0],action[0][1])
            if action[1] == "Down":
                macrocurrent2Dmap[worker_state[0]][worker_state[1]] = " "
                macrocurrent2Dmap[action[0][0]][action[0][1]] = "@"
                macrocurrent2Dmap[action[0][0]+1][action[0][1]] = "$"
                macroboxes.remove((action[0][0],action[0][1]))
                macroboxes.append((action[0][0]+1,action[0][1]))
                worker_state = (action[0][0],action[0][1])
            
            
            for macrotarget in macrotargets:
                if macrotarget not in macroboxes and macrotarget != worker_state:
                    macrocurrent2Dmap[macrotarget[0]][macrotarget[1]] = "."
                    
            for macrotarget in macrotargets:
                for box in macroboxes:
                    if macrotarget == box:
                        macrocurrent2Dmap[macrotarget[0]][macrotarget[1]] = "*"
                        # print("y")
            if self.allow_taboo_push == False:
                for cell in taboo_cells:
                    if worker_state != cell:
                        macrocurrent2Dmap[cell[0]][cell[1]] = "X"
            newstate = ""
            for i,xs in enumerate(macrocurrent2Dmap):
                if i != len(macrocurrent2Dmap)-1:
                    newstate = newstate + "".join(xs) + "\n"
                else:
                    newstate = newstate + "".join(xs)
                
            state = newstate
            return state

    def h(self, node):
        '''
        The heuristic estimate to the goal
        '''
        current2Dmap = [list(i) for i in node.state.split("\n")]
        boxes = []
        for j in range(len(current2Dmap)):
            for i in range(len(current2Dmap[0])):
                if current2Dmap[j][i] == "$":
                    boxes.append((j,i),)
                    
        static_map = [list(i) for i in str(self.warehouse).split("\n")]
        targets = []
        for j in range(len(static_map)):
            for i in range(len(static_map[0])):
                if static_map[j][i] == ".":
                    targets.append((j,i))
                if static_map[j][i] == "*":
                    targets.append((j,i))
        heuristicma = []
        for target in targets:
            for box in boxes:
                heuristicma.append(euclidean_dis(target, box))
        if len(heuristicma) == 0:
            return 0
        else:
            # print(min(heuristicma))
            return min(heuristicma)

    

    def goal_test(self, state):
        return state.replace("@", " ") == self.goal
            
    def path_cost(self, c, state1, action, state2):
        return c + 1
    

def movement(coord, dir):
    if dir == "Left":
        return (coord[0] - 1, coord[1])
    elif dir == "Right":
        return (coord[0] + 1, coord[1])
    elif dir == "Up":
        return (coord[0], coord[1] - 1)
    elif dir == "Down":
        return (coord[0], coord[1] + 1)


def path(n):
    node, path = n, []
    while node:
        path.append(node)
        node = node.parent
    return list(reversed(path))


def euclidean_dis(A1, A2):
    '''
    Calculation of euclidean distance between two given coordinates
    this is for Heuristic
    '''
    return ((A1[0] - A2[0])**2 + (A1[1] - A2[1])**2) ** 0.5


def solve_sokoban_elem(warehouse):
    '''    
    This function should solve using A* algorithm and elementary actions
    the puzzle defined in the parameter 'warehouse'.

    '''
    # Set the empty list
    elem_action = []
    problem = SokobanPuzzle(False, False, warehouse)
    elem_node = search.astar_graph_search(problem)

    # Take and add the actions of the nodes from the path
    for n in path(elem_node):
        elem_action.append(n.action)

    if not elem_action:
        return 'Impossible'
    elif problem.goal_test(problem.initial):
        return []
    else:
        return elem_action[1:]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def can_go_there(warehouse, dst):
    '''    
    Determine whether the worker can walk to the cell dst=(row,column) 
    without pushing any box.
    '''

    problem = SimpleAction(warehouse, dst)

    node = search.astar_graph_search(problem)
    
    # Return True if the A* search can determine path nodes
    return node is not None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def solve_sokoban_macro(warehouse):
    '''    
    Solve using using A* algorithm and macro actions the puzzle defined in 
    the parameter 'warehouse'. 

    A sequence of macro actions should be 
    represented by a list M of the form
            [ ((r1,c1), a1), ((r2,c2), a2), ..., ((rn,cn), an) ]
    '''
    # Set the empty lists
    macro_action = []
    problem = SokobanPuzzle(True, False, warehouse)
    
    macro_nodes = astar_graph_search(problem)
    for n in path(macro_nodes):
        macro_action.append(n.action)
        
    if not macro_action:
        return "Impossible"
    elif problem.goal_test(problem.initial):
        return []
    else:
        return macro_action[1:]
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def solve_weighted_sokoban_elem(warehouse, push_costs):
    '''
    developing
    '''
    # Set the empty list
    actions = []
    new_state = []

    problem = SokobanPuzzle(warehouse)

    copy_state = list(problem.state)
    new_state.append(copy_state[0])

    # Put the push costs on the boxes
    for i in range(len(push_costs)):
        new_state.append(((copy_state[i+1]), push_costs[i]))

    # Set the new initial value with push costs
    problem.initial = tuple(new_state)

    p = search.astar_graph_search(problem)

    # Take and add the actions from path
    for n in path(p):
        actions.append(n.action)

    if actions is None:
        return 'Impossible'
    elif problem.goal_test(problem.state): # If the state is already on the goal
        return []
    else:
        return actions[1:]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
