import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import tkinter as tk
from tkinter import filedialog
import random
import time

# Define global variable to hold test data
testdata = []

# Function to open a file dialog and load test data
def open_file():
    global testdata
    try:
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                testdata = [list(map(int, line.split())) for line in file.readlines()]
    except Exception as e:
        print(f"Error reading file: {e}")
           
# Create a Tkinter window
root = tk.Tk()
root.title("Chinese Postman Problem")

# Create a button to open the file dialog
open_button = tk.Button(root, text="Open File", command=open_file)
open_button.pack()

# Function to find the vertex with the minimum key value
def min_key(key, mst_set):
    min_value = float('inf')
    min_index = -1
    for v in range(len(testdata)):
        if key[v] < min_value and not mst_set[v]:
            min_value = key[v]
            min_index = v
    return min_index


# Function to create and draw the graph based on a solution
def draw_graph(graph, solution=None, show=True):
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, node_size=700)
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges(), width=6)
    
    if solution:
        path_edges = get_path_edges(solution)
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, width=6, edge_color="tab:red")
        
    nx.draw_networkx_labels(graph, pos, font_size=20, font_family="sans-serif")
    edge_labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)

    legend_elements = [Line2D([0], [0], color='red', lw=4, label='Solution Path')]
    plt.legend(handles=legend_elements, loc='upper left')
    plt.axis('off')
    plt.title(f"Total Distance: {calculate_fitness(graph, solution) if solution else 'N/A'}")
    plt.savefig('output.png')
    
    if show:
        plt.show()

def get_path_edges(solution):
    # Logic to extract path edges correctly, considering repeated visits
    path_edges = []
    for i in range(len(solution) - 1):
        path_edges.append((solution[i], solution[i + 1]))
    path_edges.append((solution[-1], solution[0]))  # Closing the circuit
    return path_edges



def initialize_population(graph, population_size):
    population = []
    for _ in range(population_size):
        # Create a random solution (a sequence of node indices)
        solution = list(graph.nodes())
        random.shuffle(solution)
        population.append(solution)
    return population

def calculate_fitness(graph, solution):
    weight_sum = 0
    for i in range(len(solution) - 1):
        u, v = solution[i], solution[i+1]
        if graph.has_edge(u, v):
            weight_sum += graph[u][v]['weight']
        else:
            weight_sum += 200 # Penalize the fitness for invalid edges
    # Include the edge from the last to the first node to complete the circuit
    if graph.has_edge(solution[-1], solution[0]):
        weight_sum += graph[solution[-1]][solution[0]]['weight']
    else:
        weight_sum += 200
    return weight_sum



def select_parents(population, graph):
    # Tournament selection
    tournament_size = 5
    parents = []
    for _ in range(2):  # Select two parents
        tournament = random.sample(population, tournament_size)
        tournament.sort(key=lambda x: calculate_fitness(graph, x))
        parents.append(tournament[0])
    return parents

def crossover(parent1, parent2):
    # Single-point crossover
    crossover_point = random.randint(1, len(parent1) - 2)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutate(solution, mutation_rate):
    # Swap mutation
    for i in range(len(solution)):
        if random.random() < mutation_rate:
            swap_with = random.randint(0, len(solution) - 1)
            solution[i], solution[swap_with] = solution[swap_with], solution[i]
    return solution

# Function to aggregate solutions (Wisdom of Crowds)
def aggregate_solutions(solutions):
    # Implement your aggregation logic here. This could be as simple as choosing the best solution,
    # or more complex like combining different parts of each solution.
    best_solution = min(solutions, key=lambda x: x[1])
    return best_solution[0]

# Genetic Algorithm function adapted for CPP
def genetic_algorithm(graph, population_size, generations, mutation_rate):
    population = initialize_population(graph, population_size)
    performance_log = []

    for g in range(generations):
        start_time = time.time()
        new_population = []
        for _ in range(population_size // 2):
            parents = select_parents(population, graph)
            for parent in parents:
                new_population.append(mutate(parent, mutation_rate))
        
        population.sort(key=lambda x: calculate_fitness(graph, x))
        population = population[:population_size // 2] + new_population[:population_size // 2]

        best_fitness = calculate_fitness(graph, population[0])
        performance_log.append((g, best_fitness, time.time() - start_time))

    best_solution = population[0]
    best_distance = calculate_fitness(graph, best_solution)
    print(f"Best Path: {best_solution}, Distance: {best_distance}")
    draw_graph(graph, best_solution, show=True)
    return best_solution, best_distance, performance_log

def run_ga_woc():
    global testdata
    G = nx.Graph()
    for i, row in enumerate(testdata):
        for j, weight in enumerate(row):
            if weight != 0:
                G.add_edge(i, j, weight=weight)
    
    solutions = []
    for _ in range(5):  # Run 5 independent GAs
        solution, distance, log = genetic_algorithm(G, population_size=50, generations=100, mutation_rate=0.3)
        solutions.append((solution, distance, log))

    # Aggregate solutions using WoC
    best_solution = aggregate_solutions(solutions)
    best_distance = calculate_fitness(G, best_solution)
    print(f"WoC Best Path: {best_solution}, Distance: {best_distance}")
    draw_graph(G, best_solution, show=True)


# Labels and entries for GA parameters
label_population_size = tk.Label(root, text="Population Size:")
label_population_size.pack()

entry_population_size = tk.Entry(root)
entry_population_size.pack()
entry_population_size.insert(0, "50")  # Default value

label_generations = tk.Label(root, text="Generations:")
label_generations.pack()

entry_generations = tk.Entry(root)
entry_generations.pack()
entry_generations.insert(0, "100")  # Default value

label_mutation_rate = tk.Label(root, text="Mutation Rate:")
label_mutation_rate.pack()

entry_mutation_rate = tk.Entry(root)
entry_mutation_rate.pack()
entry_mutation_rate.insert(0, "0.3")  # Default value

# Modify the Tkinter setup to include a button to run the GA
woc_button = tk.Button(root, text="Run GA with WoC", command=run_ga_woc)
woc_button.pack()

root.mainloop()