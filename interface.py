# interface gráfica (GUI) com botões, janelas, campos de entrada etc
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from ttkthemes import ThemedTk
from datetime import datetime
import pandas as pd
from finance_manager import FinanceManager

manager = FinanceManager()

# janela principal
root = ThemedTk(theme="aquativo")
root.title("Controle de Finanças Pessoais")
root.geometry("600x450")
root.resizable(True, True)  # Permite redimensionamento da janela
style = ttk.Style()
style.configure("TButton", anchor="center", font=("Arial", 10))

# Título
titulo = ttk.Label(root, text="Controle de Finanças", font=("Segoe UI", 18, "bold"))
titulo.pack(pady=(10, 2), padx=10)

# funções base para adicionar transações
def adicionar_transação():
    janela = tk.Toplevel(root)
    janela.title("Adicionar Transação")
    janela.geometry("400x400")
    janela.resizable(True, True)

    # Label e entrada para Data
    ttk.Label(janela, text="Data (DD/MM/AAAA):").pack(pady=(10, 2), padx=10)
    data_entry = DateEntry(janela, date_pattern="dd/mm/yyyy", selectmode="day")
    data_entry.pack()

    # Label e Combobox para Tipo
    ttk.Label(janela, text="Tipo (receita ou despesa):").pack(pady=(10, 2), padx=10)
    tipo_var = tk.StringVar()
    tipo_combobox = ttk.Combobox(janela, textvariable=tipo_var, values=["Receita", "Despesa"], state="readonly")
    tipo_combobox.pack()
    
    # Exibe o campo de seleção de forma de pagamento apenas para transações de despesa
    forma_pagamento_label = ttk.Label(janela, text="Forma de Pagamento:")
    forma_pagamento_var = tk.StringVar()
    combo_pagamento = ttk.Combobox(janela, textvariable=forma_pagamento_var, values=["Débito/Pix", "Crédito"], state="readonly")
    combo_pagamento.current(0)

    def exibir_forma_pagamento(event):
        if tipo_var.get().lower() == "despesa":
            forma_pagamento_label.pack(pady=(10, 2), padx=10)
            combo_pagamento.pack(pady=5)
        else:
            forma_pagamento_label.pack_forget()
            combo_pagamento.pack_forget()

    tipo_combobox.bind("<<ComboboxSelected>>", exibir_forma_pagamento)

    # Label e entrada para Valor
    ttk.Label(janela, text="Valor:").pack(pady=(10, 2), padx=10)
    valor_entry = ttk.Entry(janela)
    valor_entry.pack()

    # Label e entrada para Categoria
    ttk.Label(janela, text="Categoria:").pack(pady=(10, 2), padx=10)
    categoria_entry = ttk.Entry(janela)
    categoria_entry.pack()

    # Label e entrada para Descrição
    ttk.Label(janela, text="Descrição:").pack(pady=(10, 2), padx=10)
    descricao_entry = ttk.Entry(janela)
    descricao_entry.pack()

    def salvar(): # função para salvar os dados inseridos no arquivo json
        data = data_entry.get().strip()
        if not data:
            data = datetime.now().strftime("%d/%m/%Y")  # Se o campo estiver vazio, usa data atual
        else:
            try:
                datetime.strptime(data, "%d/%m/%Y")  # Valida o formato
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
                return

        tipo = tipo_var.get().lower()
        try:
            valor = float(valor_entry.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Use ponto ou vírgula para casas decimais.")
            return
        
        categoria = categoria_entry.get()
        descricao = descricao_entry.get()
        forma_pagamento = forma_pagamento_var.get() if tipo == "despesa" else ""

        if tipo not in ["receita", "despesa"]:
            messagebox.showerror("Erro", "Tipo deve ser 'receita' ou 'despesa'.")
            return

        manager.adicionar_transacao(data, tipo, valor, categoria, forma_pagamento, descricao)
        messagebox.showinfo("Sucesso", "Transação adicionada com sucesso!")
        janela.destroy()

    ttk.Button(janela, text="💾 Salvar", command=salvar).pack(pady=10, padx=20)

def ver_transacoes(): # exibe na tela as transações salvas no arquivo json
    janela = tk.Toplevel(root)
    janela.title("Ver Transações")
    janela.geometry("700x400")
    janela.resizable(True, True)

    tree = ttk.Treeview(janela, columns=("Tipo", "Valor", "Categoria", "Descrição", "Data", "Forma de Pagamento"), show="headings")
    # Dicionário para controlar a ordem atual (crescente ou decrescente) de cada coluna
    ordem_colunas = {}
    # Função para ordenar transações
    def ordenar_por(col):
        transacoes_atualizadas = [(tree.set(k, col), k) for k in tree.get_children('')]
        try: # tenta converter os valores para números para ordenar corretamente, caso seja "valor"
            transacoes_atualizadas.sort(key=lambda t: float(t[0].replace(",", ".")))
        except: # se não for número, ordena como strings
            transacoes_atualizadas.sort(key=lambda t: t[0])
        if ordem_colunas.get(col, False):
            transacoes_atualizadas.reverse()
        # Reorganiza itens na árvore
        for index, (val, k) in enumerate(transacoes_atualizadas):
            tree.move(k, '', index)
        # Inverte a ordem para a próxima ordenação
        ordem_colunas[col] = not ordem_colunas.get(col, False)

    tree.tag_configure('receita', background='#d4f5d4')
    tree.tag_configure('despesa', background='#f5d4d4')

    for col in tree["columns"]:
        tree.heading(col, text=col, command=lambda col=col: ordenar_por(col))
        tree.column(col, width=100)

    transacoes = manager.carregar_transacoes()

    for i, t in enumerate(transacoes):
        tipo_tag = 'receita' if t["tipo"].lower() == 'receita' else 'despesa'
        tree.insert("", "end", iid=i, values=(t["tipo"], t["valor"], t["categoria"], t["descricao"], t["data"], t.get("forma_pagamento", "")), tags=(tipo_tag))

    tree.pack(pady=10, fill="both", expand=True)

    def editar_transacao(): # seleciona e edita dados da planilha exibida
        item_selecionado = tree.selection()
        if not item_selecionado:
            messagebox.showwarning("Aviso", "Selecione um item para editar.")
            return
        index = int(item_selecionado[0])
        transacao = transacoes[index]
        abrir_janela_edicao(index, transacao, janela, tree)

    btn_editar = ttk.Button(janela, text="✏️ Editar Selecionada", command=editar_transacao)
    btn_editar.pack(pady=10, padx=20)

def abrir_janela_edicao(index, transacao, janela_pai, tree): # abre as janelas para edição dos dados da planilha
    janela_edicao = tk.Toplevel(janela_pai)
    janela_edicao.title("Editar Transação")
    janela_edicao.geometry("400x300")
    janela_edicao.resizable(True, True)

    tk.Label(janela_edicao, text="Tipo (Receita/Despesa):").pack()
    tipo_var = tk.StringVar(value=transacao["tipo"])
    tipo_combobox = ttk.Combobox(janela_edicao, textvariable=tipo_var, values=["Receita", "Despesa"], state="readonly")
    tipo_combobox.pack()

    tk.Label(janela_edicao, text="Valor:").pack()
    valor_var = tk.StringVar(value=str(transacao["valor"]))
    tk.Entry(janela_edicao, textvariable=valor_var).pack()

    tk.Label(janela_edicao, text="Categoria:").pack()
    categoria_var = tk.StringVar(value=transacao["categoria"])
    tk.Entry(janela_edicao, textvariable=categoria_var).pack()

    tk.Label(janela_edicao, text="Descrição").pack()
    descricao_var = tk.StringVar(value=transacao["descricao"])
    tk.Entry(janela_edicao, textvariable=descricao_var).pack()

    def salvar_edicao(): # salva as edições no arquivo json
        try:
            valor_float = float(valor_var.get())
            if tipo_var.get().lower() not in ["receita", "despesa"]:
                raise ValueError("Tipo deve ser 'Receita' ou 'Despesa'.")
            nova_transacao = {
                "tipo": tipo_var.get().capitalize(),
                "valor": round(valor_float, 2),
                "categoria": categoria_var.get(),
                "descricao": descricao_var.get(),
                "data": transacao["data"]
            }
            # atualiza a lista de transações
            transacoes = manager.carregar_transacoes()
            transacoes[index] = nova_transacao
            manager.salvar_transacoes(transacoes)
            # atualiza a treeview na interface
            tree.item(index, values=(
                nova_transacao["tipo"],
                nova_transacao["valor"],
                nova_transacao["categoria"],
                nova_transacao["descricao"],
                nova_transacao["data"]
            ))
            messagebox.showinfo("Sucesso", "Transação atualizada com sucesso.")
            janela_edicao.destroy()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    ttk.Button(janela_edicao, text="Salvar Alterações", command=salvar_edicao).pack(pady=10, padx=20)

def filtrar_por_data(): # filtra e exibe os dados da planilha por período selecionado
    janela_filtro = tk.Toplevel(root)
    janela_filtro.title("Filtrar por Datas")
    janela_filtro.geometry("550x300")
    janela_filtro.resizable(True, True)

    ttk.Label(janela_filtro, text="📌 Após selecionar uma data, selecione a outra para liberar a edição novamente.", 
              foreground="red", font=("Arial", 10, "bold")).pack(pady=(10, 2), padx=10)

    ttk.Label(janela_filtro, text="Data Início (DD/MM/AAAA):").pack(pady=(10, 2), padx=10)
    entrada_inicio = DateEntry(janela_filtro, date_pattern="dd/mm/yyyy", selectmode="day")
    entrada_inicio.pack(pady=5)

    ttk.Label(janela_filtro, text="Data Final (DD/MM/AAAA):").pack(pady=(10, 2), padx=10)
    entrada_fim = DateEntry(janela_filtro, date_pattern="dd/mm/yyyy", selectmode="day")
    entrada_fim.pack(pady=5)
    
    def aplicar_filtro(): # função interna que filtra e mostra o resultado
        data_inicio = entrada_inicio.get()
        data_fim = entrada_fim.get()
        try:
            datetime.strptime(data_inicio, "%d/%m/%Y")
            datetime.strptime(data_fim, "%d/%m/%Y")
            # busca transações dentro do período
            transacoes = manager.filtrar_por_data(data_inicio, data_fim)
            # nova janela mostrando o resultado
            resultado_janela = tk.Toplevel(janela_filtro)
            resultado_janela.title("Transações filtradas")
            resultado_janela.geometry("600x400")
            resultado_janela.resizable(True, True)

            tree = ttk.Treeview(resultado_janela, columns=("Data", "Tipo", "Categoria", "Valor"), show="headings")
            tree.pack(expand=True, fill="both", padx=10, pady=10)

            for col in ("Data", "Tipo", "Categoria", "Valor"):
                tree.heading(col, text=col)
                tree.column(col, width=100)
            if not transacoes:
                messagebox.showinfo("Aviso", "Nenhuma transação encontrada no período.")
            else:
                for t in transacoes:
                    tree.insert("", "end", values=(t["data"], t["tipo"], t["categoria"], f'R$ {t["valor"]:.2f}'))
            # Adiciona ordenação ao clicar no cabeçalho
            ordem_colunas = {col: False for col in tree["columns"]}
            
            def ordenar_por(col):
                ordem_colunas[col] = not ordem_colunas[col]
                lista = [(tree.set(k, col), k) for k in tree.get_children('')]
                try:
                    if col == "Valor":
                        lista.sort(key=lambda t: float(t[0].replace("R$", "").replace(",", "").replace(",", ".")), reverse=ordem_colunas[col])
                    elif col == "Data":
                        lista.sort(key=lambda t: datetime.strptime(t[0], "%d/%m/%Y"), reverse=ordem_colunas[col])
                    else:
                        lista.sort(reverse=ordem_colunas[col])
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao ordenar: {e}")
                    return
                for index, (_, k) in enumerate(lista):
                    tree.move(k, '', index)
            for col in tree["columns"]:
                tree.heading(col, text=col, command=lambda col=col: ordenar_por(col))

        except ValueError:
            messagebox.showerror("Erro", "Data inválida, use o formato DD/MM/AAAA.")
            
    ttk.Button(janela_filtro, text="Filtrar", command=aplicar_filtro).pack(pady=10, padx=20)
  
def exportar_excel(): # exporta os dados do arquivo json para uma planilha .xlsx
    def aplicar_exportacao():
        data_inicio = entrada_inicio.get()
        data_fim = entrada_fim.get()
        try:
            # Validação simples do formato
            datetime.strptime(data_inicio, "%d/%m/%Y")
            datetime.strptime(data_fim, "%d/%m/%Y")
            caminho_arquivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Planilha Excel", "*.xlsx")]
            )
            if not caminho_arquivo:
                return
            manager.exportar_para_excel(
                nome_arquivo=caminho_arquivo,
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            messagebox.showinfo("Sucesso", "Transações exportadas com sucesso.")
        except ValueError:
            messagebox.showerror("Erro", "Datas inválidas. Use o formato: DD/MM/AAAA")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exportar: {e}")

    # Cria janela para entrada de datas
    janela_exportacao = tk.Toplevel(root)
    janela_exportacao.title("Exportar para Excel")
    janela_exportacao.geometry("550x200")

    ttk.Label(janela_exportacao, text="📌 Após selecionar uma data, selecione a outra para liberar a edição novamente.", 
              foreground="red", font=("Arial", 10, "bold")).pack(pady=(10, 2), padx=10)

    ttk.Label(janela_exportacao, text="Data Início (DD/MM/AAAA):").pack(pady=(10, 2), padx=10)
    entrada_inicio = DateEntry(janela_exportacao, date_pattern="dd/mm/yyyy", selectmode="day")
    entrada_inicio.pack(pady=5)

    ttk.Label(janela_exportacao, text="Data Final (DD/MM/AAAA):").pack(pady=(10, 2), padx=10)
    entrada_fim = DateEntry(janela_exportacao, date_pattern="dd/mm/yyyy", selectmode="day")
    entrada_fim.pack(pady=5)

    ttk.Button(janela_exportacao, text="Exportar", command=aplicar_exportacao).pack(pady=(10, 2), padx=10)

def gerar_grafico():  # Interface para gerar gráficos
    def aplicar_grafico(tipo):
        data_inicio = entrada_inicio.get()
        data_fim = entrada_fim.get()
        try:
            datetime.strptime(data_inicio, "%d/%m/%Y")
            datetime.strptime(data_fim, "%d/%m/%Y")
            transacoes_filtradas = manager.filtrar_por_data(data_inicio, data_fim)

            if not transacoes_filtradas:
                messagebox.showinfo("Aviso", "Nenhuma transação para este período.")
                return

            if tipo == "saldo":
                from grafico import grafico_saldo_temporal
                grafico_saldo_temporal(transacoes_filtradas)
            elif tipo == "categoria":
                from grafico import grafico_despesas_por_categoria
                grafico_despesas_por_categoria(transacoes_filtradas)

        except ValueError:
            messagebox.showerror("Erro", "Data inválida, utilize o padrão DD/MM/AAAA.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o gráfico: {e}")

    # Cria janela de entrada de datas
    janela_grafico = tk.Toplevel(root)
    janela_grafico.title("Gerar Gráficos")
    janela_grafico.geometry("550x250")
    janela_grafico.resizable(False, False)

    ttk.Label(janela_grafico, text="📌 Após selecionar uma data, selecione a outra para liberar a edição novamente.",
              foreground="red", font=("Arial", 10, "bold")).pack(pady=(10, 2), padx=10)

    ttk.Label(janela_grafico, text="Data Início (DD/MM/AAAA):").pack(pady=(10, 2))
    entrada_inicio = DateEntry(janela_grafico, date_pattern="dd/mm/yyyy", selectmode="day")
    entrada_inicio.pack(pady=5)

    ttk.Label(janela_grafico, text="Data Final (DD/MM/AAAA):").pack(pady=(10, 2))
    entrada_fim = DateEntry(janela_grafico, date_pattern="dd/mm/yyyy", selectmode="day")
    entrada_fim.pack(pady=5)

    # Botões para escolher o tipo de gráfico
    frame_botoes = ttk.Frame(janela_grafico)
    frame_botoes.pack(pady=15)

    btn_saldo = ttk.Button(frame_botoes, text="📈 Gráfico de Saldo no Tempo", command=lambda: aplicar_grafico("saldo"))
    btn_saldo.grid(row=0, column=0, padx=10)

    btn_categoria = ttk.Button(frame_botoes, text="📊 Gráfico de Despesas por Categoria", command=lambda: aplicar_grafico("categoria"))
    btn_categoria.grid(row=0, column=1, padx=10)

def importar_planilha(): # importa planilha externa para o arquivo json, padronizando colunas
    caminho_arquivo = filedialog.askopenfilename(filetypes=[("Planilhas Excel ou CSV", "*.xlsx *.csv")])
    if not caminho_arquivo:
        return
    try:
        extensao = caminho_arquivo.split(".")[-1].lower()
        if extensao == "xlsx":
            xls = pd.ExcelFile(caminho_arquivo)
            if len(xls.sheet_names) > 1:
                def selecionar_aba():
                    aba_selecionada = aba_var.get()
                    janela_abas.destroy()
                    try:
                        df = pd.read_excel(caminho_arquivo, sheet_name=aba_selecionada)
                        visualizar_previa(df)
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao carregar aba selecionada:\n{e}")

                janela_abas = tk.Toplevel(root)
                janela_abas.title("Selecionar Aba")
                janela_abas.geometry("300x200")

                ttk.Label(janela_abas, text="Selecione a aba para importar:").pack(pady=(10, 2), padx=10)
                aba_var = tk.StringVar()
                combo_abas = ttk.Combobox(janela_abas, textvariable=aba_var, values=xls.sheet_names, state="readonly")
                combo_abas.pack(pady=5)
                ttk.Button(janela_abas, text="Confirmar", command=selecionar_aba).pack(pady=(10, 2), padx=10)
            else:
                df = pd.read_excel(caminho_arquivo)
                visualizar_previa(df)
        elif extensao == "csv":
            df = pd.read_csv(caminho_arquivo)
            visualizar_previa(df)
        else:
            messagebox.showerror("Erro", "Formato de arquivo não suportado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao carregar o arquivo:\n{e}")   

def visualizar_previa(df):
    janela_previa = tk.Toplevel(root)
    janela_previa.title("Visualizar Previa da Planilha")
    janela_previa.geometry("700x500")
    janela_previa.resizable(True, True)

    previa = df.head(20)
    texto = tk.Text(janela_previa, wrap="none")
    texto.pack(expand=True, fill="both")

    texto.insert("end", previa.to_string(index=False))
    texto.config(state="disabled")

    def continuar():
        janela_previa.destroy()
        colunas_encontradas = df.columns.tolist()
        dados_planilha = df.to_dict(orient="records")
        abrir_janela_mapeamento(colunas_encontradas, dados_planilha)

    def cancelar():
        janela_previa.destroy()
        messagebox.showinfo("Cancelado", "Importação Cancelada")

    botoes_frame = ttk.Frame(janela_previa)
    botoes_frame.pack(pady=10)

    ttk.Button(botoes_frame, text="Continuar", command=continuar).pack(side="left", pady=10, padx=20)
    ttk.Button(botoes_frame, text="Cancelar", command=cancelar).pack(side="right", pady=10, padx=20)

def carregar_dados(xls, aba):
    try:
        df = pd.read_excel(xls, sheet_name=aba)
        colunas_encontradas = df.columns.tolist()
        dados_planilha = df.to_dict(oriente="records")
        abrir_janela_mapeamento(colunas_encontradas, dados_planilha)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados da aba '{aba}':\n{e}")
    
def abrir_janela_mapeamento(colunas_encontradas, dados_planilha):
    janela_mapeamento = tk.Toplevel(root)
    janela_mapeamento.title("Mapear Colunas")
    janela_mapeamento.geometry("400x400")
    janela_mapeamento.resizable(True, True)
    
    ttk.Label(janela_mapeamento, text="Mapeie as colunas da planilha para os campos padrão:").pack(pady=(10, 2), padx=10)

    campos_padrao = ["data", "tipo", "categoria", "valor", "descricao"]
    mapeamento = {}

    for campo in campos_padrao:
        frame = ttk.Frame(janela_mapeamento)
        frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(frame, text=f"{campo.capitalize()}:").pack(side="left")

        var = tk.StringVar()
        mapeamento[campo] = var
        combo = ttk.Combobox(frame, textvariable=var, values=colunas_encontradas, state="readonly")
        combo.pack(side="right", fill="x", expand=True)

    def aplicar_mapeamento():
        transacoes_importadas = []

        for linha in dados_planilha:
            transacao = {}
            try:
                for campo, var in mapeamento.items():
                    coluna_origem = var.get()
                    if not coluna_origem:
                        valor = ""  # Campo não mapeado: deixar vazio para completar depois
                    else:
                        valor = linha.get(coluna_origem)
                    if campo == "valor":
                        valor = float(str(valor).replace(",", "."))
                    elif campo == "data":
                        if isinstance(valor, datetime):
                            valor = valor.strftime("%d/%m/%Y")
                        else:
                            valor = datetime.strptime(str(valor), "%d/%m/%Y").strftime("%d/%m/%Y")
                    elif campo == "tipo":
                        valor = str(valor).strip().lower()
                    else:
                        valor = str(valor).strip()
                    transacao[campo] = valor
                transacoes_importadas.append(transacao)
            except Exception as e:
                messagebox.showwarning("Aviso", f"Erro ao importar linha: {linha}\n{e}")
        
        if transacoes_importadas:
            for t in transacoes_importadas:
                completar_transacoes(transacoes_importadas)
            janela_mapeamento.destroy()

    ttk.Button(janela_mapeamento, text="Importar", command=aplicar_mapeamento).pack(pady=10, padx=20)

def completar_transacoes(transacoes_incompletas):
    if not transacoes_incompletas:
        return
    
    transacao_atual = transacoes_incompletas.pop(0)

    janela_edicao = tk.Toplevel(root)
    janela_edicao.title("Completar Transacao")
    janela_edicao.geometry("400x400")
    janela_edicao.resizable(True, True)

    campos = ["data", "tipo", "categoria", "valor", "descricao"]
    entradas = {}

    primeiro_vazio = None # para guardar o primeiro campo vazio
    
    for campo in campos:
        frame = ttk.Frame(janela_edicao)
        frame.pack(pady=5, fill="x", padx=20)
        ttk.Label(frame, text=f"{campo.capitalize()}:").pack(side="left")

        entrada = ttk.Entry(frame)
        entrada.pack(side="right", fill="x", expand=True)

        valor_inicial = transacao_atual.get(campo, "")
        if valor_inicial:
            entrada.insert(0, valor_inicial)
        else:
            if primeiro_vazio is None:
                primeiro_vazio = entrada

        entradas[campo]= entrada
      
    def salvar_completo():
        nova_transacao = {}
        try:
            for campo, entrada in entradas.items():
                valor = entrada.get().strip()
                if not valor and campo != "descricao":
                    raise ValueError(f"Campo '{campo}' não pode ficar vazio.")
                if campo == "valor":
                    valor = float(valor.replace(",", "."))
                nova_transacao[campo] = valor
            # salvar no sistema
            manager.adicionar_transacao(
                nova_transacao["data"],
                nova_transacao["tipo"],
                nova_transacao["valor"],
                nova_transacao["categoria"],
                nova_transacao.get("descricao", "")
            )
            janela_edicao.destroy()
            # Se ainda restarem transações, chama novamente
            completar_transacoes(transacoes_incompletas)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar transação: \n{e}")
    
    ttk.Button(janela_edicao, text="Salvar e Próximo", command=salvar_completo).pack(pady=10, padx=20)
    janela_edicao.after(100, lambda: primeiro_vazio.focus() if primeiro_vazio else list(entradas.values())[0].focus())

def configurar_vencimento_fatura():
    janela_config = tk.Toplevel(root)
    janela_config.title("Configurar Vencimento da Fatura")
    janela_config.geometry("400x150")

    ttk.Label(janela_config, text="Dia de vencimento da fatura (1 a 28):").pack(pady=10)
    vencimento_var = tk.IntVar(value=manager.obter_vencimento_fatura())
    spin = tk.Spinbox(janela_config, from_=1, to=28, textvariable=vencimento_var)
    spin.pack(pady=5)

    def salvar():
        manager.configurar_vencimento_fatura(vencimento_var.get())
        messagebox.showinfo("Sucesso", "Vencimento salvo com sucesso.")
        janela_config.destroy()

    ttk.Button(janela_config, text="💾 Salvar", command=salvar).pack(pady=10)

botoes = [
    ("➕ Adicionar Transação", adicionar_transação),
    ("📄 Ver Transações", ver_transacoes),
    ("📆 Filtrar por Data", filtrar_por_data),
    ("📤 Exportar para Excel", exportar_excel),
    ("📊 Gerar Gráficos", gerar_grafico),
    ("📥 Importar Planilha", importar_planilha),
    ("⚙️ Configurações", configurar_vencimento_fatura),
    ("⛔ Sair", lambda: root.destroy())
]
for texto, comando in botoes:
    btn = ttk.Button(root, text=texto, command=comando)
    btn.pack(pady=10, fill="x", padx=50)

#rodar interface
root.mainloop()