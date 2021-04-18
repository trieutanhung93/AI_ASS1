import random
import time
import sys
from tkinter.font import BOLD, ITALIC
from typing import List, Tuple
from tkinter import *

class Sudoku:

    def __init__(self, population: int, generation: int) -> None:
        """ Sudoku constructor """

        self.board = [[0 for _ in range(9)] for _ in range(9)]      # init sudoku board
        self.population = population                                # fixed population            
        self.generation = generation                                # maximum generation
        self._createGUI()


    def _createGUI(self) -> None:
        """ Create GUI for sudoku solver """

        window = Tk()
        window.title("Sudoku Solver") 
        window.geometry('800x800')

        for i in range(5):
            window.grid_rowconfigure(i, minsize=25)
            window.grid_columnconfigure(i, minsize=40)

        self._createElement(window)

        window.mainloop()


    def _createElement(self, root: Tk):
        """ Create GUI elements """

        self.canvas = Canvas(root, width=630, height=630, bg="light goldenrod")
        self.canvas.grid(row=2, column=2)

        self.button = Canvas(root, width=640, height=65, bg="mint cream")
        self.button.grid(row=4, column=2)

        for i in range(3):
            self.button.grid_columnconfigure(i, minsize=220)

        self.clear_solution_but = Button(self.button, text="Clear solution", height=1, width=15, command=self.__ClearSolution)
        self.clear_solution_but.grid(row=0, column=0)
        self.clear_solution_but.configure(font=("Roman", 20, BOLD, ITALIC), bd=5, bg="pink", activeforeground="blue", relief=RIDGE)

        self.clear_all_but = Button(self.button, text="Clear all", height=1, width=15, command=self.__ClearAll)
        self.clear_all_but.grid(row=0, column=1)
        self.clear_all_but.configure(font=("Roman", 20, BOLD, ITALIC), bd=5, bg="pink", activeforeground="blue", relief=RIDGE)

        self.solve_but = Button(self.button, text="Solve", height=1, width=15, command=self.__Solve)
        self.solve_but.grid(row=0, column=2)
        self.solve_but.configure(font=("Roman", 20, BOLD, ITALIC), bd=5, bg="pink", activeforeground="blue", relief=RIDGE)

        self.res_lbl = Label(root, font=("Times New Roman", 18), fg="blue")
        self.res_lbl.grid(row=0, column=2)

        self.time_lbl = Label(root, font=("Times New Roman", 18), fg="green")
        self.time_lbl.grid(row=1, column=2)

        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            self.canvas.create_line(10, i*68+10, 620, i*68+10, fill="black", width=width)
            self.canvas.create_line(i*68+10, 10, i*68+10, 620, fill="black", width=width)

        self.entries = []

        for i in range(9):
            for j in range(9):
                entry = Text(root, font=("Times New Roman", 40), width=1, height=1, padx=18, pady=1, bd=0, fg="blue")
                self.entries.append(entry)
                self.canvas.create_window(44+j*68, 44+i*68, window=entry)


    def __ClearSolution(self) -> None:
        """ Clear Solution button command """

        self.solve_but.configure(bg="pink", command=self.__Solve)

        for i in self.index:
            self.entries[i].delete("1.0", END)

        self.res_lbl['text'] = ""
        self.time_lbl['text'] = ""

    def __ClearAll(self) -> None:
        """ Clear All button command """

        self.solve_but.configure(bg="pink", command=self.__Solve)
        self.clear_solution_but.configure(bg="pink", command=self.__ClearSolution)

        for i in range(81):
            self.entries[i].delete("1.0", END)
            self.entries[i].configure(fg="blue")

        self.res_lbl['text'] = ""
        self.time_lbl['text'] = ""

    def __Solve(self) -> None:
        """ Solve button command """

        self.time_lbl['text'] = ""
        self.solve_but.configure(bg="light grey", command="")
        self.clear_solution_but.configure(bg="light grey", command="")

        counter = time.time()
        self.index = []                                                             # list of not fixed element index
        for i in range(81):
            if self.entries[i].get("end-2c", "end-1c") != "":
                self.board[int(i/9)][i%9] = int(float(self.entries[i].get("end-2c", "end-1c")))
            else:
                self.index.append(i)
        
        self.fixed = [set(filter(lambda ele: ele != 0, row)) for row in self.board]   # set of fixed element in each row
        self.remain = [set(range(1, 10)).difference(row) for row in self.fixed]       # set of remain element in each

        solution, generation = GeneticAlgorithm.CreateGeneration(self.board, self.remain, self.population, self.generation)

        for i in range(81):
            if i in self.index:
                self.entries[i].configure(fg="red")
                self.entries[i].insert("1.0", solution[int(i/9)][i%9])

        if generation < 2000:
            self.res_lbl['fg'] = "blue"
            self.res_lbl['text'] = "Solution Found at " + str(generation) + " generation"
        else:
            self.res_lbl.configure(fg="red", text="Best Solution Found")

        counter = time.time() - counter
        self.time_lbl['text'] = "Time: " + str(counter) + " s"

        self.clear_solution_but.configure(bg="pink", command=self.__ClearSolution)


class GeneticAlgorithm:

    @staticmethod
    def CreateGeneration(board: List[List[int]], remain: List[List[int]], size: int, n: int) -> Tuple[List[List[int]], int]:
        """ Genetic algorithm main flow """

        # randomly generate population
        population = GeneticAlgorithm.generatePopulation(size, board, remain)

        # next generation parameter
        count = 0
        best_score = GeneticAlgorithm.fitness(population[0])        # best score of all generation
        best_solution = population[0]                               # best solution found
        best_current_score = best_score                             # best score of vicinal generation
        score = best_score                                          # best score of current generation
        mutationRate = 0.06
        crossoverRate = 0.75
        mutation = [0, 0]                                           # all mutations & successful mutation
        sigma = 1                                                   # parameter for calculate new mutation rate

        # maximum n generation
        for i in range(n):
            # solution found
            if best_current_score == 162:
                return best_solution, i
            else:
                # keep 10 best chromosomes of current generation
                nextGeneration = population[0:10]

                # other base on crossover rate
                for _ in range(int(size /2) - 5):
                    nextGen = GeneticAlgorithm.crossover(population, size, mutationRate, mutation, crossoverRate, board, remain)
                    nextGeneration += nextGen

                population = sorted(nextGeneration, key=GeneticAlgorithm.fitness, reverse=True)
                score = GeneticAlgorithm.fitness(population[0])
                print(GeneticAlgorithm.fitness(population[0]), GeneticAlgorithm.fitness(population[-1]))    # print best and worst score of current generation

                # Calculate new adaptive mutation rate (based on Rechenberg's 1/5 success rule). This is to stop too much mutation as the fitness progresses towards unity.
                if mutation[0] == 0 or mutation[1] / mutation[0] < 0.2:
                    sigma = sigma * 0.998
                elif mutation[1] / mutation[0] > 0.2:
                    sigma = sigma / 0.998
                mutationRate = abs(random.normalvariate(0.0, sigma))

                # reset if in local optimal for 150 generations
                if count == 150:
                    population = GeneticAlgorithm.generatePopulation(size, board, remain)
                    best_current_score = GeneticAlgorithm.fitness(population[0])
                    score = best_current_score
                    mutation = [0, 0]
                    mutationRate = 0.06
                    crossoverRate = 0.75
                    count = 0
                    sigma = 1

                # tracking local optimal
                elif score == best_current_score:
                    count = count + 1
                else:
                    # save best solution
                    if score > best_score:
                        best_score = score
                        best_solution = population[0]
                    best_current_score = score
                    count = 0

        return best_solution, n


    @staticmethod
    def generateChromosome(board: List[List[int]], remain: List[List[int]]) -> List[List[int]]:
        """ generate random chromosome """

        genome = []
        for i in range(9):
            # Chromosome satisfies at least row constraint
            remainEle = list(remain[i]) 
            random.shuffle(remainEle)   
            genome.append([ele if ele != 0 else remainEle.pop(-1) for ele in board[i]])

        return genome


    @staticmethod
    def generatePopulation(n: int, board: List[List[int]], remain: List[List[int]]) -> List[List[List[int]]]:
        """ generate n chromosome """

        population = []
        [population.append(GeneticAlgorithm.generateChromosome(board, remain)) for _ in range(n)]
        return sorted(population, key=GeneticAlgorithm.fitness, reverse=True)
        

    @staticmethod
    def mutation(genome: List[List[int]], probability: float, mutation: List[int], board: List[List[int]], remain: List[List[int]]) -> List[List[int]]:
        if random.uniform(0, 1) < probability:
            """ random resetting mutation """

            old_fitness = GeneticAlgorithm.fitness(genome)

            # begin mutation
            index = random.randint(1, 8)
            remainEle = list(remain[index])
            random.shuffle(remainEle)
            genome[index] = [ele if ele != 0 else remainEle.pop(-1) for ele in board[index]]

            # update number of mutation and successful mutation
            new_fitness = GeneticAlgorithm.fitness(genome)
            mutation[0] += 1
            mutation[1] += 1 if new_fitness > old_fitness else 0

        return genome


    @staticmethod
    def tournament(population: List[List[int]], n: int) -> int:
        """ select two parents to perform crossover """

        # randomly chose two different genes
        chromosome_1 = random.randint(0, n - 1)  
        chromosome_2 = random.randint(0, n - 1)

        while chromosome_2 == chromosome_1:
            chromosome_2 = random.randint(0, n - 1)
            chromosome_1 = random.randint(0, n - 1)  

        # better gene get better chance
        fitness_1 = GeneticAlgorithm.fitness(population[chromosome_1])
        fitness_2 = GeneticAlgorithm.fitness(population[chromosome_2])

        better = chromosome_1 if fitness_1 > fitness_2 else chromosome_2
        weaker = chromosome_1 if fitness_1 <= fitness_2 else chromosome_2

        return better if random.uniform(0, 1) < 0.8 else weaker


    @staticmethod
    def crossover(population: List[List[List[int]]], n: int, mutateProb: float, mutation: List[int], crossProb, board: List[List[int]], remain: List[List[int]]) -> List[List[List[int]]]:
        """ Uniform crossover """

        # select two parents
        parent_1 = GeneticAlgorithm.tournament(population, n)
        parent_2 = GeneticAlgorithm.tournament(population, n)

        while parent_1 == parent_2:
            parent_1 = GeneticAlgorithm.tournament(population, n)                
            parent_2 = GeneticAlgorithm.tournament(population, n)
        
        parents = [population[parent_1], population[parent_2]]

        # perform crossover with probability
        if random.uniform(0, 1) < crossProb:
            # generate two offsprings
            offspring_1 = []
            offspring_2 = []

            # apply uniform crossover
            for i in range(9):
                rand = random.randint(0, 1)
                offspring_1.append(parents[rand][i])
                offspring_2.append(parents[1 - rand][i])

            # apply mutation
            offspring_1 = GeneticAlgorithm.mutation(offspring_1, mutateProb, mutation, board, remain)
            offspring_2 = GeneticAlgorithm.mutation(offspring_2, mutateProb, mutation, board, remain)

            return [offspring_1, offspring_2]

        else:
            return parents


    @staticmethod
    def fitness(genome: List[List[int]]) -> int:
        """ estimate function """

        # goal: sum = 162
        sum = 0
        
        # each col has maximum 9 points
        for col in map(list, zip(*genome)):
            sum += len(set(col))

        # each 3x3 grid has maximum 9 points
        for i in range(9):
            grid = [genome[int(j / 3) + int(i / 3) * 3][j % 3 + i % 3 * 3] for j in range(9)]
            sum += len(set(grid))

        return sum


def main(argv: List[str]) -> None:
    if len(argv) != 2:
        print("Please run as follow command: python sudoku.py population(int) generation(int)")
    else:
        Sudoku(int(argv[0]), int(argv[1]))

if __name__ == "__main__":
    main(sys.argv[1:])




