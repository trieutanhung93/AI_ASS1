from queue import Queue
from queue import LifoQueue
import random
import math

class State:
    def __init__(self, state, parent, direction, depth):
        self.state = state
        self.parent = parent
        self.direction = direction
        self.depth = depth
    
    
    def test(self, goal):
        if self.state == goal:
            return True
        return False

    @staticmethod
    #This would remove illegal moves for a given state
    def available_moves(x, n): 
        moves = ['Left', 'Right', 'Up', 'Down']
        if x % n == 0:
            moves.remove('Left')
        if x % n == n-1:
            moves.remove('Right')
        if x - n < 0:
            moves.remove('Up')
        if x + n > n*n - 1:
            moves.remove('Down')
        return moves
    
    #Produces children of a given state
    def expand(self , n): 
        x = self.state.index(0)
        moves = self.available_moves(x,n)
        
        children = []
        for direction in moves:
            temp = self.state.copy()
            if direction == 'Left':
                temp[x], temp[x - 1] = temp[x - 1], temp[x]
            elif direction == 'Right':
                temp[x], temp[x + 1] = temp[x + 1], temp[x]
            elif direction == 'Up':
                temp[x], temp[x - n] = temp[x - n], temp[x]
            elif direction == 'Down':
                temp[x], temp[x + n] = temp[x + n], temp[x]
        
        
            children.append(State(temp, self, direction, self.depth + 1))
        return children

    #This will return the result: Steps to go to the goal state 
    def solution(self):
        solution = []
        solution.append(self.direction)
        path = self
        while path.parent != None:
            path = path.parent
            solution.append(path.direction)
        solution = solution[:-1]
        solution.reverse()
        return solution
 
def DFS(given_state , goal_state, n): 
    root = State(given_state, None, None, 0)
    if root.test(goal_state):
        return root.solution()
    frontier = LifoQueue()
    frontier.put(root)
    explored = [] #Contains the state has passed 
    
    while not(frontier.empty()):
        current_node = frontier.get()
        max_depth = current_node.depth #current depth of node
        explored.append(current_node.state)
        
        if max_depth == 50:
            continue #go to the next branch

        children = current_node.expand(n) #get children of a given state
        for child in children:
            if child.state not in explored:#check if that state has passed 
                if child.test(goal_state):#that status check is must be the goal status 
                    return child.solution()
                frontier.put(child)
    return []

def random_input(n):
    root =[]
    i = 0
    while i < n*n:
        x = random.randint(0, n*n-1)
        if x not in root:
            root.append(x)
            i+=1
    return root

#Enter N-puzzle
N = int(input("Enter N:\n"))
n = int(math.sqrt(N+1))

#initial start state

#IF you want to be random
root = random_input(n)

#IF you want to allow user input 
# print("Enter your" ,n,"*",n, "puzzle")
# root = []
# for i in range(0,n*n):
#     p = int(input())
#     root.append(p)

#initializes the target state

#if you want random goal state.
goal = random_input(n)

#If you want default goal state: ascending from left to right, top to bottom.
# goal =[]
# for i in range(1, n*n):
#     goal.append(i)
# goal.append(0)

print("The initialization state is:", root)
print("The goal state is:", goal)
if root == goal:
    print("The given state is the goal state.")
else:
    DFS_solution = DFS(root, goal, n)
    if DFS_solution == []:
        print("Couldn't find solution in the limited depth.")
    else:
        print(DFS_solution)