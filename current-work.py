from ortools.linear_solver.pywraplp import Solver 

def create_solver(coefficients, constraints):
    quantity_variables = len(coefficients)
    solver = Solver.CreateSolver('GLOP')
    if not solver:
        raise Exception("Solver não disponível.")

    variables = []
    for i in range(quantity_variables):
        variables.append(solver.NumVar(0, solver.infinity(), f'x{i+1}'))

    objective = solver.Objective()
    for i in range(quantity_variables):
        objective.SetCoefficient(variables[i], coefficients[i])
    objective.SetMinimization()

    for constraint in constraints:
        constraint_coefficients, limit = constraint
        expression = sum(constraint_coefficients[i] * variables[i] for i in range(len(constraint_coefficients)))
        solver.Add(expression >= limit)

    solver.variables = variables
    return solver

def resolve_board(solver, ID):
    status = solver.Solve()
    if status == Solver.OPTIMAL:
        lower_bound = solver.Objective().Value()
        print(f"Solução encontrada para o nó atual {ID}:")
        result = []
        for var in solver.variables:
            print(f"{var.name()} = {var.solution_value()}")
            result.append(var.solution_value())
        print(f"Valor da função objetivo (limite inferior): {lower_bound}")

        return [result, lower_bound]
    elif status == Solver.INFEASIBLE:
        print("Nenhuma solução viável encontrada.")
        return []


def principal():
    coefficients = [float(6), float(7), float(4)]
    constraints = [[[float(4), float(6), float(9)], 45], [[float(8), float(6), float(3)], 46]]

    solver = create_solver(coefficients, constraints)
    initial_result = resolve_board(solver, 1)
    root_node = Node(initial_result)
    print(root_node.value)
    solve_problem(solver, root_node)

def solve_problem(solver, node, node_counter = 1):
    global_ub = float('inf')
    node_counter += 1

    if not node.value:
        return

    result, lower_bound = node.value
    if lower_bound >= global_ub:
        print(f"Poda por qualidade: limite inferior {lower_bound} >= limite superior global {global_ub}")

    if all(value.is_integer() for value in result):
        print(f"Solução inteira encontrada. Atualizando limite superior global: {lower_bound}")
        global_ub = lower_bound
        print(f"Solução ótima encontrada:")
        for i in range(len(result)):
            print(f"x{i+1} = {result[i]}")
        print("Valor ótimo =", global_ub)
        return

    print("Realizando ramificação...")
    for i, value in enumerate(result):
        if not value.is_integer():
            solver.Add(solver.variables[i] >= int(value) + 1)

    node = Node(resolve_board(solver, node_counter))
    node_counter += 1
    node.add_child(node)

    for child in node.children:
        solve_problem(solver, child, node_counter)
    

def print_in_generic_order(no, level=0):
    if not no.children:
        print(no.value, end=" ")
    else:
        for i, filho in enumerate(no.filhos):
            if i == len(no.children) // 2:
                print(no.value, end=" ")
            print_in_generic_order(filho)

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, filho):
        self.children.append(filho)

if __name__ == "__main__":
    principal()
