import matplotlib.pyplot as plt # Biblioteca para criar gráficos
from collections import defaultdict # Usado para facilitar a contagem de categorias
from datetime import datetime

# Função para gerar um gráfico de pizza com as despesas por categoria
def grafico_despesas_por_categoria(transacoes):
    categorias = defaultdict(float)

    for t in transacoes:
        if t["tipo"] == "despesa":
            categorias[t["categoria"]] += t["valor"]

    if not categorias:
        print("Nenhuma despesa para exibir no gráfico.")
        return

    labels = []
    valores = []
    for categoria, valor in categorias.items():
        labels.append(f"{categoria}: R$ {valor:.2f}")
        valores.append(valor)

    cores = plt.get_cmap('Pastel1').colors  # Paleta suave de cores

    plt.figure(figsize=(7, 7))
    plt.pie(valores, labels=labels, autopct=lambda pct: f"{pct:.1f}%", startangle=90, colors=cores)
    plt.title("Despesas por Categoria", fontsize=14)
    plt.tight_layout()
    plt.show()

# Função para gerar um gráfico de linha com a evolução do saldo ao longo do tempo
def grafico_saldo_temporal(transacoes):
    if not transacoes:
        print("Nenhuma transação para exibir no gráfico.")
        return

    # Ordena por data
    transacoes_ordenadas = sorted(transacoes, key=lambda x: datetime.strptime(x["data"], "%d/%m/%Y"))

    datas = []
    entradas = []
    saidas = []
    saldos = []
    saldo_atual = 0

    for t in transacoes_ordenadas:
        data = datetime.strptime(t["data"], "%d/%m/%Y")
        valor = t["valor"]

        datas.append(data)
        if t["tipo"] == "receita":
            entradas.append(valor)
            saidas.append(0)
            saldo_atual += valor
        else:
            entradas.append(0)
            saidas.append(valor)
            saldo_atual -= valor

        saldos.append(saldo_atual)

    # Criação do gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(datas, saldos, marker='o', label='Saldo', color='blue', linewidth=2)
    plt.bar(datas, entradas, label='Entradas', color='green')
    plt.bar(datas, [-s for s in saidas], label='Saídas', color='red')  # negativo para sair abaixo do zero

    plt.axhline(0, color='black', linewidth=0.5)
    plt.title("Evolução de Entradas, Saídas e Saldo")
    plt.xlabel("Data")
    plt.ylabel("Valor (R$)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()