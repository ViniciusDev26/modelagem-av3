from ortools.linear_solver import pywraplp

def resolve_problema_ramificacao_poda(coeficientes, restricoes):
    qtd_variaveis = len(coeficientes)

    resolvedor = pywraplp.Solver.CreateSolver('SCIP')
    if not resolvedor:
        raise Exception("Solver não disponível.")

    variaveis = []
    for i in range(qtd_variaveis):
        variaveis.append(resolvedor.IntVar(0, resolvedor.infinity(), f'x{i+1}'))

    objetivo = resolvedor.Objective()
    for i in range(qtd_variaveis):
        objetivo.SetCoefficient(variaveis[i], coeficientes[i])
    objetivo.SetMinimization()

    for restricao in restricoes:
        coeficientes_restricao, limite = restricao
        linha_restricao = resolvedor.RowConstraint(limite, resolvedor.infinity())
        for i in range(len(coeficientes_restricao)):
            linha_restricao.SetCoefficient(variaveis[i], coeficientes_restricao[i])

    global_ub = float('inf')
    solucao_otima = None

    status = resolvedor.Solve()

    if status == pywraplp.Solver.INFEASIBLE:
        print("Nenhuma solução viável encontrada.")
        return

    while status == pywraplp.Solver.OPTIMAL:
        limite_inferior = resolvedor.Objective().Value()
        print("\nSolução encontrada para o nó atual:")
        for var in variaveis:
            print(f"{var.name()} = {var.solution_value()}")
        print(f"Valor da função objetivo (limite inferior): {limite_inferior}")

        if limite_inferior >= global_ub:
            print(f"Poda por qualidade: limite inferior {limite_inferior} >= limite superior global {global_ub}")
            break

        solucao_inteira = True
        for var in variaveis:
            if var.solution_value() != int(var.solution_value()):
                solucao_inteira = False
                break

        if solucao_inteira:
            print(f"Solução inteira encontrada. Atualizando limite superior global: {limite_inferior}")
            global_ub = limite_inferior
            solucao_otima = [var.solution_value() for var in variaveis]
            break

        print("Realizando ramificação...")
        for var in variaveis:
            if var.solution_value() != int(var.solution_value()):
                valor_fracionado = var.solution_value()
                resolvedor.Add(var <= int(valor_fracionado))
                resolvedor.Add(var >= int(valor_fracionado) + 1)
                break

        status = resolvedor.Solve()

    if solucao_otima is not None:
        print("Solução ótima encontrada:")
        for i in range(len(solucao_otima)):
            print(f"x{i+1} = {solucao_otima[i]}")
        print("Valor ótimo =", global_ub)
    else:
        print("Nenhuma solução inteira viável encontrada.")


def principal():
    qtd_restricoes = 2

    print("Informe os coeficientes da função objetivo (separados por espaço):")
    coeficientes = [float(6), float(7), float(4)]

    restricoes = []
    for i in range(qtd_restricoes):
        print(f"Informe os coeficientes da restrição {i+1} (separados por espaço):")
        coef_restricao = [[float(4), float(6), float(9)], [float(8), float(6), float(3)]]
        limite = [45, 46]
        restricoes.append([coef_restricao[i], limite[i]])

    resolve_problema_ramificacao_poda(coeficientes, restricoes)


if __name__ == "__main__":
    principal()
