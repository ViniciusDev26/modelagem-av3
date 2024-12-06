from ortools.linear_solver.pywraplp import Solver
import time

def create_solver(coefficients, constraints):
    solver = Solver.CreateSolver('GLOP')
    variables = [solver.NumVar(0, solver.infinity(), f'x{i+1}') for i in range(len(coefficients))]

    objective = solver.Objective()
    for i, coefficient in enumerate(coefficients):
        objective.SetCoefficient(variables[i], coefficient)
    objective.SetMinimization()

    for coefficient, limit in constraints:
        expr = sum(coefficient[i] * variables[i] for i in range(len(coefficient)))
        solver.Add(expr >= limit)

    return solver, variables

def solver_output(solver, variables):
    status = solver.Solve()

    if status == Solver.OPTIMAL: # Poda por otimalidade
        return [var.solution_value() for var in variables], solver.Objective().Value()
    elif status == Solver.INFEASIBLE: # Poda por inviabilidade
        return None, None
    return None, None

def all_integers(lst):
    return all(element.is_integer() for element in lst)

def first_non_integer(lst):
    return next(((index, element) for index, element in enumerate(lst) if not element.is_integer()), None)

def branch_and_bound(coefficients, constraints):
    # Inicializa a pilha com estados definidos apenas pelos dados necessários
    stack = [{"constraints": constraints, "bounds": []}]
    best_solution = None
    best_value = float('inf')

    while stack:
        state = stack.pop()
        current_constraints = state["constraints"]
        bounds = state["bounds"]

        time.sleep(1)

        solver, variables = create_solver(coefficients, current_constraints + bounds)
        result, limit = solver_output(solver, variables)

        print("-" * 50)
        print(f"\nSolução encontrada para o nó atual:")
        print(result, limit)

        if not result:
            print(f"Poda por inviabilidade: Nenhuma solução viável encontrada.")
            print("-" * 50)
            continue
        if limit >= best_value: # Poda por qualidade
            print(f"Poda por qualidade: limite inferior {limit} >= limite superior global {best_value}")
            continue

        if all(x.is_integer() for x in result):
            if limit < best_value:
                print(f"Solução inteira encontrada. Atualizando limite superior global: {limit}")
                best_value = limit
                best_solution = result
            continue

        # Encontra o índice do primeiro valor não-inteiro
        index, value = next((i, x) for i, x in enumerate(result) if not x.is_integer())

        # Divide em dois ramos
        left_bound = [([-1 if i == index else 0 for i in range(len(coefficients))], -(value // 1))]
        right_bound = [([1 if i == index else 0 for i in range(len(coefficients))], value // 1 + 1)]

        print("-" * 50)

        # Adiciona à pilha os novos estados
        stack.append({"constraints": current_constraints, "bounds": bounds + left_bound})
        stack.append({"constraints": current_constraints, "bounds": bounds + right_bound})

    return best_solution, best_value

def main():
    num_constraints = int(input("Informe o número de restrições: "))
    print("Informe os coeficientes da função objetivo (separados por espaço):")
    coefficients = list(map(float, input().split()))

    # Entrada: restrições
    constraints = []
    for i in range(num_constraints):
        print(f"Informe os coeficientes da restrição {i+1} (separados por espaço):")
        constraint_coefficients = list(map(float, input().split()))
        limite = float(input(f"Informe o termo independente da restrição {i+1}: "))
        constraints.append((constraint_coefficients, limite))

    result = branch_and_bound(coefficients, constraints)
    print("Melhor resultado:", result)

def main_filled():
    coefficients = [float(6), float(7), float(4)]
    constraints = [[[float(4), float(6), float(9)], 45], [[float(8), float(6), float(3)], 46]]

    result = branch_and_bound(coefficients, constraints)
    print("Melhor resultado:", result)

if __name__ == "__main__":
    main()
