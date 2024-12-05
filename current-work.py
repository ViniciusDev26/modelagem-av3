from ortools.linear_solver import pywraplp

class Node:
    def __init__(self, valor):
        self.valor = valor
        self.filhos = []

    def adicionar_filho(self, filho):
        self.filhos.append(filho)

def create_solver(coeficientes, restricoes):
    qtd_variaveis = len(coeficientes)

    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        raise Exception("Solver não disponível.")

    variaveis = []
    for i in range(qtd_variaveis):
        variaveis.append(solver.NumVar(0, solver.infinity(), f'x{i+1}'))

    objetivo = solver.Objective()
    for i in range(qtd_variaveis):
        objetivo.SetCoefficient(variaveis[i], coeficientes[i])
    objetivo.SetMinimization()

    for restricao in restricoes:
        coeficientes_restricao, limite = restricao
        expressao = sum(coeficientes_restricao[i] * variaveis[i] for i in range(len(coeficientes_restricao)))
        solver.Add(expressao >= limite)

    solver.variaveis = variaveis
    return solver

def resolve_board(solver, ID):
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        lower_bound = solver.Objective().Value()
        print(f"Solução encontrada para o nó atual {ID}:")
        result = []
        for var in solver.variaveis:
            print(f"{var.name()} = {var.solution_value()}")
            result.append(var.solution_value())
        print(f"Valor da função objetivo (limite inferior): {lower_bound}")

        return [result, lower_bound]
    elif status == pywraplp.Solver.INFEASIBLE:
        print("Nenhuma solução viável encontrada.")
        return []


def principal():
    coeficientes = [float(6), float(7), float(4)]
    restricoes = [[[float(4), float(6), float(9)], 45], [[float(8), float(6), float(3)], 46]]

    solver = create_solver(coeficientes, restricoes)
    initial_result = resolve_board(solver, 1)
    root_node = Node(initial_result)
    print(root_node.valor)
    solve_problem(solver, root_node)

def solve_problem(solver, node, node_counter = 1):
    global_ub = float('inf')
    node_counter += 1

    if not node.valor:
        return

    result, lower_bound = node.valor
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
            solver.Add(solver.variaveis[i] >= int(value) + 1)

    node = Node(resolve_board(solver, node_counter))
    node_counter += 1
    node.adicionar_filho(node)

    for child in node.filhos:
        solve_problem(solver, child, node_counter)
    

def imprimir_em_ordem_generica(no, nivel=0):
    if not no.filhos:
        print(no.valor, end=" ")
    else:
        for i, filho in enumerate(no.filhos):
            if i == len(no.filhos) // 2:
                print(no.valor, end=" ")
            imprimir_em_ordem_generica(filho)

if __name__ == "__main__":
    principal()
