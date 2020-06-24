
"""

    Searching alghorithms and Problem and Node class here

"""

import sys

# check the Python version is at least 3.5
assert sys.version_info >= (3, 5)

import itertools
import functools
import heapq

import collections # for dequeue


def memoize(fn, slot=None, maxsize=128):
    """Memoize fn: make it remember the computed value for any argument list.
    If slot is specified, store result in that slot of first argument.
    If slot is false, use lru_cache for caching the values."""
    if slot:
        def memoized_fn(obj, *args):
            if hasattr(obj, slot):
                return getattr(obj, slot)
            else:
                val = fn(obj, *args)
                setattr(obj, slot, val)
                return val
    else:
        @functools.lru_cache(maxsize=maxsize)
        def memoized_fn(*args):
            return fn(*args)

    return memoized_fn


#______________________________________________________________________________
# Queues: Stack, FIFOQueue, PriorityQueue
# Stack and FIFOQueue are implemented as list and collection.deque
# PriorityQueue is implemented here


class Queue:
    def __init__(self):
        raise NotImplementedError

    def extend(self, items):
        for item in items: self.append(item)


def LIFOQueue():
    """
    A Last-In-First-Out Queue.
    """
    return []


class FIFOQueue(collections.deque):
    """
    A First-In-First-Out Queue.
    """
    def __init__(self):
        collections.deque.__init__(self)
    def pop(self):
        return self.popleft()


# ______________________________________________________________________________
# Queues: Stack, FIFOQueue, PriorityQueue
# Stack and FIFOQueue are implemented as list and collection.deque
# PriorityQueue is implemented here

class PriorityQueue:
    """A Queue in which the minimum (or maximum) element (as determined by f and
    order) is returned first.."""

    def __init__(self, order='min', f=lambda x: x):
        self.heap = []
        if order == 'min':
            self.f = f
        elif order == 'max':  # now item with max f(x)
            self.f = lambda x: -f(x)  # will be popped first
        else:
            raise ValueError("Order must be either 'min' or 'max'.")

    def append(self, item):
        """Insert item at its correct position."""
        heapq.heappush(self.heap, (self.f(item), item))

    def extend(self, items):
        """Insert each item in items at its correct position."""
        for item in items:
            self.append(item)

    def pop(self):
        """Pop and return the item (with min or max f(x) value)
        depending on the order."""
        if self.heap:
            return heapq.heappop(self.heap)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    def __len__(self):
        """Return current capacity of PriorityQueue."""
        return len(self.heap)

    def __contains__(self, key):
        """Return True if the key is in PriorityQueue."""
        return any([item == key for _, item in self.heap])

    def __getitem__(self, key):
        """Returns the first value associated with key in PriorityQueue.
        Raises KeyError if key is not present."""
        for value, item in self.heap:
            if item == key:
                return value
        raise KeyError(str(key) + " is not in the priority queue")

    def __delitem__(self, key):
        """Delete the first occurrence of key."""
        try:
            del self.heap[[item == key for _, item in self.heap].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.heap)


#______________________________________________________________________________

class Problem(object):
    """The abstract class for a formal problem. """

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. """
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. """
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. """
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value.  Hill-climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError
        
#______________________________________________________________________________

class Node:
    """
    A node in a search tree/graph.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """
        Create and return a child node corresponding to 'action'
        """
        next_state = problem.result(self.state, action)
        return Node(next_state, # next_state is a state
                    self, # parent is a node
                    action, # from this state to next state 
                    problem.path_cost(self.path_cost, self.state, action, next_state)
                    )

    def solution(self):
        """Return the sequence of actions to go from the root state to this node state."""
        # The root node is associated to the initial state.
        # The action associated to the root node is None
        return [node.action for node in self.path()[1:]]

    def path(self):
        "Return a list of nodes forming the path from the root to this node."
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):     
        return hash(self.state)

#______________________________________________________________________________

# Uninformed Search algorithms
        
def tree_search(problem, frontier):
    assert isinstance(problem, Problem)
    frontier.append(Node(problem.initial))
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        frontier.extend(node.expand(problem))
    return None


def graph_search(problem, frontier):
    assert isinstance(problem, Problem)
    frontier.append(Node(problem.initial))
    explored = set() # initial empty set of explored states
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        # Python note: next line uses of a generator
        frontier.extend(child for child in node.expand(problem)
                        if child.state not in explored
                        and child not in frontier)
    return None

def depth_first_graph_search(problem):
    "Search the deepest nodes in the search tree first."
    return graph_search(problem, LIFOQueue())


def breadth_first_graph_search(problem):
    "Graph search version of BFS.  [Fig. 3.11]"
    return graph_search(problem, FIFOQueue())


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# Informed Search algorithms
def best_first_graph_search(problem, f):
    """
    Search the nodes with the lowest f scores first.
    """
    node = Node(problem.initial)
    if problem.goal_test(node.state):
        return node
    frontier = PriorityQueue(f=f)
    frontier.append(node)
    explored = set() # set of states
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                # frontier[child] is the f value of the 
                # incumbent node that shares the same state as 
                # the node child.  Read implementation of PriorityQueue
                if f(child) < frontier[child]:
                    del frontier[child] # delete the incumbent node
                    frontier.append(child) # 
    return None


def uniform_cost_search(problem):
    return best_first_graph_search(problem, lambda node: node.path_cost)

def astar_graph_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    h function when I call astar_search"""
    h = memoize(h or problem.h, slot='h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))


#______________________________________________________________________________
#

# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + 
#                              CODE CEMETARY
# + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + + 

