from datetime import datetime
from finance_manager import FinanceManager
from grafico import grafico_despesas_por_categoria, grafico_saldo_temporal

def exibir_menu():
    print("\n=== Controle de Finanças pessoais ===")
    print("1. Adicionar Receita")
    print("2. Adicionar Despesa")
    print("3. Ver Transações")
    print("4. Ver Resumo Financeiro")
    print("5. Filtrar por Categoria")
    print("6. Filtrar por Data")
    print("7. Gráfico de Despesas por Categoria")
    print("8. Gráfico de Saldo ao Longo do Tempo")
    print("9. Exportar pra Excel (.xlsx)")
    print("0. Sair")


def main():
    manager = FinanceManager()

    while True:
        exibir_menu()
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            valor = float(input("Valor da receita: R$ "))
            categoria = input("Categoria (ex: salário, extra): ")
            descricao = input("Descrição (opcional): ")
            manager.adicionar_transacao("receita", valor, categoria, descricao)

        elif escolha == "2":
            valor = float(input("Valor da despesa: R$ "))
            categoria = input("Categoria (ex: alimentação, transporte, lazer): ")
            descricao = input("Descrição (opcional): ")
            manager.adicionar_transacao("despesa", valor, categoria, descricao)

        elif escolha == "3":
            transacoes = manager.carregar_transacoes()
            if not transacoes:
                print("Nenhuma transação encontrada.")
            else:
                print("\n=== Lista de Transações ===")
                for t in transacoes:
                    print(f"{t['data']} | {t['tipo'].capitalize():7} | R$ {t['valor']:.2f} | {t['categoria']} | {t['descricao']}")

        elif escolha == "4":
            transacoes = manager.carregar_transacoes()
            total_receitas = sum(t["valor"] for t in transacoes if t["tipo"] == "receita")
            total_despesas = sum(t["valor"] for t in transacoes if t["tipo"] == "despesa")
            saldo = total_receitas - total_despesas

            print("\n=== Resumo ===")
            print(f"Total de Receitas: R$ {total_receitas:.2f}")
            print(f"Total de Despesas: R$ {total_despesas:.2f}")
            print(f"Saldo Final: R$ {saldo:.2f}")

        elif escolha == "5":
            categoria = input("Digite a categoria para filtrar: ").lower()
            transacoes = manager.carregar_transacoes()
            filtradas = [t for t in transacoes if t["categoria"].lower() == categoria]

            if not filtradas:
                print("Nenhuma transação encontrada para essa categoria.")
            else:
                print(f"\nTransações na categoria '{categoria}':")
                for t in filtradas:
                    print(f"{t['data']} | {t['tipo'].capitalize()} | R$ {t['valor']:.2f} | {t['descricao']}")

        elif escolha == "6":
            data_inicio = input("Data inicial (DD/MM/AAAA): ")
            data_fim = input("Data final (DD/MM/AAAA): ")

            try:
                data_i = datetime.strptime(data_inicio, "%d/%m/%Y")
                data_f = datetime.strptime(data_fim, "%d/%m/%Y")
            except ValueError:
                print("Formato da data inválido, use o formato DD/MM/AAAA.")
                continue

            transacoes = manager.carregar_transacoes()
            filtradas = [
                t for t in transacoes
                if data_i <= datetime.strptime(t["data"], "%d/%m/%Y") <= data_f
            ]
            if not filtradas:
                print("Nenhuma transação encontrada nesse intervalo.")
            else:
                print(f"\nTransações entre {data_inicio} e {data_fim}:")
                for t in filtradas:
                    print(f"{t['data']} | {t['tipo'].capitalize()} | R$ {t['valor']:.2f} | {t['categoria']} | {t['descricao']}")

        elif escolha == "7":
            transacoes = manager.carregar_transacoes()
            grafico_despesas_por_categoria(transacoes)

        elif escolha == "8":
            transacoes = manager.carregar_transacoes()
            grafico_saldo_temporal(transacoes)

        elif escolha == "9":
            nome_arquivo = input("Nome do arquivo Excel (pressiona Enter para usar o padrão): ").strip()
            if not nome_arquivo:
                nome_arquivo = "transacoes_exportadas.xlsx"
            elif not nome_arquivo.endswith(".xlsx"):
                nome_arquivo+= ".xlsx"
            
            usar_filtro = input("Deseja exportar um intervalo de datas? (s/n): ").strip().lower()
            if usar_filtro == "s":
                data_inicio = input("Data Inicial (DD/MM/AAAA): ").strip()
                data_fim = input("Data final (DD/MM/AAAA): ").strip()
                manager.exportar_para_excel(nome_arquivo, data_inicio, data_fim)
            else:
                manager.exportar_para_excel(nome_arquivo)

        elif escolha == "0":
            print("Encerrando programa. Até logo!")    
            break

        else:
            print("Escolha inválida. Tente novamente.") 

if __name__ == "__main__":
    main()