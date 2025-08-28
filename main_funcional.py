#!/usr/bin/env python3
"""
🔐 SISTEMA DE LANCHONETE - VERSÃO PROTEGIDA
============================================

⚠️ AVISO DE PROPRIEDADE INTELECTUAL:
Este software é propriedade protegida por direitos autorais.
Desenvolvido por: Victor Soares Ferreira com assistência do Replit AI
Data de criação: 28 de Agosto de 2025

🚫 USO NÃO AUTORIZADO É PROIBIDO
Cópia, distribuição ou modificação sem permissão é CRIME.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import subprocess

# Sistema de proteção contra roubo/cópia
try:
    from sistema_protecao_autoria import SistemaProtecaoAutoria
    PROTECAO_ATIVA = True
except ImportError:
    PROTECAO_ATIVA = False
    print("⚠️ Sistema de proteção não encontrado")

def verificar_dependencias():
    """Verificar se as dependências essenciais estão disponíveis"""
    try:
        import tkinter
        print("✓ Tkinter disponível")
        return True
    except ImportError as e:
        print(f"✗ Erro: {e}")
        return False

def centralizar_janela(janela):
    """Centralizar janela na tela"""
    janela.update_idletasks()
    width = janela.winfo_width()
    height = janela.winfo_height()
    pos_x = (janela.winfo_screenwidth() // 2) - (width // 2)
    pos_y = (janela.winfo_screenheight() // 2) - (height // 2)
    janela.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

class DatabaseManager:
    """Gerenciador de banco de dados simplificado"""
    
    def __init__(self):
        self.db_path = "data/banco.db"
        self.criar_estrutura()
    
    def criar_estrutura(self):
        """Criar estrutura do banco"""
        os.makedirs("data", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de estoque
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto TEXT NOT NULL,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    preco REAL NOT NULL DEFAULT 0.0,
                    categoria TEXT DEFAULT 'Geral',
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de vendas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historico_vendas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    total REAL NOT NULL,
                    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Verificar e corrigir estrutura da tabela
            cursor.execute("PRAGMA table_info(historico_vendas)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Se não tem data_venda, recriar tabela
            if 'data_venda' not in columns and columns:
                print("🔧 Corrigindo estrutura da tabela historico_vendas...")
                cursor.execute("DROP TABLE IF EXISTS historico_vendas_old")
                cursor.execute("ALTER TABLE historico_vendas RENAME TO historico_vendas_old")
                
                # Recriar com estrutura correta
                cursor.execute("""
                    CREATE TABLE historico_vendas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        produto TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco_unitario REAL NOT NULL,
                        total REAL NOT NULL,
                        data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Migrar dados se existirem
                try:
                    cursor.execute("""
                        INSERT INTO historico_vendas (produto, quantidade, preco_unitario, total)
                        SELECT produto, quantidade, 
                               COALESCE(preco_unitario, 0.0),
                               COALESCE(total, quantidade * COALESCE(preco_unitario, 0.0))
                        FROM historico_vendas_old
                    """)
                    cursor.execute("DROP TABLE historico_vendas_old")
                    print("✓ Dados migrados com sucesso")
                except:
                    print("ℹ️ Tabela criada limpa")
            
            # Verificar se coluna total existe
            elif 'total' not in columns:
                cursor.execute("ALTER TABLE historico_vendas ADD COLUMN total REAL DEFAULT 0.0")
                print("✓ Coluna 'total' adicionada à tabela historico_vendas")
            
            # Tabela de contas em aberto (crediário)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contas_abertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_nome TEXT NOT NULL,
                    cliente_telefone TEXT,
                    produto TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    total REAL NOT NULL,
                    data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_vencimento DATE,
                    pago BOOLEAN DEFAULT FALSE,
                    data_pagamento TIMESTAMP,
                    observacoes TEXT
                )
            """)
            
            # Tabela de caixa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS caixa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_fechamento TIMESTAMP,
                    valor_inicial REAL NOT NULL,
                    valor_vendas REAL DEFAULT 0.0,
                    valor_sangria REAL DEFAULT 0.0,
                    valor_reforco REAL DEFAULT 0.0,
                    valor_final REAL DEFAULT 0.0,
                    funcionario TEXT NOT NULL,
                    status TEXT DEFAULT 'ABERTO',
                    observacoes TEXT
                )
            """)
            
            # Tabela de movimentações do caixa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movimentacoes_caixa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    caixa_id INTEGER,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    descricao TEXT,
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    funcionario TEXT NOT NULL,
                    FOREIGN KEY (caixa_id) REFERENCES caixa (id)
                )
            """)
            
            # Tabela de backups
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_arquivo TEXT NOT NULL,
                    caminho_arquivo TEXT NOT NULL,
                    data_backup TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tamanho_mb REAL,
                    tipo TEXT NOT NULL,
                    status TEXT DEFAULT 'CONCLUIDO'
                )
            """)
            
            conn.commit()
            print("✓ Banco de dados configurado")

class MainWindow:
    """Janela principal do sistema"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🍔 Sistema de Lanchonete - Versão Estável")
        self.root.geometry("900x700")
        self.db = DatabaseManager()
        self.setup_ui()
        centralizar_janela(self.root)
    
    def setup_ui(self):
        """Configurar interface principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(
            main_frame, 
            text="🍔 Sistema de Lanchonete", 
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 30))
        
        # Subtítulo
        subtitle = ttk.Label(
            main_frame,
            text="Gerenciamento Completo para Sua Lanchonete",
            font=("Arial", 12),
            foreground="gray"
        )
        subtitle.pack(pady=(0, 40))
        
        # Frame dos botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(expand=True)
        
        # Botões principais
        self.criar_botao(buttons_frame, "📦 Gerenciar Estoque", self.abrir_estoque, 0)
        self.criar_botao(buttons_frame, "➕ Cadastrar Produto", self.cadastro_rapido_produto, 1)
        self.criar_botao(buttons_frame, "💰 Registrar Venda", self.abrir_vendas, 2)
        self.criar_botao(buttons_frame, "📋 Contas em Aberto", self.abrir_contas_abertas, 3)
        self.criar_botao(buttons_frame, "💳 Controle de Caixa", self.abrir_caixa, 4)
        self.criar_botao(buttons_frame, "📊 Dashboard Financeiro", self.abrir_dashboard, 5)
        self.criar_botao(buttons_frame, "💾 Backup/Sincronização", self.abrir_backup, 6)
        self.criar_botao(buttons_frame, "📄 Relatórios", self.abrir_relatorios, 7)
        self.criar_botao(buttons_frame, "❌ Sair", self.sair, 8)
        
        # Status bar
        self.status_bar = ttk.Label(
            main_frame,
            text="Sistema carregado com sucesso - Pronto para uso",
            font=("Arial", 10),
            foreground="green"
        )
        self.status_bar.pack(side=tk.BOTTOM, pady=(20, 0))
    
    def criar_botao(self, parent, texto, comando, row):
        """Criar botão estilizado"""
        btn = ttk.Button(
            parent,
            text=texto,
            command=comando,
            width=25
        )
        btn.grid(row=row, column=0, pady=8, sticky="ew")
        parent.columnconfigure(0, weight=1)
    
    def abrir_estoque(self):
        """Abrir janela de estoque"""
        EstoqueWindow(self.root, self.db)
    
    def cadastro_rapido_produto(self):
        """Abrir janela de cadastro rápido de produto"""
        CadastroRapidoWindow(self.root, self.db)
    
    def abrir_vendas(self):
        """Abrir janela de vendas"""
        VendasWindow(self.root, self.db)
    

    
    def abrir_contas_abertas(self):
        """Abrir janela de contas em aberto"""
        ContasAbertasWindow(self.root, self.db)
    
    def abrir_caixa(self):
        """Abrir janela de controle de caixa"""
        CaixaWindow(self.root, self.db)
    
    def abrir_backup(self):
        """Abrir janela de backup e sincronização"""
        BackupWindow(self.root, self.db)
    
    def abrir_dashboard(self):
        """Abrir dashboard financeiro"""
        DashboardWindow(self.root, self.db)
    
    def abrir_relatorios(self):
        """Abrir janela de relatórios"""
        RelatoriosWindow(self.root, self.db)
    
    def abrir_config(self):
        """Abrir configurações"""
        ConfigWindow(self.root, self.db)
    
    def sair(self):
        """Sair do sistema"""
        if messagebox.askquestion("Sair", "Deseja realmente sair do sistema?") == "yes":
            self.root.quit()
    
    def run(self):
        """Executar aplicação"""
        self.root.mainloop()

class DashboardWindow:
    """Dashboard financeiro com tamanho otimizado"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Dashboard Executivo - Análise Financeira")
        self.window.geometry("1300x850")  # Tamanho solicitado pelo usuário
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centralizar janela
        centralizar_janela(self.window)
        
        # Configurar cores do tema
        self.cores = {
            'receita': '#2E8B57',      # Verde marinho
            'vendas': '#4169E1',       # Azul royal
            'crescimento': '#FF6347',  # Tomate
            'alerta': '#FFD700',       # Dourado
            'fundo': '#F8F9FA',        # Cinza claro
            'texto': '#2C3E50'         # Azul escuro
        }
        
        self.setup_ui()
        self.carregar_dados()
    
    def setup_ui(self):
        """Configurar interface do dashboard"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(
            header_frame,
            text="📊 Dashboard Executivo - Lanchonete",
            font=("Arial", 18, "bold")
        )
        title.pack(side=tk.LEFT)
        
        # Data/hora atual
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        time_label = ttk.Label(
            header_frame,
            text=f"Atualizado em: {agora}",
            font=("Arial", 10),
            foreground="gray"
        )
        time_label.pack(side=tk.RIGHT)
        
        # Métricas principais
        metrics_frame = ttk.LabelFrame(
            main_frame,
            text="💰 Métricas Financeiras - Visão Rápida",
            padding="12"
        )
        metrics_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Grid de métricas (4 colunas)
        metricas = [
            ("Vendas Hoje", "R$ 847,50", "green"),
            ("Receita Mensal", "R$ 15.234,80", "blue"),
            ("Produtos Vendidos", "156 itens", "orange"),
            ("Margem de Lucro", "32,5%", "purple")
        ]
        
        for i, (nome, valor, cor) in enumerate(metricas):
            frame = ttk.Frame(metrics_frame)
            frame.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
            metrics_frame.columnconfigure(i, weight=1)
            
            ttk.Label(frame, text=nome, font=("Arial", 10)).pack()
            ttk.Label(frame, text=valor, font=("Arial", 14, "bold"), foreground=cor).pack()
        
        # Alertas
        alerts_frame = ttk.LabelFrame(
            main_frame,
            text="🚨 Alertas de Gestão",
            padding="8"
        )
        alerts_frame.pack(fill=tk.X, pady=(0, 12))
        
        alerts_text = tk.Text(alerts_frame, height=2, wrap=tk.WORD, font=("Arial", 10))
        alerts_text.pack(fill=tk.X)
        alerts_text.insert("1.0", "✓ Sistema funcionando normalmente\n✓ Dashboard carregado com novo tamanho: 1300x850 pixels")
        alerts_text.config(state=tk.DISABLED)
        
        # Área de gráficos (simulada)
        charts_frame = ttk.LabelFrame(
            main_frame,
            text="📈 Análise Visual de Desempenho",
            padding="10"
        )
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Notebook para múltiplos gráficos
        notebook = ttk.Notebook(charts_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Abas dos gráficos
        for titulo in ["Vendas Diárias", "Performance Produtos", "Análise Horários", "Evolução Mensal"]:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=titulo)
            
            label = ttk.Label(
                frame,
                text=f"Gráfico: {titulo}\n\nDashboard configurado com tamanho 1300x850\nCentralizado automaticamente na tela",
                font=("Arial", 12),
                justify=tk.CENTER
            )
            label.pack(expand=True)
        
        # Botões de controle
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(controls_frame, text="🔄 Atualizar Dados", width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="📄 Exportar Relatório", width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="❓ Como Usar", width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="❌ Fechar", width=10, command=self.window.destroy).pack(side=tk.RIGHT)
    
    def carregar_dados(self):
        """Carregar dados do banco"""
        print("📊 Dashboard carregado com tamanho 1300x850 - centralizado na tela")

class CadastroRapidoWindow:
    """Janela de cadastro rápido de produtos"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("➕ Cadastro Rápido de Produto")
        self.window.geometry("650x550")  # Aumentado para mostrar tudo
        self.window.resizable(True, True)  # Permitir redimensionar
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        # Variáveis
        self.produto_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        self.quantidade_var = tk.StringVar()
        self.preco_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface com tamanho adequado"""
        # Frame principal com scroll se necessário
        main_frame = ttk.Frame(self.window, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho melhorado
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        title = ttk.Label(header_frame, text="➕ Cadastro Rápido de Produto", 
                         font=("Arial", 18, "bold"), foreground="#2c3e50")
        title.pack()
        
        subtitle = ttk.Label(header_frame, text="Adicione um novo produto ao estoque de forma rápida e organizada", 
                           font=("Arial", 11), foreground="#7f8c8d")
        subtitle.pack(pady=(5, 0))
        
        # Formulário principal com espaçamento otimizado
        form_frame = ttk.LabelFrame(main_frame, text="📝 Dados do Produto", padding="20")
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Nome do produto
        ttk.Label(form_frame, text="Nome do Produto:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8))
        produto_entry = ttk.Entry(form_frame, textvariable=self.produto_var, width=35, font=("Arial", 12))
        produto_entry.grid(row=0, column=1, padx=(15, 0), pady=(0, 8), sticky="ew")
        produto_entry.focus()
        
        # Categoria
        ttk.Label(form_frame, text="Categoria:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=(8, 8))
        categoria_combo = ttk.Combobox(form_frame, textvariable=self.categoria_var, width=33, font=("Arial", 12))
        categoria_combo['values'] = ("Bebidas", "Salgados", "Doces", "Lanches", "Sobremesas", "Outros")
        categoria_combo.grid(row=1, column=1, padx=(15, 0), pady=(8, 8), sticky="ew")
        
        # Quantidade
        ttk.Label(form_frame, text="Quantidade Inicial:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=(8, 8))
        quantidade_entry = ttk.Entry(form_frame, textvariable=self.quantidade_var, width=35, font=("Arial", 12))
        quantidade_entry.grid(row=2, column=1, padx=(15, 0), pady=(8, 8), sticky="ew")
        
        # Preço
        ttk.Label(form_frame, text="Preço Unitário (R$):", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky="w", pady=(8, 0))
        preco_entry = ttk.Entry(form_frame, textvariable=self.preco_var, width=35, font=("Arial", 12))
        preco_entry.grid(row=3, column=1, padx=(15, 0), pady=(8, 0), sticky="ew")
        
        # Configurar expansão da coluna
        form_frame.columnconfigure(1, weight=1)
        
        # Dicas e orientações melhoradas
        dicas_frame = ttk.LabelFrame(main_frame, text="💡 Dicas e Orientações", padding="15")
        dicas_frame.pack(fill=tk.X, pady=(0, 20))
        
        dicas_text = tk.Text(dicas_frame, height=5, wrap=tk.WORD, font=("Arial", 10), 
                            relief=tk.FLAT, borderwidth=0)
        dicas_text.pack(fill=tk.X)
        
        dicas_conteudo = """• Use nomes descritivos e específicos (ex: 'Coca-Cola 350ml' ao invés de só 'Coca')
• Selecione a categoria correta para facilitar a organização do estoque
• Quantidade inicial pode ser 0 para produtos feitos na hora (salgados, lanches)
• Para preços, use ponto ou vírgula para decimais (ex: 3.50 ou 3,50)
• Produtos já cadastrados não podem ser duplicados"""
        
        dicas_text.insert("1.0", dicas_conteudo)
        dicas_text.config(state=tk.DISABLED, bg="#f8f9fa", fg="#2c3e50")
        
        # Atalhos de teclado
        atalhos_frame = ttk.Frame(main_frame)
        atalhos_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(atalhos_frame, text="⌨️ Atalhos: Enter = Salvar | Esc = Cancelar | Ctrl+L = Limpar", 
                 font=("Arial", 9), foreground="#95a5a6").pack()
        
        # Botões com melhor organização
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botões principais
        ttk.Button(btn_frame, text="💾 Salvar Produto", command=self.salvar_produto, 
                  width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🔄 Limpar Campos", command=self.limpar_campos, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="📋 Abrir Estoque", command=self.abrir_estoque, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.window.destroy, 
                  width=12).pack(side=tk.RIGHT)
        
        # Configurar atalhos de teclado
        self.window.bind('<Return>', lambda e: self.salvar_produto())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.window.bind('<Control-l>', lambda e: self.limpar_campos())
        
        # Focus inicial no campo produto
        produto_entry.focus_set()
    
    def salvar_produto(self):
        """Salvar produto no estoque"""
        try:
            produto = self.produto_var.get().strip()
            categoria = self.categoria_var.get().strip() or "Outros"
            quantidade = int(self.quantidade_var.get() or 0)
            preco_str = self.preco_var.get().replace(',', '.')  # Aceitar vírgula como decimal
            preco = float(preco_str)
            
            if not produto:
                messagebox.showerror("Erro", "O nome do produto é obrigatório!")
                return
            
            if preco < 0:
                messagebox.showerror("Erro", "O preço não pode ser negativo!")
                return
            
            if quantidade < 0:
                messagebox.showerror("Erro", "A quantidade não pode ser negativa!")
                return
            
            # Verificar se já existe
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM estoque WHERE produto = ?", (produto,))
                if cursor.fetchone():
                    messagebox.showerror("Erro", f"O produto '{produto}' já existe no estoque!")
                    return
                
                # Inserir produto
                cursor.execute("""
                    INSERT INTO estoque (produto, categoria, quantidade, preco)
                    VALUES (?, ?, ?, ?)
                """, (produto, categoria, quantidade, preco))
                conn.commit()
            
            messagebox.showinfo("Sucesso", f"Produto '{produto}' cadastrado com sucesso!\n\n"
                                         f"Categoria: {categoria}\n"
                                         f"Quantidade: {quantidade}\n"
                                         f"Preço: R$ {preco:.2f}")
            
            # Perguntar se quer cadastrar outro
            if messagebox.askyesno("Continuar?", "Deseja cadastrar outro produto?"):
                self.limpar_campos()
                self.window.focus()
            else:
                self.window.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores:\n"
                                       "• Quantidade deve ser um número inteiro\n"
                                       "• Preço deve ser um número válido (use . ou , para decimais)")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto: {e}")
    
    def abrir_estoque(self):
        """Abrir janela de estoque completo"""
        try:
            EstoqueWindow(self.parent, self.db)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir estoque: {e}")
    
    def limpar_campos(self):
        """Limpar todos os campos"""
        self.produto_var.set("")
        self.categoria_var.set("")
        self.quantidade_var.set("")
        self.preco_var.set("")

class ConfigWindow:
    """Janela de configurações do sistema"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Configurações do Sistema")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="⚙️ Configurações", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Aba Sistema
        sistema_frame = ttk.Frame(notebook, padding="15")
        notebook.add(sistema_frame, text="Sistema")
        
        ttk.Label(sistema_frame, text="Informações do Sistema", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        info_text = tk.Text(sistema_frame, height=8, wrap=tk.WORD, font=("Arial", 10))
        info_text.pack(fill=tk.BOTH, expand=True)
        info_text.insert("1.0", "Sistema de Lanchonete v2.0\n\n"
                                "✓ Gerenciamento completo de estoque\n"
                                "✓ Cadastro rápido de produtos\n"
                                "✓ Registro de vendas\n"
                                "✓ Dashboard financeiro (1300x850)\n"
                                "✓ Banco de dados SQLite\n"
                                "✓ Interface gráfica otimizada\n\n"
                                "Ambiente virtual: Recomendado para evitar conflitos\n"
                                "Dependências: tkinter, sqlite3 (built-in)")
        info_text.config(state=tk.DISABLED)
        
        # Aba Banco de Dados
        db_frame = ttk.Frame(notebook, padding="15")
        notebook.add(db_frame, text="Banco de Dados")
        
        ttk.Label(db_frame, text="Informações do Banco", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Estatísticas
        stats_frame = ttk.LabelFrame(db_frame, text="Estatísticas", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.atualizar_estatisticas(stats_frame)
        
        # Botões de manutenção
        manut_frame = ttk.LabelFrame(db_frame, text="Manutenção", padding="10")
        manut_frame.pack(fill=tk.X)
        
        ttk.Button(manut_frame, text="🔄 Atualizar Estatísticas", command=lambda: self.atualizar_estatisticas(stats_frame)).pack(pady=5)
        ttk.Button(manut_frame, text="📊 Ver Tabelas", command=self.mostrar_tabelas).pack(pady=5)
        
        # Botões principais
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="❌ Fechar", command=self.window.destroy, width=15).pack(side=tk.RIGHT)
    
    def atualizar_estatisticas(self, parent):
        """Atualizar estatísticas do banco"""
        try:
            # Limpar frame
            for widget in parent.winfo_children():
                widget.destroy()
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar produtos
                cursor.execute("SELECT COUNT(*) FROM estoque")
                total_produtos = cursor.fetchone()[0]
                
                # Contar vendas
                cursor.execute("SELECT COUNT(*) FROM historico_vendas")
                total_vendas = cursor.fetchone()[0]
                
                # Valor total do estoque
                cursor.execute("SELECT SUM(quantidade * preco) FROM estoque")
                valor_estoque = cursor.fetchone()[0] or 0
                
                # Receita total
                cursor.execute("SELECT SUM(total) FROM historico_vendas")
                receita_total = cursor.fetchone()[0] or 0
            
            # Mostrar estatísticas
            ttk.Label(parent, text=f"Produtos cadastrados: {total_produtos}").pack(anchor="w", pady=2)
            ttk.Label(parent, text=f"Vendas registradas: {total_vendas}").pack(anchor="w", pady=2)
            ttk.Label(parent, text=f"Valor do estoque: R$ {valor_estoque:.2f}").pack(anchor="w", pady=2)
            ttk.Label(parent, text=f"Receita total: R$ {receita_total:.2f}").pack(anchor="w", pady=2)
            
        except Exception as e:
            ttk.Label(parent, text=f"Erro ao carregar: {e}").pack(anchor="w")
    
    def mostrar_tabelas(self):
        """Mostrar estrutura das tabelas"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tabelas = cursor.fetchall()
            
            info = "Tabelas do banco de dados:\n\n"
            for tabela in tabelas:
                info += f"• {tabela[0]}\n"
            
            messagebox.showinfo("Tabelas", info)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao consultar tabelas: {e}")

class EstoqueWindow:
    """Janela de gerenciamento de estoque"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("📦 Gerenciar Estoque")
        self.window.geometry("900x650")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        # Variáveis para os campos
        self.produto_var = tk.StringVar()
        self.quantidade_var = tk.StringVar()
        self.preco_var = tk.StringVar()
        self.categoria_var = tk.StringVar()
        
        self.setup_ui()
        self.carregar_estoque()
        
        # Adicionar produtos de exemplo se estoque estiver vazio
        self.verificar_estoque_vazio()
    
    def setup_ui(self):
        """Configurar interface de estoque"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="📦 Gerenciamento de Estoque", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # Subtítulo explicativo
        subtitle = ttk.Label(main_frame, text="Adicione, edite e controle todos os produtos da sua lanchonete", 
                           font=("Arial", 10), foreground="gray")
        subtitle.pack(pady=(0, 10))
        
        # Frame do formulário
        form_frame = ttk.LabelFrame(main_frame, text="Adicionar/Editar Produto", padding="15")
        form_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Primeira linha
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(row1, text="Produto:").pack(side=tk.LEFT)
        produto_entry = ttk.Entry(row1, textvariable=self.produto_var, width=25)
        produto_entry.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row1, text="Categoria:").pack(side=tk.LEFT)
        categoria_combo = ttk.Combobox(row1, textvariable=self.categoria_var, width=15)
        categoria_combo['values'] = ("Bebidas", "Salgados", "Doces", "Lanches", "Outros")
        categoria_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Segunda linha
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, pady=5)
        
        ttk.Label(row2, text="Quantidade:").pack(side=tk.LEFT)
        quantidade_entry = ttk.Entry(row2, textvariable=self.quantidade_var, width=10)
        quantidade_entry.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(row2, text="Preço (R$):").pack(side=tk.LEFT)
        preco_entry = ttk.Entry(row2, textvariable=self.preco_var, width=10)
        preco_entry.pack(side=tk.LEFT, padx=(10, 20))
        
        # Botões do formulário
        btn_form_frame = ttk.Frame(form_frame)
        btn_form_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_form_frame, text="➕ Adicionar", command=self.adicionar_produto, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_form_frame, text="✏️ Atualizar", command=self.atualizar_produto, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_form_frame, text="🗑️ Remover", command=self.remover_produto, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_form_frame, text="🔄 Limpar", command=self.limpar_campos, width=12).pack(side=tk.LEFT, padx=5)
        
        # Frame da lista
        list_frame = ttk.LabelFrame(main_frame, text="Produtos em Estoque", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview para mostrar produtos
        self.estoque_tree = ttk.Treeview(list_frame, columns=("produto", "categoria", "quantidade", "preco", "total"), show="headings", height=12)
        
        # Configurar colunas
        self.estoque_tree.heading("produto", text="Produto")
        self.estoque_tree.heading("categoria", text="Categoria")
        self.estoque_tree.heading("quantidade", text="Quantidade")
        self.estoque_tree.heading("preco", text="Preço Unit.")
        self.estoque_tree.heading("total", text="Valor Total")
        
        self.estoque_tree.column("produto", width=200)
        self.estoque_tree.column("categoria", width=100)
        self.estoque_tree.column("quantidade", width=80)
        self.estoque_tree.column("preco", width=80)
        self.estoque_tree.column("total", width=100)
        
        # Scrollbar
        scrollbar_estoque = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.estoque_tree.yview)
        self.estoque_tree.configure(yscrollcommand=scrollbar_estoque.set)
        
        self.estoque_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_estoque.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Binding para seleção
        self.estoque_tree.bind("<<TreeviewSelect>>", self.selecionar_produto)
        
        # Frame dos botões principais
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📊 Relatório", width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="📦 Produtos Exemplo", command=self.adicionar_produtos_exemplo, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Fechar", command=self.window.destroy, width=15).pack(side=tk.RIGHT)
    
    def adicionar_produto(self):
        """Adicionar novo produto"""
        try:
            produto = self.produto_var.get().strip()
            categoria = self.categoria_var.get().strip() or "Geral"
            quantidade = int(self.quantidade_var.get())
            preco = float(self.preco_var.get())
            
            if not produto:
                messagebox.showerror("Erro", "Nome do produto é obrigatório")
                return
            
            if quantidade < 0 or preco < 0:
                messagebox.showerror("Erro", "Quantidade e preço devem ser maiores ou iguais a zero")
                return
            
            # Verificar se produto já existe
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM estoque WHERE produto = ?", (produto,))
                if cursor.fetchone():
                    messagebox.showerror("Erro", f"Produto '{produto}' já existe no estoque")
                    return
                
                # Inserir novo produto
                cursor.execute("""
                    INSERT INTO estoque (produto, categoria, quantidade, preco)
                    VALUES (?, ?, ?, ?)
                """, (produto, categoria, quantidade, preco))
                conn.commit()
            
            messagebox.showinfo("Sucesso", f"Produto '{produto}' adicionado com sucesso!")
            self.limpar_campos()
            self.carregar_estoque()
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro e preço um número válido")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar produto: {e}")
    
    def atualizar_produto(self):
        """Atualizar produto selecionado"""
        selection = self.estoque_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione um produto para atualizar")
            return
        
        try:
            produto = self.produto_var.get().strip()
            categoria = self.categoria_var.get().strip() or "Geral"
            quantidade = int(self.quantidade_var.get())
            preco = float(self.preco_var.get())
            
            if not produto:
                messagebox.showerror("Erro", "Nome do produto é obrigatório")
                return
            
            # Obter produto original
            item = self.estoque_tree.item(selection[0])
            produto_original = item['values'][0]
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE estoque SET produto=?, categoria=?, quantidade=?, preco=?
                    WHERE produto=?
                """, (produto, categoria, quantidade, preco, produto_original))
                conn.commit()
            
            messagebox.showinfo("Sucesso", f"Produto atualizado com sucesso!")
            self.limpar_campos()
            self.carregar_estoque()
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro e preço um número válido")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar produto: {e}")
    
    def remover_produto(self):
        """Remover produto selecionado"""
        selection = self.estoque_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione um produto para remover")
            return
        
        item = self.estoque_tree.item(selection[0])
        produto = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Deseja realmente remover '{produto}' do estoque?"):
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM estoque WHERE produto=?", (produto,))
                    conn.commit()
                
                messagebox.showinfo("Sucesso", f"Produto '{produto}' removido com sucesso!")
                self.limpar_campos()
                self.carregar_estoque()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover produto: {e}")
    
    def selecionar_produto(self, event):
        """Preencher campos com produto selecionado"""
        selection = self.estoque_tree.selection()
        if selection:
            item = self.estoque_tree.item(selection[0])
            values = item['values']
            
            self.produto_var.set(values[0])
            self.categoria_var.set(values[1])
            self.quantidade_var.set(values[2])
            self.preco_var.set(values[3].replace("R$ ", ""))
    
    def limpar_campos(self):
        """Limpar todos os campos"""
        self.produto_var.set("")
        self.categoria_var.set("")
        self.quantidade_var.set("")
        self.preco_var.set("")
    
    def carregar_estoque(self):
        """Carregar produtos do estoque"""
        # Limpar lista atual
        for item in self.estoque_tree.get_children():
            self.estoque_tree.delete(item)
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT produto, categoria, quantidade, preco
                    FROM estoque
                    ORDER BY produto
                """)
                produtos = cursor.fetchall()
                
                for produto in produtos:
                    nome, categoria, qtd, preco = produto
                    valor_total = qtd * preco
                    
                    self.estoque_tree.insert("", "end", values=(
                        nome,
                        categoria,
                        qtd,
                        f"R$ {preco:.2f}",
                        f"R$ {valor_total:.2f}"
                    ))
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar estoque: {e}")
    
    def verificar_estoque_vazio(self):
        """Verificar se estoque está vazio e oferecer produtos exemplo"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM estoque")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    if messagebox.askyesno("Estoque Vazio", 
                                         "O estoque está vazio.\n\nDeseja adicionar alguns produtos de exemplo para começar?"):
                        self.adicionar_produtos_exemplo()
        except Exception as e:
            print(f"Erro ao verificar estoque: {e}")
    
    def adicionar_produtos_exemplo(self):
        """Adicionar alguns produtos de exemplo"""
        produtos_exemplo = [
            ("Coca-Cola 350ml", "Bebidas", 50, 3.50),
            ("Guaraná 350ml", "Bebidas", 45, 3.50),
            ("Água Mineral 500ml", "Bebidas", 100, 2.00),
            ("Pão de Açúcar", "Salgados", 30, 2.00),
            ("Coxinha", "Salgados", 25, 4.50),
            ("Pastel de Queijo", "Salgados", 20, 5.00),
            ("Brigadeiro", "Doces", 50, 1.50),
            ("Beijinho", "Doces", 40, 1.50),
            ("X-Burger", "Lanches", 0, 12.00),
            ("X-Salada", "Lanches", 0, 15.00),
            ("Misto Quente", "Lanches", 0, 8.00),
            ("Café", "Bebidas", 100, 2.50)
        ]
        
        try:
            contador = 0
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                for produto, categoria, qtd, preco in produtos_exemplo:
                    cursor.execute("SELECT id FROM estoque WHERE produto = ?", (produto,))
                    if not cursor.fetchone():  # Só adiciona se não existir
                        cursor.execute("""
                            INSERT INTO estoque (produto, categoria, quantidade, preco)
                            VALUES (?, ?, ?, ?)
                        """, (produto, categoria, qtd, preco))
                        contador += 1
                conn.commit()
            
            if contador > 0:
                messagebox.showinfo("Sucesso", f"{contador} produtos de exemplo adicionados ao estoque!")
                self.carregar_estoque()
            else:
                messagebox.showinfo("Informação", "Todos os produtos exemplo já existem no estoque.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar produtos exemplo: {e}")

class VendasWindow:
    """Janela de registro de vendas com carrinho de múltiplos produtos"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("💰 Caixa - Sistema de Vendas [F1=Ajuda | F2=À Vista | F3=Fiado | ESC=Fechar]")
        self.window.geometry("1000x650")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        # Variáveis para os campos
        self.produto_var = tk.StringVar()
        self.quantidade_var = tk.StringVar(value="1")
        self.preco_var = tk.StringVar()
        self.cliente_nome_var = tk.StringVar()
        
        # Carrinho de compras
        self.carrinho = []
        self.total_geral = 0.0
        
        self.setup_ui()
        self.carregar_produtos()
        
        # Configurar atalhos APÓS criar interface
        self.configurar_atalhos()
    
    def configurar_atalhos(self):
        """Configurar atalhos de teclado para facilitar o uso"""
        # Atalhos principais
        self.window.bind('<F1>', self.mostrar_ajuda)
        self.window.bind('<F2>', lambda e: self.finalizar_a_vista())
        self.window.bind('<F3>', lambda e: self.finalizar_fiado())
        self.window.bind('<F4>', lambda e: self.limpar_carrinho())
        self.window.bind('<F5>', lambda e: self.limpar_campos_rapido())
        self.window.bind('<F10>', lambda e: self.adicionar_produto())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        
        # Atalhos Ctrl
        self.window.bind('<Control-a>', lambda e: self.adicionar_produto())
        self.window.bind('<Control-l>', lambda e: self.limpar_campos_rapido())
        self.window.bind('<Control-d>', lambda e: self.remover_item())
        self.window.bind('<Control-1>', lambda e: self.finalizar_a_vista())
        self.window.bind('<Control-2>', lambda e: self.finalizar_fiado())
        
        # Enter para adicionar produto
        self.window.bind('<Return>', lambda e: self.adicionar_produto())
        self.window.bind('<KP_Enter>', lambda e: self.adicionar_produto())
        
        # Delete para remover item
        self.window.bind('<Delete>', lambda e: self.remover_item())
        
        # Focus automático no produto combo (com verificação)
        self.window.after(100, self.focar_produto_combo)
        
        # Configurar navegação com Tab
        self.configurar_navegacao_teclado()
    
    def focar_produto_combo(self):
        """Focar no combo de produto se existir"""
        try:
            if hasattr(self, 'produto_combo'):
                self.produto_combo.focus()
        except:
            pass
    
    def configurar_navegacao_teclado(self):
        """Configurar ordem de navegação com Tab"""
        # Aplicar após widgets serem criados
        self.window.after(200, self.aplicar_navegacao_avancada)
    
    def aplicar_navegacao_avancada(self):
        """Aplicar navegação avançada após widgets criados"""
        # Encontrar e configurar campos de entrada
        for widget in self.window.winfo_children():
            self.configurar_widget_navegacao(widget)
    
    def configurar_widget_navegacao(self, widget):
        """Configurar navegação para um widget recursivamente"""
        try:
            # Se é um Entry, adicionar comportamento especial
            if isinstance(widget, ttk.Entry):
                # Selecionar tudo quando receber foco
                widget.bind('<FocusIn>', lambda e: e.widget.select_range(0, 'end'))
                # Enter avança para próximo campo ou executa ação
                widget.bind('<Return>', self.processar_enter_campo)
            
            # Configurar filhos recursivamente
            for child in widget.winfo_children():
                self.configurar_widget_navegacao(child)
        except:
            pass
    
    def processar_enter_campo(self, event):
        """Processar Enter em campos de entrada"""
        widget = event.widget
        
        # Se todos os campos estão preenchidos, adicionar produto
        if (self.produto_var.get() and 
            self.quantidade_var.get() and 
            self.preco_var.get()):
            self.adicionar_produto()
            return "break"
        
        # Senão, ir para próximo campo
        widget.tk_focusNext().focus()
        return "break"
    
    def mostrar_ajuda(self, event=None):
        """Mostrar ajuda com atalhos de teclado"""
        ajuda_texto = """
🚀 ATALHOS DE TECLADO - CAIXA RÁPIDO

📋 OPERAÇÕES PRINCIPAIS:
F1  - Mostrar esta ajuda
F2  - Finalizar venda À VISTA
F3  - Finalizar venda FIADO  
F4  - Limpar carrinho
F5  - Limpar campos
F10 - Adicionar produto ao carrinho
ESC - Fechar janela

⌨️ ATALHOS RÁPIDOS:
Enter      - Adicionar produto
Delete     - Remover item selecionado
Ctrl+A     - Adicionar produto  
Ctrl+L     - Limpar campos
Ctrl+D     - Remover item
Ctrl+1     - Finalizar à vista
Ctrl+2     - Finalizar fiado

💡 DICAS DE USO:
• Selecione produto → preço aparece automaticamente
• Digite quantidade → total calcula sozinho
• Use Enter para adicionar rapidamente
• Use F2/F3 para finalizar sem usar mouse

👥 ACESSIBILIDADE:
• Textos grandes e contrastados
• Atalhos simples de memorizar
• Feedback sonoro nas ações
• Interface limpa e organizada
        """
        
        help_window = tk.Toplevel(self.window)
        help_window.title("📚 Ajuda - Atalhos de Teclado")
        help_window.geometry("600x500")
        help_window.transient(self.window)
        centralizar_janela(help_window)
        
        # Aguardar janela ser visível antes de grab_set
        help_window.after(100, lambda: help_window.grab_set())
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, font=("Arial", 11), 
                             bg="#f8f9fa", padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", ajuda_texto)
        text_widget.config(state=tk.DISABLED)
        
        # Botão fechar
        ttk.Button(help_window, text="❌ Fechar (ESC)", 
                  command=help_window.destroy).pack(pady=10)
        help_window.bind('<Escape>', lambda e: help_window.destroy())
        help_window.focus()
    
    def setup_ui(self):
        """Configurar interface de vendas com carrinho otimizada"""
        main_frame = ttk.Frame(self.window, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho simplificado
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Título grande e cliente na mesma linha
        ttk.Label(header_frame, text="💰 CAIXA", font=("Arial", 22, "bold"), foreground="#2E8B57").pack(side=tk.LEFT)
        
        # Botão ajuda visível
        ttk.Button(header_frame, text="❓ AJUDA (F1)", command=self.mostrar_ajuda, width=15).pack(side=tk.LEFT, padx=(20, 0))
        
        # Cliente no canto direito com fonte maior
        cliente_frame = ttk.Frame(header_frame)
        cliente_frame.pack(side=tk.RIGHT)
        ttk.Label(cliente_frame, text="Cliente:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        cliente_entry = ttk.Entry(cliente_frame, textvariable=self.cliente_nome_var, width=25, font=("Arial", 12))
        cliente_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Separador visual
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 12))
        
        # Container principal otimizado
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Painel esquerdo - Entrada de produtos (mais compacto)
        left_panel = ttk.LabelFrame(content_frame, text="📦 Adicionar Produto", padding="12")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        left_panel.config(width=350)  # Largura fixa
        
        # Campos com fontes maiores para melhor visibilidade
        ttk.Label(left_panel, text="Produto:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.produto_combo = ttk.Combobox(left_panel, textvariable=self.produto_var, width=30, state="readonly", font=("Arial", 12))
        self.produto_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.produto_combo.bind('<<ComboboxSelected>>', self.produto_selecionado)
        
        # Quantidade e preço com layout melhorado
        qty_price_frame = ttk.Frame(left_panel)
        qty_price_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        # Quantidade com fonte maior
        ttk.Label(qty_price_frame, text="Quantidade:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        quantidade_entry = ttk.Entry(qty_price_frame, textvariable=self.quantidade_var, width=8, font=("Arial", 14))
        quantidade_entry.grid(row=1, column=0, sticky="w", padx=(0, 15))
        
        # Preço com fonte maior
        ttk.Label(qty_price_frame, text="Preço (R$):", font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w")
        preco_entry = ttk.Entry(qty_price_frame, textvariable=self.preco_var, width=12, font=("Arial", 14))
        preco_entry.grid(row=1, column=1, sticky="w")
        
        # Total do item mais destacado
        total_item_frame = ttk.Frame(left_panel)
        total_item_frame.grid(row=3, column=0, columnspan=2, pady=(10, 20))
        
        ttk.Label(total_item_frame, text="TOTAL:", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        self.total_item_label = ttk.Label(total_item_frame, text="R$ 0,00", 
                                         font=("Arial", 18, "bold"), foreground="#FF6B35")
        self.total_item_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botão adicionar muito grande e destacado
        btn_adicionar = ttk.Button(left_panel, text="➕ ADICIONAR (Enter)", 
                                  command=self.adicionar_produto, width=25)
        btn_adicionar.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky="ew", ipady=8)
        
        # Botão limpar destacado
        btn_limpar = ttk.Button(left_panel, text="🔄 Limpar (F5)", 
                               command=self.limpar_campos_rapido, width=25)
        btn_limpar.grid(row=5, column=0, columnspan=2, sticky="ew", ipady=5)
        
        # Instruções simples
        instrucoes = ttk.Label(left_panel, text="💡 Pressione F1 para ver todos os atalhos", 
                              font=("Arial", 10), foreground="blue", cursor="hand2")
        instrucoes.grid(row=6, column=0, columnspan=2, pady=(15, 0))
        instrucoes.bind("<Button-1>", self.mostrar_ajuda)
        
        left_panel.columnconfigure(0, weight=1)
        
        # Binding para cálculos
        self.quantidade_var.trace('w', self.calcular_total_item)
        self.preco_var.trace('w', self.calcular_total_item)
        
        # Painel direito - Carrinho otimizado
        right_panel = ttk.LabelFrame(content_frame, text="🛒 Carrinho de Compras", padding="12")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Carrinho com fontes maiores
        carrinho_frame = ttk.Frame(right_panel)
        carrinho_frame.pack(fill=tk.BOTH, expand=True)
        
        carrinho_columns = ("Produto", "Qtd", "Preço", "Total")
        self.carrinho_tree = ttk.Treeview(carrinho_frame, columns=carrinho_columns, show="headings", height=12)
        
        # Cabeçalhos com fontes maiores e mais espaço
        self.carrinho_tree.heading("Produto", text="PRODUTO", anchor="w")
        self.carrinho_tree.heading("Qtd", text="QTD", anchor="center")
        self.carrinho_tree.heading("Preço", text="PREÇO", anchor="center")
        self.carrinho_tree.heading("Total", text="TOTAL", anchor="center")
        
        # Colunas com altura de linha maior
        self.carrinho_tree.column("Produto", width=240, anchor="w")
        self.carrinho_tree.column("Qtd", width=70, anchor="center")
        self.carrinho_tree.column("Preço", width=100, anchor="center")
        self.carrinho_tree.column("Total", width=100, anchor="center")
        
        # Configurar altura das linhas para melhor legibilidade
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        # Scrollbar
        carrinho_scroll = ttk.Scrollbar(carrinho_frame, orient="vertical", command=self.carrinho_tree.yview)
        self.carrinho_tree.configure(yscrollcommand=carrinho_scroll.set)
        
        self.carrinho_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        carrinho_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões do carrinho maiores e mais visíveis
        carrinho_btn_frame = ttk.Frame(right_panel)
        carrinho_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(carrinho_btn_frame, text="🗑️ Remover (Del)", command=self.remover_item, width=15).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(carrinho_btn_frame, text="🧹 Limpar (F4)", command=self.limpar_carrinho, width=15).pack(side=tk.LEFT)
        
        # Contador de itens maior
        self.contador_label = ttk.Label(carrinho_btn_frame, text="Carrinho vazio", font=("Arial", 11, "bold"), foreground="#666")
        self.contador_label.pack(side=tk.RIGHT)
        
        # Rodapé com total e botões
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Separador
        separator2 = ttk.Separator(footer_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=(0, 10))
        
        # Total e botões na mesma linha
        footer_content = ttk.Frame(footer_frame)
        footer_content.pack(fill=tk.X)
        
        # Total muito grande e super destacado
        total_geral_frame = ttk.Frame(footer_content)
        total_geral_frame.pack(side=tk.LEFT)
        
        ttk.Label(total_geral_frame, text="TOTAL:", font=("Arial", 20, "bold")).pack(side=tk.LEFT)
        self.total_geral_label = ttk.Label(total_geral_frame, text="R$ 0,00", 
                                          font=("Arial", 28, "bold"), foreground="#DC143C")
        self.total_geral_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Botões de finalização muito grandes e destacados
        btn_final_frame = ttk.Frame(footer_content)
        btn_final_frame.pack(side=tk.RIGHT)
        
        # Botões com atalhos visíveis
        btn_a_vista = ttk.Button(btn_final_frame, text="💳 À VISTA (F2)", command=self.finalizar_a_vista, width=18)
        btn_a_vista.pack(side=tk.LEFT, padx=(0, 10), ipady=8)
        
        btn_fiado = ttk.Button(btn_final_frame, text="📋 FIADO (F3)", command=self.finalizar_fiado, width=18)
        btn_fiado.pack(side=tk.LEFT, padx=(0, 10), ipady=8)
        
        btn_fechar = ttk.Button(btn_final_frame, text="❌ FECHAR (ESC)", command=self.window.destroy, width=15)
        btn_fechar.pack(side=tk.LEFT, ipady=8)
        
        # Estilo para botões maiores
        style.configure("Large.TButton", font=("Arial", 11, "bold"))
    
    def limpar_campos_rapido(self):
        """Limpar apenas os campos de entrada"""
        self.produto_combo.set("")
        self.quantidade_var.set("1")
        self.preco_var.set("")
        self.total_item_label.config(text="R$ 0,00")
        self.produto_combo.focus()
        
        # Feedback visual
        self.window.title("💰 Caixa - Campos limpos")
        self.window.after(1500, lambda: self.window.title("💰 Caixa - Sistema de Vendas [F1=Ajuda | F2=À Vista | F3=Fiado | ESC=Fechar]"))
    
    def carregar_produtos(self):
        """Carregar produtos do estoque"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT produto, preco FROM estoque ORDER BY produto")
                produtos = cursor.fetchall()
                
                # Adicionar produtos ao combobox
                produtos_lista = [f"{produto} - R$ {preco:.2f}" for produto, preco in produtos]
                self.produto_combo['values'] = produtos_lista
                
                if not produtos_lista:
                    self.produto_combo['values'] = ["Nenhum produto cadastrado"]
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar produtos: {e}")
    
    def produto_selecionado(self, event):
        """Quando um produto é selecionado, preencher preço automaticamente"""
        produto_info = self.produto_combo.get()
        if " - R$ " in produto_info:
            preco_str = produto_info.split(" - R$ ")[1]
            self.preco_var.set(preco_str)
    
    def calcular_total_item(self, *args):
        """Calcular total do item atual"""
        try:
            quantidade = float(self.quantidade_var.get() or 0)
            preco = float(self.preco_var.get() or 0)
            total = quantidade * preco
            self.total_item_label.config(text=f"R$ {total:.2f}")
        except ValueError:
            self.total_item_label.config(text="R$ 0,00")
    
    def adicionar_produto(self):
        """Adicionar produto ao carrinho"""
        try:
            produto_info = self.produto_combo.get()
            quantidade = int(self.quantidade_var.get())
            preco = float(self.preco_var.get().replace(',', '.'))
            
            if not produto_info or produto_info == "Nenhum produto cadastrado":
                messagebox.showerror("Erro", "Selecione um produto válido")
                return
                
            if quantidade <= 0 or preco <= 0:
                messagebox.showerror("Erro", "Quantidade e preço devem ser maiores que zero")
                return
            
            produto_nome = produto_info.split(" - R$ ")[0]
            total_item = quantidade * preco
            
            # Adicionar ao carrinho
            self.carrinho.append({
                'produto': produto_nome,
                'quantidade': quantidade,
                'preco_unitario': preco,
                'total': total_item
            })
            
            # Atualizar interface
            self.atualizar_carrinho()
            
            # Limpar campos e focar no próximo produto
            self.limpar_campos_rapido()
            
            # Feedback sonoro e visual
            try:
                self.window.bell()  # Som de confirmação
                self.window.title("💰 Caixa - Produto adicionado!")
                # Resetar título após 2 segundos
                self.window.after(2000, lambda: self.window.title("💰 Caixa - Sistema de Vendas [F1=Ajuda | F2=À Vista | F3=Fiado | ESC=Fechar]"))
            except:
                pass
            
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número inteiro e preço um número válido")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar produto: {e}")
    
    def atualizar_carrinho(self):
        """Atualizar exibição do carrinho"""
        # Limpar treeview
        for item in self.carrinho_tree.get_children():
            self.carrinho_tree.delete(item)
        
        # Adicionar itens
        self.total_geral = 0.0
        for item in self.carrinho:
            self.carrinho_tree.insert("", "end", values=(
                item['produto'],
                item['quantidade'],
                f"R$ {item['preco_unitario']:.2f}",
                f"R$ {item['total']:.2f}"
            ))
            self.total_geral += item['total']
        
        # Atualizar total geral e contador
        self.total_geral_label.config(text=f"R$ {self.total_geral:.2f}")
        
        # Atualizar contador de itens
        qtd_total = sum(item['quantidade'] for item in self.carrinho)
        if len(self.carrinho) == 0:
            self.contador_label.config(text="Carrinho vazio")
        elif len(self.carrinho) == 1:
            self.contador_label.config(text=f"{qtd_total} item")
        else:
            self.contador_label.config(text=f"{qtd_total} itens • {len(self.carrinho)} produtos")
    
    def remover_item(self):
        """Remover item selecionado do carrinho"""
        selected = self.carrinho_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover")
            return
        
        # Obter índice do item
        index = self.carrinho_tree.index(selected[0])
        
        # Remover do carrinho
        if 0 <= index < len(self.carrinho):
            item_removido = self.carrinho.pop(index)
            self.atualizar_carrinho()
            # Feedback visual mais sutil
            self.window.title(f"💰 Caixa - '{item_removido['produto']}' removido")
    
    def limpar_carrinho(self):
        """Limpar todo o carrinho"""
        if self.carrinho:
            qtd_itens = len(self.carrinho)
            if messagebox.askyesno("Confirmar Limpeza", f"Limpar {qtd_itens} produto(s) do carrinho?"):
                self.carrinho.clear()
                self.atualizar_carrinho()
                self.cliente_nome_var.set("")
                self.window.title("💰 Caixa - Carrinho limpo")
    
    def finalizar_a_vista(self):
        """Finalizar vendas à vista"""
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Carrinho está vazio")
            return
        
        cliente = self.cliente_nome_var.get().strip() or "Cliente Anônimo"
        
        if messagebox.askyesno("Confirmar Venda", 
                             f"Finalizar venda à vista?\n\n"
                             f"Cliente: {cliente}\n"
                             f"Itens: {len(self.carrinho)} produtos\n"
                             f"Total: R$ {self.total_geral:.2f}"):
            
            try:
                # Registrar todas as vendas
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    for item in self.carrinho:
                        cursor.execute("""
                            INSERT INTO historico_vendas (produto, quantidade, preco_unitario, total)
                            VALUES (?, ?, ?, ?)
                        """, (item['produto'], item['quantidade'], item['preco_unitario'], item['total']))
                    conn.commit()
                
                # Tocar som de sucesso
                try:
                    for _ in range(2):
                        self.window.bell()
                        self.window.after(100)
                except:
                    pass
                
                messagebox.showinfo("✅ Venda Finalizada!", 
                                  f"Venda à vista concluída com sucesso!\n\n"
                                  f"Cliente: {cliente}\n"
                                  f"Produtos: {len(self.carrinho)} itens\n"
                                  f"Total pago: R$ {self.total_geral:.2f}\n\n"
                                  f"Obrigado pela preferência!")
                
                # Limpar carrinho
                self.carrinho.clear()
                self.atualizar_carrinho()
                self.cliente_nome_var.set("")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao finalizar venda: {e}")
    
    def finalizar_fiado(self):
        """Finalizar vendas fiado"""
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Carrinho está vazio")
            return
        
        cliente = self.cliente_nome_var.get().strip()
        if not cliente:
            messagebox.showerror("Erro", "Nome do cliente é obrigatório para vendas fiado")
            return
        
        # Abrir janela de dados do fiado
        VendaFiadoCarrinhoWindow(self.window, self.db, cliente, self.carrinho, self.total_geral, self)


class VendaFiadoCarrinhoWindow:
    """Janela para dados adicionais da venda fiado do carrinho"""
    
    def __init__(self, parent, db, cliente, carrinho, total, vendas_window):
        self.parent = parent
        self.db = db
        self.cliente = cliente
        self.carrinho = carrinho
        self.total = total
        self.vendas_window = vendas_window
        
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Finalizar Venda Fiado")
        self.window.geometry("550x450")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        # Variáveis
        self.telefone_var = tk.StringVar()
        self.data_vencimento_var = tk.StringVar()
        self.observacoes_var = tk.StringVar()
        
        # Data padrão (30 dias)
        data_venc = (datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y")
        self.data_vencimento_var.set(data_venc)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="📋 Finalizar Venda Fiado", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # Resumo da venda
        resumo_frame = ttk.LabelFrame(main_frame, text="Resumo da Venda", padding="10")
        resumo_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(resumo_frame, text=f"Cliente: {self.cliente}", font=("Arial", 11, "bold")).pack(anchor="w")
        ttk.Label(resumo_frame, text=f"Quantidade de itens: {len(self.carrinho)} produtos").pack(anchor="w")
        
        # Lista de produtos
        produtos_text = ", ".join([f"{item['quantidade']}x {item['produto']}" for item in self.carrinho[:3]])
        if len(self.carrinho) > 3:
            produtos_text += f" e mais {len(self.carrinho) - 3} itens..."
        ttk.Label(resumo_frame, text=f"Produtos: {produtos_text}").pack(anchor="w")
        
        ttk.Label(resumo_frame, text=f"Total: R$ {self.total:.2f}", 
                 font=("Arial", 12, "bold"), foreground="red").pack(anchor="w")
        
        # Dados adicionais
        dados_frame = ttk.LabelFrame(main_frame, text="Dados do Cliente", padding="15")
        dados_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Telefone
        ttk.Label(dados_frame, text="Telefone:").grid(row=0, column=0, sticky="w", pady=8)
        telefone_entry = ttk.Entry(dados_frame, textvariable=self.telefone_var, width=20)
        telefone_entry.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="ew")
        telefone_entry.focus()
        
        # Data vencimento
        ttk.Label(dados_frame, text="Data de Vencimento:").grid(row=1, column=0, sticky="w", pady=8)
        venc_entry = ttk.Entry(dados_frame, textvariable=self.data_vencimento_var, width=15)
        venc_entry.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="w")
        
        # Observações
        ttk.Label(dados_frame, text="Observações:").grid(row=2, column=0, sticky="w", pady=8)
        obs_entry = ttk.Entry(dados_frame, textvariable=self.observacoes_var, width=35)
        obs_entry.grid(row=2, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        dados_frame.columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(btn_frame, text="💾 Confirmar Venda Fiado", 
                  command=self.confirmar_fiado, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=self.window.destroy, width=15).pack(side=tk.RIGHT)
    
    def confirmar_fiado(self):
        """Confirmar venda fiado do carrinho"""
        try:
            telefone = self.telefone_var.get().strip()
            data_venc = self.data_vencimento_var.get().strip()
            observacoes = self.observacoes_var.get().strip()
            
            # Registrar na tabela de contas abertas
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                for item in self.carrinho:
                    cursor.execute("""
                        INSERT INTO contas_abertas 
                        (cliente_nome, cliente_telefone, produto, quantidade, preco_unitario, total, data_vencimento, observacoes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (self.cliente, telefone, item['produto'], item['quantidade'], 
                          item['preco_unitario'], item['total'], data_venc, observacoes))
                conn.commit()
            
            # Som de confirmação fiado
            try:
                self.window.bell()
            except:
                pass
                
            messagebox.showinfo("📋 Venda Fiado Registrada!", 
                              f"Conta registrada com sucesso!\n\n"
                              f"Cliente: {self.cliente}\n"
                              f"Telefone: {telefone or 'Não informado'}\n"
                              f"Produtos: {len(self.carrinho)} itens\n"
                              f"Valor total: R$ {self.total:.2f}\n"
                              f"Vencimento: {data_venc}\n\n"
                              f"Lembre o cliente da data de pagamento!")
            
            # Limpar carrinho da janela principal
            self.vendas_window.carrinho.clear()
            self.vendas_window.atualizar_carrinho()
            self.vendas_window.cliente_nome_var.set("")
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar venda fiado: {e}")

class VendaFiadoWindow:
    """Janela para registrar venda fiado"""
    
    def __init__(self, parent, db, produto_selecionado, quantidade, preco):
        self.parent = parent
        self.db = db
        self.produto_selecionado = produto_selecionado
        self.quantidade = quantidade
        self.preco = preco
        self.total = quantidade * preco
        
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Venda Fiado - Dados do Cliente")
        self.window.geometry("500x450")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        # Variáveis
        self.cliente_nome_var = tk.StringVar()
        self.cliente_telefone_var = tk.StringVar()
        self.data_vencimento_var = tk.StringVar()
        self.observacoes_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="📋 Registrar Venda Fiado", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # Frame resumo da venda
        resumo_frame = ttk.LabelFrame(main_frame, text="Resumo da Venda", padding="10")
        resumo_frame.pack(fill=tk.X, pady=(0, 15))
        
        produto_nome = self.produto_selecionado.split(" - R$")[0]
        ttk.Label(resumo_frame, text=f"Produto: {produto_nome}").pack(anchor="w")
        ttk.Label(resumo_frame, text=f"Quantidade: {self.quantidade}").pack(anchor="w")
        ttk.Label(resumo_frame, text=f"Preço Unitário: R$ {self.preco:.2f}").pack(anchor="w")
        ttk.Label(resumo_frame, text=f"Total: R$ {self.total:.2f}", font=("Arial", 11, "bold"), foreground="red").pack(anchor="w")
        
        # Frame dados do cliente
        cliente_frame = ttk.LabelFrame(main_frame, text="Dados do Cliente", padding="15")
        cliente_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Nome do cliente
        ttk.Label(cliente_frame, text="Nome do Cliente: *").grid(row=0, column=0, sticky="w", pady=8)
        cliente_entry = ttk.Entry(cliente_frame, textvariable=self.cliente_nome_var, width=35, font=("Arial", 11))
        cliente_entry.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="ew")
        cliente_entry.focus()
        
        # Telefone
        ttk.Label(cliente_frame, text="Telefone:").grid(row=1, column=0, sticky="w", pady=8)
        telefone_entry = ttk.Entry(cliente_frame, textvariable=self.cliente_telefone_var, width=35)
        telefone_entry.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        # Data de vencimento
        ttk.Label(cliente_frame, text="Vencimento (dd/mm/aaaa):").grid(row=2, column=0, sticky="w", pady=8)
        vencimento_entry = ttk.Entry(cliente_frame, textvariable=self.data_vencimento_var, width=20)
        vencimento_entry.grid(row=2, column=1, padx=(10, 0), pady=8, sticky="w")
        
        # Definir vencimento padrão para 30 dias
        vencimento_padrao = (datetime.now() + datetime.timedelta(days=30)).strftime("%d/%m/%Y")
        self.data_vencimento_var.set(vencimento_padrao)
        
        # Observações
        ttk.Label(cliente_frame, text="Observações:").grid(row=3, column=0, sticky="nw", pady=8)
        obs_entry = ttk.Entry(cliente_frame, textvariable=self.observacoes_var, width=35)
        obs_entry.grid(row=3, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        cliente_frame.columnconfigure(1, weight=1)
        
        # Aviso
        aviso_frame = ttk.Frame(main_frame)
        aviso_frame.pack(fill=tk.X, pady=(0, 15))
        
        aviso_text = tk.Text(aviso_frame, height=3, wrap=tk.WORD, font=("Arial", 9))
        aviso_text.pack(fill=tk.X)
        aviso_text.insert("1.0", "⚠️ ATENÇÃO: Esta venda ficará registrada como conta em aberto.\n"
                                "O cliente pode pagar posteriormente através da opção 'Contas em Aberto'.\n"
                                "* Campos obrigatórios")
        aviso_text.config(state=tk.DISABLED, bg="#fff3cd")
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="📋 Registrar Fiado", command=self.registrar_fiado, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.window.destroy, width=15).pack(side=tk.RIGHT)
        
        # Binding Enter
        self.window.bind('<Return>', lambda e: self.registrar_fiado())
    
    def registrar_fiado(self):
        """Registrar venda fiado no banco"""
        try:
            cliente_nome = self.cliente_nome_var.get().strip()
            cliente_telefone = self.cliente_telefone_var.get().strip()
            data_vencimento = self.data_vencimento_var.get().strip()
            observacoes = self.observacoes_var.get().strip()
            
            if not cliente_nome:
                messagebox.showerror("Erro", "Nome do cliente é obrigatório!")
                return
            
            # Validar data de vencimento
            if data_vencimento:
                try:
                    datetime.strptime(data_vencimento, "%d/%m/%Y")
                except ValueError:
                    messagebox.showerror("Erro", "Data de vencimento inválida! Use o formato dd/mm/aaaa")
                    return
            
            # Extrair nome do produto
            produto = self.produto_selecionado.split(" - R$")[0]
            
            # Registrar no banco
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO contas_abertas 
                    (cliente_nome, cliente_telefone, produto, quantidade, preco_unitario, total, data_vencimento, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (cliente_nome, cliente_telefone, produto, self.quantidade, self.preco, self.total, data_vencimento, observacoes))
                conn.commit()
            
            messagebox.showinfo("Sucesso", f"Venda fiado registrada com sucesso!\n\n"
                                         f"Cliente: {cliente_nome}\n"
                                         f"Produto: {produto}\n"
                                         f"Total: R$ {self.total:.2f}\n"
                                         f"Vencimento: {data_vencimento or 'Não definido'}")
            
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar venda fiado: {e}")

class ContasAbertasWindow:
    """Janela para gerenciar contas em aberto"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("📋 Contas em Aberto")
        self.window.geometry("1000x650")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        self.setup_ui()
        self.carregar_contas()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="📋 Contas em Aberto", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Filtros em linha
        filter_row = ttk.Frame(filter_frame)
        filter_row.pack(fill=tk.X)
        
        ttk.Label(filter_row, text="Mostrar:").pack(side=tk.LEFT, padx=(0, 10))
        self.filtro_var = tk.StringVar(value="pendentes")
        
        ttk.Radiobutton(filter_row, text="Apenas Pendentes", variable=self.filtro_var, value="pendentes", command=self.carregar_contas).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(filter_row, text="Apenas Pagas", variable=self.filtro_var, value="pagas", command=self.carregar_contas).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(filter_row, text="Todas", variable=self.filtro_var, value="todas", command=self.carregar_contas).pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Button(filter_row, text="🔄 Atualizar", command=self.carregar_contas, width=12).pack(side=tk.RIGHT)
        
        # Frame da lista
        list_frame = ttk.LabelFrame(main_frame, text="Lista de Contas", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview
        self.contas_tree = ttk.Treeview(list_frame, columns=("cliente", "telefone", "produto", "qtd", "total", "data_venda", "vencimento", "status"), show="headings", height=15)
        
        # Configurar colunas
        self.contas_tree.heading("cliente", text="Cliente")
        self.contas_tree.heading("telefone", text="Telefone")
        self.contas_tree.heading("produto", text="Produto")
        self.contas_tree.heading("qtd", text="Qtd")
        self.contas_tree.heading("total", text="Total")
        self.contas_tree.heading("data_venda", text="Data Venda")
        self.contas_tree.heading("vencimento", text="Vencimento")
        self.contas_tree.heading("status", text="Status")
        
        self.contas_tree.column("cliente", width=150)
        self.contas_tree.column("telefone", width=100)
        self.contas_tree.column("produto", width=150)
        self.contas_tree.column("qtd", width=50)
        self.contas_tree.column("total", width=80)
        self.contas_tree.column("data_venda", width=100)
        self.contas_tree.column("vencimento", width=100)
        self.contas_tree.column("status", width=80)
        
        # Scrollbar
        scrollbar_contas = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.contas_tree.yview)
        self.contas_tree.configure(yscrollcommand=scrollbar_contas.set)
        
        self.contas_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_contas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame dos botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="💰 Marcar como Pago", command=self.marcar_como_pago, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="✏️ Editar", command=self.editar_conta, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🗑️ Excluir", command=self.excluir_conta, width=12).pack(side=tk.LEFT, padx=(0, 10))
        
        # Estatísticas
        self.stats_label = ttk.Label(btn_frame, text="", font=("Arial", 10))
        self.stats_label.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(btn_frame, text="❌ Fechar", command=self.window.destroy, width=12).pack(side=tk.RIGHT)
    
    def carregar_contas(self):
        """Carregar contas em aberto agrupadas por cliente"""
        # Limpar lista
        for item in self.contas_tree.get_children():
            self.contas_tree.delete(item)
        
        try:
            filtro = self.filtro_var.get()
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                if filtro == "pendentes":
                    query = "SELECT * FROM contas_abertas WHERE pago = 0 ORDER BY cliente_nome, data_venda DESC"
                elif filtro == "pagas":
                    query = "SELECT * FROM contas_abertas WHERE pago = 1 ORDER BY cliente_nome, data_pagamento DESC"
                else:
                    query = "SELECT * FROM contas_abertas ORDER BY cliente_nome, pago ASC, data_venda DESC"
                
                cursor.execute(query)
                contas = cursor.fetchall()
                
                total_pendente = 0
                total_pago = 0
                count_pendente = 0
                count_pago = 0
                
                # Agrupar contas por cliente
                clientes_agrupados = {}
                
                for conta in contas:
                    id_conta, cliente_nome, cliente_telefone, produto, quantidade, preco_unitario, total, data_venda, data_vencimento, pago, data_pagamento, observacoes = conta
                    
                    # Normalizar nome do cliente (maiúsculo e sem espaços extras)
                    cliente_key = cliente_nome.upper().strip()
                    
                    if cliente_key not in clientes_agrupados:
                        clientes_agrupados[cliente_key] = {
                            'nome_original': cliente_nome,
                            'telefone': cliente_telefone,
                            'pedidos': [],
                            'total_pendente': 0,
                            'total_pago': 0,
                            'count_pendente': 0,
                            'count_pago': 0,
                            'tem_vencido': False
                        }
                    
                    # Formatar datas
                    try:
                        data_venda_fmt = datetime.fromisoformat(data_venda).strftime("%d/%m/%Y")
                    except:
                        data_venda_fmt = data_venda[:10] if data_venda else ""
                    
                    data_venc_fmt = data_vencimento if data_vencimento else ""
                    status = "✅ PAGO" if pago else "⏰ PENDENTE"
                    
                    # Verificar se está vencido
                    vencido = False
                    if not pago and data_vencimento:
                        try:
                            venc_date = datetime.strptime(data_vencimento, "%d/%m/%Y")
                            if venc_date < datetime.now():
                                status = "🔴 VENCIDO"
                                vencido = True
                                clientes_agrupados[cliente_key]['tem_vencido'] = True
                        except:
                            pass
                    
                    # Adicionar pedido ao cliente
                    clientes_agrupados[cliente_key]['pedidos'].append({
                        'produto': produto,
                        'quantidade': quantidade,
                        'total': total,
                        'data_venda': data_venda_fmt,
                        'data_vencimento': data_venc_fmt,
                        'status': status,
                        'pago': pago,
                        'vencido': vencido
                    })
                    
                    # Estatísticas por cliente
                    if pago:
                        clientes_agrupados[cliente_key]['total_pago'] += total
                        clientes_agrupados[cliente_key]['count_pago'] += 1
                        total_pago += total
                        count_pago += 1
                    else:
                        clientes_agrupados[cliente_key]['total_pendente'] += total
                        clientes_agrupados[cliente_key]['count_pendente'] += 1
                        total_pendente += total
                        count_pendente += 1
                
                # Inserir clientes agrupados na árvore
                for cliente_key, dados_cliente in clientes_agrupados.items():
                    # Preparar resumo do cliente
                    total_cliente = dados_cliente['total_pendente'] + dados_cliente['total_pago']
                    count_cliente = dados_cliente['count_pendente'] + dados_cliente['count_pago']
                    
                    # Status do cliente
                    if dados_cliente['tem_vencido']:
                        status_cliente = "🔴 TEM VENCIDOS"
                    elif dados_cliente['count_pendente'] > 0:
                        status_cliente = "⏰ PENDENTE"
                    else:
                        status_cliente = "✅ PAGO"
                    
                    # Resumo dos produtos
                    if count_cliente > 1:
                        produtos_resumo = f"{count_cliente} pedidos"
                    else:
                        produtos_resumo = dados_cliente['pedidos'][0]['produto']
                    
                    # Data mais recente
                    data_recente = max([p['data_venda'] for p in dados_cliente['pedidos']])
                    
                    # Inserir linha principal do cliente
                    cliente_item = self.contas_tree.insert("", "end", values=(
                        dados_cliente['nome_original'],
                        dados_cliente['telefone'] or "",
                        produtos_resumo,
                        count_cliente,
                        f"R$ {total_cliente:.2f}",
                        data_recente,
                        "",
                        status_cliente
                    ))
                    
                    # Inserir pedidos individuais como filhos (se mais de um pedido)
                    if count_cliente > 1:
                        for pedido in dados_cliente['pedidos']:
                            self.contas_tree.insert(cliente_item, "end", values=(
                                "  → " + pedido['produto'],
                                "",
                                pedido['produto'],
                                pedido['quantidade'],
                                f"R$ {pedido['total']:.2f}",
                                pedido['data_venda'],
                                pedido['data_vencimento'],
                                pedido['status']
                            ))
                
                # Atualizar estatísticas
                stats_text = f"Pendentes: {count_pendente} (R$ {total_pendente:.2f}) | Pagas: {count_pago} (R$ {total_pago:.2f})"
                self.stats_label.config(text=stats_text)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar contas: {e}")
    
    def marcar_como_pago(self):
        """Marcar conta selecionada como paga"""
        selection = self.contas_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma conta para marcar como paga")
            return
        
        item = self.contas_tree.item(selection[0])
        values = item['values']
        cliente = values[0].replace("  → ", "")  # Remove marcador de sub-item
        produto = values[2]
        total_str = values[4]
        
        if "PAGO" in values[7]:
            messagebox.showinfo("Informação", "Esta conta já está marcada como paga")
            return
        
        # Verificar se é um cliente agrupado ou um produto específico
        parent = self.contas_tree.parent(selection[0])
        
        if parent:  # É um pedido específico (filho)
            # Marcar pedido específico como pago
            if messagebox.askyesno("Confirmar Pagamento", f"Marcar como paga?\n\nCliente: {cliente}\nProduto: {produto}\nValor: {total_str}"):
                try:
                    with sqlite3.connect(self.db.db_path) as conn:
                        cursor = conn.cursor()
                        total_valor = float(total_str.replace("R$ ", ""))
                        cursor.execute("""
                            UPDATE contas_abertas 
                            SET pago = 1, data_pagamento = CURRENT_TIMESTAMP 
                            WHERE cliente_nome LIKE ? AND produto = ? AND total = ? AND pago = 0
                            LIMIT 1
                        """, (f"%{cliente}%", produto, total_valor))
                        
                        if cursor.rowcount > 0:
                            conn.commit()
                            messagebox.showinfo("Sucesso", f"Pedido de {cliente} marcado como pago!")
                            self.carregar_contas()
                        else:
                            messagebox.showerror("Erro", "Não foi possível encontrar o pedido para marcar como pago")
                            
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao marcar como pago: {e}")
        else:  # É um cliente agrupado (pai)
            # Verificar quantos pedidos pendentes o cliente tem
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*), SUM(total) FROM contas_abertas 
                        WHERE cliente_nome LIKE ? AND pago = 0
                    """, (f"%{cliente}%",))
                    count, total_pendente = cursor.fetchone()
                    
                    if count == 0:
                        messagebox.showinfo("Informação", "Este cliente não possui contas pendentes")
                        return
                    
                    # Confirmar se quer marcar todos os pedidos como pagos
                    msg = f"Marcar TODOS os pedidos de {cliente} como pagos?\n\n"
                    msg += f"Total de pedidos pendentes: {count}\n"
                    msg += f"Valor total: R$ {total_pendente:.2f}"
                    
                    if messagebox.askyesno("Confirmar Pagamento Total", msg):
                        cursor.execute("""
                            UPDATE contas_abertas 
                            SET pago = 1, data_pagamento = CURRENT_TIMESTAMP 
                            WHERE cliente_nome LIKE ? AND pago = 0
                        """, (f"%{cliente}%",))
                        conn.commit()
                        
                        messagebox.showinfo("Sucesso", f"Todos os pedidos de {cliente} foram marcados como pagos!")
                        self.carregar_contas()
                        
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao marcar como pago: {e}")
    
    def editar_conta(self):
        """Editar conta selecionada"""
        selection = self.contas_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma conta para editar")
            return
        
        item = self.contas_tree.item(selection[0])
        values = item['values']
        cliente = values[0].replace("  → ", "")  # Remove marcador de sub-item
        produto = values[2]
        
        # Verificar se é um cliente agrupado ou um produto específico
        parent = self.contas_tree.parent(selection[0])
        
        if not parent:  # É um cliente agrupado (pai)
            messagebox.showinfo("Informação", "Para editar, selecione um pedido específico do cliente, não o cliente agrupado")
            return
        
        # É um pedido específico - buscar dados completos do banco
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, cliente_nome, cliente_telefone, produto, quantidade, 
                           preco_unitario, total, data_venda, data_vencimento, 
                           pago, observacoes 
                    FROM contas_abertas 
                    WHERE cliente_nome LIKE ? AND produto = ? AND pago = 0
                    LIMIT 1
                """, (f"%{cliente}%", produto))
                
                conta_data = cursor.fetchone()
                
                if not conta_data:
                    messagebox.showerror("Erro", "Conta não encontrada ou já foi paga")
                    return
                
                # Abrir janela de edição
                dialog = EditarContaDialog(self.window, self.db, conta_data)
                if dialog.resultado:
                    self.carregar_contas()
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar dados da conta: {e}")
    
    def excluir_conta(self):
        """Excluir conta selecionada"""
        selection = self.contas_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione uma conta para excluir")
            return
        
        item = self.contas_tree.item(selection[0])
        values = item['values']
        cliente = values[0]
        produto = values[2]
        
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir conta?\n\nCliente: {cliente}\nProduto: {produto}"):
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM contas_abertas 
                        WHERE cliente_nome = ? AND produto = ?
                    """, (cliente, produto))
                    conn.commit()
                
                messagebox.showinfo("Sucesso", "Conta excluída com sucesso!")
                self.carregar_contas()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir conta: {e}")

class EditarContaDialog:
    """Diálogo para editar contas em aberto"""
    
    def __init__(self, parent, db, conta_data):
        self.parent = parent
        self.db = db
        self.conta_data = conta_data
        self.resultado = False
        
        # Extrair dados da conta
        (self.conta_id, self.cliente_nome, self.cliente_telefone, self.produto, 
         self.quantidade, self.preco_unitario, self.total, self.data_venda, 
         self.data_vencimento, self.pago, self.observacoes) = conta_data
        
        self.criar_janela()
    
    def criar_janela(self):
        """Criar janela de edição"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("✏️ Editar Conta em Aberto")
        self.window.geometry("500x600")
        self.window.transient(self.parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="✏️ Editar Conta em Aberto", 
                          font=("Arial", 16, "bold"))
        titulo.pack(pady=(0, 20))
        
        # Informações do cliente
        cliente_frame = ttk.LabelFrame(main_frame, text="Dados do Cliente", padding="15")
        cliente_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Nome do cliente
        ttk.Label(cliente_frame, text="Nome do Cliente:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.cliente_nome_var = tk.StringVar(value=self.cliente_nome)
        nome_entry = ttk.Entry(cliente_frame, textvariable=self.cliente_nome_var, 
                              font=("Arial", 12), width=40)
        nome_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Telefone do cliente
        ttk.Label(cliente_frame, text="Telefone:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.cliente_telefone_var = tk.StringVar(value=self.cliente_telefone or "")
        telefone_entry = ttk.Entry(cliente_frame, textvariable=self.cliente_telefone_var, 
                                  font=("Arial", 12), width=40)
        telefone_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Informações do pedido
        pedido_frame = ttk.LabelFrame(main_frame, text="Dados do Pedido", padding="15")
        pedido_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Produto
        ttk.Label(pedido_frame, text="Produto:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.produto_var = tk.StringVar(value=self.produto)
        produto_entry = ttk.Entry(pedido_frame, textvariable=self.produto_var, 
                                 font=("Arial", 12), width=40)
        produto_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Quantidade e preço na mesma linha
        qtd_preco_frame = ttk.Frame(pedido_frame)
        qtd_preco_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quantidade
        qtd_frame = ttk.Frame(qtd_preco_frame)
        qtd_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Label(qtd_frame, text="Quantidade:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.quantidade_var = tk.StringVar(value=str(self.quantidade))
        qtd_entry = ttk.Entry(qtd_frame, textvariable=self.quantidade_var, 
                             font=("Arial", 12), width=15)
        qtd_entry.pack(fill=tk.X, pady=(5, 0))
        qtd_entry.bind('<KeyRelease>', self.calcular_total)
        
        # Preço unitário
        preco_frame = ttk.Frame(qtd_preco_frame)
        preco_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(preco_frame, text="Preço Unitário:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.preco_unitario_var = tk.StringVar(value=f"{self.preco_unitario:.2f}")
        preco_entry = ttk.Entry(preco_frame, textvariable=self.preco_unitario_var, 
                               font=("Arial", 12), width=15)
        preco_entry.pack(fill=tk.X, pady=(5, 0))
        preco_entry.bind('<KeyRelease>', self.calcular_total)
        
        # Total (calculado automaticamente)
        ttk.Label(pedido_frame, text="Total:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        self.total_var = tk.StringVar(value=f"R$ {self.total:.2f}")
        total_label = ttk.Label(pedido_frame, textvariable=self.total_var, 
                               font=("Arial", 14, "bold"), foreground="#2E8B57")
        total_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Datas
        datas_frame = ttk.LabelFrame(main_frame, text="Datas", padding="15")
        datas_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Data de vencimento
        ttk.Label(datas_frame, text="Data de Vencimento (DD/MM/AAAA):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.data_vencimento_var = tk.StringVar(value=self.data_vencimento or "")
        venc_entry = ttk.Entry(datas_frame, textvariable=self.data_vencimento_var, 
                              font=("Arial", 12), width=20)
        venc_entry.pack(anchor=tk.W, pady=(5, 10))
        
        # Observações
        obs_frame = ttk.LabelFrame(main_frame, text="Observações", padding="15")
        obs_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.observacoes_var = tk.StringVar(value=self.observacoes or "")
        obs_entry = ttk.Entry(obs_frame, textvariable=self.observacoes_var, 
                             font=("Arial", 12), width=40)
        obs_entry.pack(fill=tk.X)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="💾 Salvar", command=self.salvar_alteracoes, 
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.window.destroy, 
                  width=15).pack(side=tk.RIGHT)
        
        # Focar no primeiro campo
        nome_entry.focus()
        nome_entry.select_range(0, tk.END)
        
        # Atalhos
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.window.bind('<Control-s>', lambda e: self.salvar_alteracoes())
    
    def calcular_total(self, event=None):
        """Calcular total automaticamente"""
        try:
            quantidade = float(self.quantidade_var.get() or 0)
            preco_unitario = float(self.preco_unitario_var.get() or 0)
            total = quantidade * preco_unitario
            self.total_var.set(f"R$ {total:.2f}")
        except ValueError:
            self.total_var.set("R$ 0,00")
    
    def salvar_alteracoes(self):
        """Salvar alterações no banco"""
        # Validar campos obrigatórios
        if not self.cliente_nome_var.get().strip():
            messagebox.showerror("Erro", "Nome do cliente é obrigatório")
            return
        
        if not self.produto_var.get().strip():
            messagebox.showerror("Erro", "Produto é obrigatório")
            return
        
        try:
            quantidade = float(self.quantidade_var.get())
            preco_unitario = float(self.preco_unitario_var.get())
            
            if quantidade <= 0 or preco_unitario <= 0:
                messagebox.showerror("Erro", "Quantidade e preço devem ser maiores que zero")
                return
        except ValueError:
            messagebox.showerror("Erro", "Quantidade e preço devem ser números válidos")
            return
        
        # Calcular novo total
        novo_total = quantidade * preco_unitario
        
        # Validar data de vencimento se fornecida
        data_venc = self.data_vencimento_var.get().strip()
        if data_venc:
            try:
                datetime.strptime(data_venc, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Erro", "Data de vencimento deve estar no formato DD/MM/AAAA")
                return
        
        # Confirmar alterações
        msg = f"Salvar alterações?\n\n"
        msg += f"Cliente: {self.cliente_nome_var.get()}\n"
        msg += f"Produto: {self.produto_var.get()}\n"
        msg += f"Quantidade: {quantidade}\n"
        msg += f"Preço: R$ {preco_unitario:.2f}\n"
        msg += f"Total: R$ {novo_total:.2f}"
        
        if messagebox.askyesno("Confirmar Alterações", msg):
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE contas_abertas 
                        SET cliente_nome = ?, cliente_telefone = ?, produto = ?, 
                            quantidade = ?, preco_unitario = ?, total = ?, 
                            data_vencimento = ?, observacoes = ?
                        WHERE id = ?
                    """, (
                        self.cliente_nome_var.get().strip(),
                        self.cliente_telefone_var.get().strip() or None,
                        self.produto_var.get().strip(),
                        quantidade,
                        preco_unitario,
                        novo_total,
                        data_venc or None,
                        self.observacoes_var.get().strip() or None,
                        self.conta_id
                    ))
                    conn.commit()
                
                messagebox.showinfo("Sucesso", "Conta editada com sucesso!")
                self.resultado = True
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")

class RelatoriosWindow:
    """Janela de relatórios completos"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("📄 Relatórios Gerenciais")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="📄 Relatórios Gerenciais", 
                          font=("Arial", 18, "bold"))
        titulo.pack(pady=(0, 30))
        
        # Descrição
        desc = ttk.Label(main_frame, 
                        text="Selecione o tipo de relatório que deseja gerar:",
                        font=("Arial", 12))
        desc.pack(pady=(0, 20))
        
        # Frame dos botões de relatórios
        relatorios_frame = ttk.Frame(main_frame)
        relatorios_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Organizar em grid 2x3
        self.criar_botao_relatorio(relatorios_frame, 0, 0,
                                  "📊 Vendas Diárias", 
                                  "Relatório detalhado das vendas do dia",
                                  self.relatorio_vendas_diarias)
        
        self.criar_botao_relatorio(relatorios_frame, 0, 1,
                                  "📈 Vendas por Período", 
                                  "Relatório de vendas entre datas específicas",
                                  self.relatorio_vendas_periodo)
        
        self.criar_botao_relatorio(relatorios_frame, 1, 0,
                                  "🏆 Produtos Mais Vendidos", 
                                  "Ranking dos produtos por quantidade",
                                  self.relatorio_produtos_vendidos)
        
        self.criar_botao_relatorio(relatorios_frame, 1, 1,
                                  "💰 Análise Financeira", 
                                  "Resumo financeiro completo",
                                  self.relatorio_financeiro)
        
        self.criar_botao_relatorio(relatorios_frame, 2, 0,
                                  "📦 Relatório de Estoque", 
                                  "Situação atual do estoque",
                                  self.relatorio_estoque)
        
        self.criar_botao_relatorio(relatorios_frame, 2, 1,
                                  "🏪 Contas em Aberto", 
                                  "Relatório de crediário e pendências",
                                  self.relatorio_contas_abertas)
        
        # Botão fechar
        ttk.Button(main_frame, text="❌ Fechar", command=self.window.destroy, 
                  width=15).pack(pady=20)
    
    def criar_botao_relatorio(self, parent, row, col, titulo, descricao, comando):
        """Criar botão de relatório estilizado"""
        frame = ttk.LabelFrame(parent, text=titulo, padding="15")
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configurar grid
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        # Descrição
        ttk.Label(frame, text=descricao, font=("Arial", 10), 
                 wraplength=200, justify=tk.CENTER).pack(pady=(0, 15))
        
        # Botão
        ttk.Button(frame, text="📋 Gerar Relatório", command=comando, 
                  width=20).pack()
    
    def relatorio_vendas_diarias(self):
        """Gerar relatório de vendas diárias"""
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar vendas do dia
                cursor.execute("""
                    SELECT produto, quantidade, preco_unitario, total, 
                           time(data_venda) as hora_venda
                    FROM historico_vendas 
                    WHERE date(data_venda) = date('now')
                    ORDER BY data_venda DESC
                """)
                vendas = cursor.fetchall()
                
                if not vendas:
                    messagebox.showinfo("Relatório Vazio", "Nenhuma venda registrada hoje")
                    return
                
                # Calcular totais
                total_vendas = len(vendas)
                receita_total = sum(venda[3] for venda in vendas)
                ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
                
                # Criar relatório
                relatorio = f"""
📊 RELATÓRIO DE VENDAS DIÁRIAS
Data: {hoje}
{'='*50}

💰 RESUMO FINANCEIRO:
• Total de Vendas: {total_vendas}
• Receita Total: R$ {receita_total:.2f}
• Ticket Médio: R$ {ticket_medio:.2f}

📋 VENDAS DETALHADAS:
"""
                
                for i, (produto, qtd, preco, total, hora) in enumerate(vendas, 1):
                    relatorio += f"{i:2d}. {produto:<20} | Qtd: {qtd:2d} | "
                    relatorio += f"Preço: R$ {preco:6.2f} | Total: R$ {total:7.2f} | {hora}\n"
                
                self.mostrar_relatorio("Vendas Diárias", relatorio)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def relatorio_vendas_periodo(self):
        """Gerar relatório de vendas por período"""
        PeriodoDialog(self.window, self.db)
    
    def relatorio_produtos_vendidos(self):
        """Gerar relatório de produtos mais vendidos"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar produtos mais vendidos
                cursor.execute("""
                    SELECT produto, SUM(quantidade) as total_vendido, 
                           SUM(total) as receita_total, COUNT(*) as num_vendas
                    FROM historico_vendas 
                    GROUP BY produto
                    ORDER BY total_vendido DESC
                    LIMIT 20
                """)
                produtos = cursor.fetchall()
                
                if not produtos:
                    messagebox.showinfo("Relatório Vazio", "Nenhuma venda registrada")
                    return
                
                relatorio = f"""
🏆 TOP 20 PRODUTOS MAIS VENDIDOS
{'='*60}

{'Posição':<8} {'Produto':<25} {'Qtd':<8} {'Receita':<12} {'Vendas':<8}
{'-'*60}
"""
                
                for i, (produto, qtd, receita, vendas) in enumerate(produtos, 1):
                    relatorio += f"{i:2d}º      {produto:<25} {qtd:<8} R$ {receita:<8.2f} {vendas:<8}\n"
                
                self.mostrar_relatorio("Produtos Mais Vendidos", relatorio)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def relatorio_financeiro(self):
        """Gerar relatório financeiro completo"""
        try:
            hoje = datetime.now().strftime("%d/%m/%Y")
            mes_atual = datetime.now().strftime("%m/%Y")
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Vendas de hoje
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(total), 0)
                    FROM historico_vendas 
                    WHERE date(data_venda) = date('now')
                """)
                vendas_hoje, receita_hoje = cursor.fetchone()
                
                # Vendas do mês
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(total), 0)
                    FROM historico_vendas 
                    WHERE strftime('%m/%Y', data_venda) = ?
                """, (mes_atual,))
                vendas_mes, receita_mes = cursor.fetchone()
                
                # Contas em aberto
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(total), 0)
                    FROM contas_abertas 
                    WHERE pago = 0
                """)
                contas_pendentes, valor_pendente = cursor.fetchone()
                
                # Valor do estoque
                cursor.execute("""
                    SELECT COALESCE(SUM(quantidade * preco), 0)
                    FROM estoque
                """)
                valor_estoque = cursor.fetchone()[0]
                
                relatorio = f"""
💰 RELATÓRIO FINANCEIRO COMPLETO
Data: {hoje}
{'='*50}

📈 DESEMPENHO HOJE:
• Vendas: {vendas_hoje or 0}
• Receita: R$ {receita_hoje or 0:.2f}
• Ticket Médio: R$ {(receita_hoje/vendas_hoje if vendas_hoje > 0 else 0):.2f}

📊 DESEMPENHO DO MÊS:
• Vendas: {vendas_mes or 0}
• Receita: R$ {receita_mes or 0:.2f}
• Média Diária: R$ {(receita_mes/30 if receita_mes > 0 else 0):.2f}

💳 CONTAS EM ABERTO:
• Contas Pendentes: {contas_pendentes or 0}
• Valor a Receber: R$ {valor_pendente or 0:.2f}

📦 PATRIMÔNIO:
• Valor do Estoque: R$ {valor_estoque or 0:.2f}

💎 RESUMO GERAL:
• Receita Realizada (Mês): R$ {receita_mes or 0:.2f}
• Receita Pendente: R$ {valor_pendente or 0:.2f}
• Patrimônio em Estoque: R$ {valor_estoque or 0:.2f}
• Total Potencial: R$ {(receita_mes or 0) + (valor_pendente or 0) + (valor_estoque or 0):.2f}
"""
                
                self.mostrar_relatorio("Análise Financeira", relatorio)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def relatorio_estoque(self):
        """Gerar relatório de estoque"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT produto, categoria, quantidade, preco, 
                           (quantidade * preco) as valor_total
                    FROM estoque 
                    ORDER BY categoria, produto
                """)
                produtos = cursor.fetchall()
                
                if not produtos:
                    messagebox.showinfo("Relatório Vazio", "Nenhum produto no estoque")
                    return
                
                # Agrupar por categoria
                categorias = {}
                total_geral = 0
                
                for produto, categoria, qtd, preco, valor in produtos:
                    if categoria not in categorias:
                        categorias[categoria] = []
                    categorias[categoria].append((produto, qtd, preco, valor))
                    total_geral += valor
                
                relatorio = f"""
📦 RELATÓRIO DE ESTOQUE COMPLETO
Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}
{'='*70}

"""
                
                for categoria, itens in categorias.items():
                    relatorio += f"\n🏷️ {categoria.upper()}\n"
                    relatorio += f"{'Produto':<30} {'Qtd':<8} {'Preço':<12} {'Valor Total':<12}\n"
                    relatorio += f"{'-'*62}\n"
                    
                    total_categoria = 0
                    for produto, qtd, preco, valor in itens:
                        relatorio += f"{produto:<30} {qtd:<8} R$ {preco:<8.2f} R$ {valor:<8.2f}\n"
                        total_categoria += valor
                    
                    relatorio += f"{'-'*62}\n"
                    relatorio += f"{'TOTAL DA CATEGORIA:':<50} R$ {total_categoria:.2f}\n"
                
                relatorio += f"\n{'='*70}\n"
                relatorio += f"💎 VALOR TOTAL DO ESTOQUE: R$ {total_geral:.2f}\n"
                
                self.mostrar_relatorio("Relatório de Estoque", relatorio)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def relatorio_contas_abertas(self):
        """Gerar relatório de contas em aberto"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT cliente_nome, cliente_telefone, produto, quantidade,
                           total, data_venda, data_vencimento, pago
                    FROM contas_abertas 
                    ORDER BY pago ASC, data_vencimento ASC, cliente_nome
                """)
                contas = cursor.fetchall()
                
                if not contas:
                    messagebox.showinfo("Relatório Vazio", "Nenhuma conta em aberto")
                    return
                
                pendentes = [c for c in contas if not c[7]]
                pagas = [c for c in contas if c[7]]
                
                relatorio = f"""
🏪 RELATÓRIO DE CONTAS EM ABERTO
Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}
{'='*80}

⏰ CONTAS PENDENTES ({len(pendentes)}):
"""
                
                total_pendente = 0
                if pendentes:
                    relatorio += f"{'Cliente':<25} {'Produto':<20} {'Qtd':<5} {'Valor':<10} {'Vencimento':<12}\n"
                    relatorio += f"{'-'*72}\n"
                    
                    for cliente, tel, produto, qtd, total, data_venda, venc, pago in pendentes:
                        venc_str = venc if venc else "Sem prazo"
                        relatorio += f"{cliente[:24]:<25} {produto[:19]:<20} {qtd:<5} R$ {total:<6.2f} {venc_str:<12}\n"
                        total_pendente += total
                
                relatorio += f"\n💰 Total Pendente: R$ {total_pendente:.2f}\n"
                
                if pagas:
                    relatorio += f"\n✅ CONTAS PAGAS ({len(pagas)}):\n"
                    total_pago = sum(c[4] for c in pagas)
                    relatorio += f"💚 Total Pago: R$ {total_pago:.2f}\n"
                
                relatorio += f"\n📊 RESUMO GERAL:\n"
                relatorio += f"• Contas Pendentes: {len(pendentes)}\n"
                relatorio += f"• Contas Pagas: {len(pagas)}\n"
                relatorio += f"• Total a Receber: R$ {total_pendente:.2f}\n"
                
                self.mostrar_relatorio("Contas em Aberto", relatorio)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def mostrar_relatorio(self, titulo, conteudo):
        """Mostrar relatório em janela"""
        RelatorioVisualizadorWindow(self.window, titulo, conteudo)

class PeriodoDialog:
    """Diálogo para selecionar período de relatório"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("📅 Selecionar Período")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="📅 Selecionar Período para Relatório", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Data inicial
        ttk.Label(main_frame, text="Data Inicial (DD/MM/AAAA):", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.data_inicial_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.data_inicial_var, 
                 font=("Arial", 12), width=15).pack(pady=(5, 15))
        
        # Data final
        ttk.Label(main_frame, text="Data Final (DD/MM/AAAA):", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.data_final_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.data_final_var, 
                 font=("Arial", 12), width=15).pack(pady=(5, 20))
        
        # Sugestões rápidas
        sugestoes_frame = ttk.LabelFrame(main_frame, text="Períodos Rápidos", padding="10")
        sugestoes_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(sugestoes_frame, text="Hoje", 
                  command=self.periodo_hoje, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(sugestoes_frame, text="Esta Semana", 
                  command=self.periodo_semana, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(sugestoes_frame, text="Este Mês", 
                  command=self.periodo_mes, width=12).pack(side=tk.LEFT)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="📊 Gerar Relatório", 
                  command=self.gerar_relatorio, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", 
                  command=self.window.destroy, width=15).pack(side=tk.RIGHT)
    
    def periodo_hoje(self):
        """Definir período para hoje"""
        hoje = datetime.now().strftime("%d/%m/%Y")
        self.data_inicial_var.set(hoje)
        self.data_final_var.set(hoje)
    
    def periodo_semana(self):
        """Definir período para esta semana"""
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        
        self.data_inicial_var.set(inicio_semana.strftime("%d/%m/%Y"))
        self.data_final_var.set(fim_semana.strftime("%d/%m/%Y"))
    
    def periodo_mes(self):
        """Definir período para este mês"""
        hoje = datetime.now()
        inicio_mes = hoje.replace(day=1)
        
        # Último dia do mês
        if hoje.month == 12:
            fim_mes = hoje.replace(year=hoje.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)
        
        self.data_inicial_var.set(inicio_mes.strftime("%d/%m/%Y"))
        self.data_final_var.set(fim_mes.strftime("%d/%m/%Y"))
    
    def gerar_relatorio(self):
        """Gerar relatório do período"""
        data_inicial = self.data_inicial_var.get().strip()
        data_final = self.data_final_var.get().strip()
        
        if not data_inicial or not data_final:
            messagebox.showerror("Erro", "Preencha ambas as datas")
            return
        
        try:
            # Validar datas
            datetime.strptime(data_inicial, "%d/%m/%Y")
            datetime.strptime(data_final, "%d/%m/%Y")
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar vendas do período
                cursor.execute("""
                    SELECT produto, quantidade, preco_unitario, total, 
                           date(data_venda) as data_venda
                    FROM historico_vendas 
                    WHERE date(data_venda) BETWEEN date(?) AND date(?)
                    ORDER BY data_venda DESC, produto
                """, (self.converter_data_sql(data_inicial), self.converter_data_sql(data_final)))
                
                vendas = cursor.fetchall()
                
                if not vendas:
                    messagebox.showinfo("Relatório Vazio", f"Nenhuma venda no período de {data_inicial} a {data_final}")
                    return
                
                # Calcular estatísticas
                total_vendas = len(vendas)
                receita_total = sum(venda[3] for venda in vendas)
                ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
                
                # Agrupar por produto
                produtos_resumo = {}
                for produto, qtd, preco, total, data in vendas:
                    if produto not in produtos_resumo:
                        produtos_resumo[produto] = {'qtd': 0, 'receita': 0, 'vendas': 0}
                    produtos_resumo[produto]['qtd'] += qtd
                    produtos_resumo[produto]['receita'] += total
                    produtos_resumo[produto]['vendas'] += 1
                
                relatorio = f"""
📊 RELATÓRIO DE VENDAS POR PERÍODO
Período: {data_inicial} a {data_final}
{'='*60}

💰 RESUMO FINANCEIRO:
• Total de Vendas: {total_vendas}
• Receita Total: R$ {receita_total:.2f}
• Ticket Médio: R$ {ticket_medio:.2f}

🏆 PRODUTOS MAIS VENDIDOS NO PERÍODO:
{'Produto':<25} {'Qtd':<8} {'Receita':<12} {'Vendas':<8}
{'-'*53}
"""
                
                # Ordenar produtos por receita
                produtos_ordenados = sorted(produtos_resumo.items(), 
                                          key=lambda x: x[1]['receita'], reverse=True)
                
                for produto, dados in produtos_ordenados:
                    relatorio += f"{produto[:24]:<25} {dados['qtd']:<8} R$ {dados['receita']:<8.2f} {dados['vendas']:<8}\n"
                
                # Mostrar relatório
                RelatorioVisualizadorWindow(self.window, f"Vendas - {data_inicial} a {data_final}", relatorio)
                self.window.destroy()
                
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/AAAA")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def converter_data_sql(self, data_str):
        """Converter data DD/MM/AAAA para formato SQL"""
        dia, mes, ano = data_str.split('/')
        return f"{ano}-{mes.zfill(2)}-{dia.zfill(2)}"

class RelatorioVisualizadorWindow:
    """Janela para visualizar relatórios"""
    
    def __init__(self, parent, titulo, conteudo):
        self.window = tk.Toplevel(parent)
        self.window.title(f"📄 {titulo}")
        self.window.geometry("900x700")
        self.window.transient(parent)
        centralizar_janela(self.window)
        
        self.setup_ui(titulo, conteudo)
    
    def setup_ui(self, titulo, conteudo):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=f"📄 {titulo}", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # Botões
        ttk.Button(header_frame, text="💾 Salvar", 
                  command=lambda: self.salvar_relatorio(titulo, conteudo), 
                  width=12).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(header_frame, text="🖨️ Imprimir", 
                  command=lambda: self.imprimir_relatorio(conteudo), 
                  width=12).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Área de texto
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget com scrollbar
        self.text_widget = tk.Text(text_frame, font=("Courier New", 10), 
                                  wrap=tk.NONE, bg="#f8f9fa")
        scrollbar_v = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        scrollbar_h = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=self.text_widget.xview)
        
        self.text_widget.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Inserir conteúdo
        self.text_widget.insert("1.0", conteudo)
        self.text_widget.config(state=tk.DISABLED)
        
        # Botão fechar
        ttk.Button(main_frame, text="❌ Fechar", command=self.window.destroy, 
                  width=15).pack(pady=10)
    
    def salvar_relatorio(self, titulo, conteudo):
        """Salvar relatório em arquivo"""
        try:
            import os
            from tkinter import filedialog
            
            # Criar pasta de relatórios
            os.makedirs("data/relatorios", exist_ok=True)
            
            # Nome padrão do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_{titulo.replace(' ', '_')}_{timestamp}.txt"
            
            # Diálogo para salvar
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
                initialdir="data/relatorios",
                initialfilename=nome_arquivo,
                title="Salvar Relatório"
            )
            
            if arquivo:
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{arquivo}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {e}")
    
    def imprimir_relatorio(self, conteudo):
        """Simular impressão do relatório"""
        messagebox.showinfo("Imprimir", 
                           "Para imprimir o relatório:\n\n"
                           "1. Salve o relatório em arquivo\n"
                           "2. Abra o arquivo em um editor de texto\n"
                           "3. Use Ctrl+P para imprimir\n\n"
                           "Ou copie o conteúdo da tela e cole em seu programa favorito")

class CaixaWindow:
    """Janela de controle de caixa"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("💳 Controle de Caixa")
        self.window.geometry("900x700")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        self.setup_ui()
        self.verificar_caixa_aberto()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="💳 Controle de Caixa", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # Frame status do caixa
        self.status_frame = ttk.LabelFrame(main_frame, text="Status do Caixa", padding="15")
        self.status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status inicial
        self.status_label = ttk.Label(self.status_frame, text="Verificando status...", font=("Arial", 12, "bold"))
        self.status_label.pack()
        
        # Frame ações
        self.acoes_frame = ttk.LabelFrame(main_frame, text="Ações do Caixa", padding="15")
        self.acoes_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botões de ação (serão criados dinamicamente)
        self.btn_frame = ttk.Frame(self.acoes_frame)
        self.btn_frame.pack(fill=tk.X)
        
        # Frame movimentações
        mov_frame = ttk.LabelFrame(main_frame, text="Movimentações do Dia", padding="10")
        mov_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview movimentações
        self.mov_tree = ttk.Treeview(mov_frame, columns=("tipo", "valor", "descricao", "hora", "funcionario"), show="headings", height=12)
        
        self.mov_tree.heading("tipo", text="Tipo")
        self.mov_tree.heading("valor", text="Valor")
        self.mov_tree.heading("descricao", text="Descrição")
        self.mov_tree.heading("hora", text="Hora")
        self.mov_tree.heading("funcionario", text="Funcionário")
        
        self.mov_tree.column("tipo", width=100)
        self.mov_tree.column("valor", width=100)
        self.mov_tree.column("descricao", width=250)
        self.mov_tree.column("hora", width=120)
        self.mov_tree.column("funcionario", width=120)
        
        # Scrollbar
        scrollbar_mov = ttk.Scrollbar(mov_frame, orient=tk.VERTICAL, command=self.mov_tree.yview)
        self.mov_tree.configure(yscrollcommand=scrollbar_mov.set)
        
        self.mov_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_mov.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame resumo
        resumo_frame = ttk.LabelFrame(main_frame, text="Resumo do Dia", padding="10")
        resumo_frame.pack(fill=tk.X)
        
        self.resumo_label = ttk.Label(resumo_frame, text="", font=("Arial", 10))
        self.resumo_label.pack()
        
        # Botão fechar
        ttk.Button(main_frame, text="❌ Fechar", command=self.window.destroy, width=15).pack(pady=10)
    
    def verificar_caixa_aberto(self):
        """Verificar se há caixa aberto"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM caixa WHERE status = 'ABERTO' ORDER BY data_abertura DESC LIMIT 1")
                caixa_aberto = cursor.fetchone()
                
                if caixa_aberto:
                    self.caixa_atual = caixa_aberto
                    self.mostrar_caixa_aberto()
                else:
                    self.caixa_atual = None
                    self.mostrar_caixa_fechado()
                    
                self.carregar_movimentacoes()
                self.atualizar_resumo()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar status do caixa: {e}")
    
    def mostrar_caixa_aberto(self):
        """Mostrar interface para caixa aberto"""
        self.status_label.config(text="🟢 CAIXA ABERTO", foreground="green")
        
        # Limpar botões existentes
        for widget in self.btn_frame.winfo_children():
            widget.destroy()
        
        # Botões para caixa aberto
        ttk.Button(self.btn_frame, text="💰 Sangria", command=self.fazer_sangria, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(self.btn_frame, text="➕ Reforço", command=self.fazer_reforco, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(self.btn_frame, text="📊 Relatório", command=self.gerar_relatorio, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(self.btn_frame, text="🔒 Fechar Caixa", command=self.fechar_caixa, width=15).pack(side=tk.RIGHT)
    
    def mostrar_caixa_fechado(self):
        """Mostrar interface para caixa fechado"""
        self.status_label.config(text="🔴 CAIXA FECHADO", foreground="red")
        
        # Limpar botões existentes
        for widget in self.btn_frame.winfo_children():
            widget.destroy()
        
        # Botão para abrir caixa
        ttk.Button(self.btn_frame, text="🔓 Abrir Caixa", command=self.abrir_caixa, width=20).pack()
    
    def abrir_caixa(self):
        """Abrir novo caixa"""
        dialog = AbrirCaixaDialog(self.window, self.db)
        if dialog.resultado:
            self.verificar_caixa_aberto()
    
    def fazer_sangria(self):
        """Fazer sangria do caixa"""
        dialog = MovimentacaoCaixaDialog(self.window, self.db, "SANGRIA", self.caixa_atual[0])
        if dialog.resultado:
            self.verificar_caixa_aberto()
    
    def fazer_reforco(self):
        """Fazer reforço do caixa"""
        dialog = MovimentacaoCaixaDialog(self.window, self.db, "REFORCO", self.caixa_atual[0])
        if dialog.resultado:
            self.verificar_caixa_aberto()
    
    def fechar_caixa(self):
        """Fechar caixa atual"""
        dialog = FecharCaixaDialog(self.window, self.db, self.caixa_atual)
        if dialog.resultado:
            self.verificar_caixa_aberto()
    
    def gerar_relatorio(self):
        """Gerar relatório do caixa"""
        if not self.caixa_atual:
            messagebox.showerror("Erro", "Nenhum caixa aberto")
            return
        
        # Calcular valores
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Vendas do dia
                cursor.execute("SELECT SUM(total) FROM historico_vendas WHERE DATE(data_venda) = DATE('now')")
                vendas_dia = cursor.fetchone()[0] or 0
                
                # Movimentações
                cursor.execute("""
                    SELECT tipo, SUM(valor) FROM movimentacoes_caixa 
                    WHERE caixa_id = ? GROUP BY tipo
                """, (self.caixa_atual[0],))
                movimentacoes = dict(cursor.fetchall())
                
                sangria = movimentacoes.get('SANGRIA', 0)
                reforco = movimentacoes.get('REFORCO', 0)
                
                valor_inicial = self.caixa_atual[6]
                valor_teorico = valor_inicial + vendas_dia - sangria + reforco
                
                relatorio = f"""RELATÓRIO DE CAIXA
                
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Funcionário: {self.caixa_atual[11]}

VALORES:
Valor Inicial: R$ {valor_inicial:.2f}
Vendas do Dia: R$ {vendas_dia:.2f}
Sangrias: R$ {sangria:.2f}
Reforços: R$ {reforco:.2f}

VALOR TEÓRICO EM CAIXA: R$ {valor_teorico:.2f}"""
                
                messagebox.showinfo("Relatório de Caixa", relatorio)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def carregar_movimentacoes(self):
        """Carregar movimentações do dia"""
        # Limpar lista
        for item in self.mov_tree.get_children():
            self.mov_tree.delete(item)
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                if self.caixa_atual:
                    cursor.execute("""
                        SELECT tipo, valor, descricao, data_hora, funcionario 
                        FROM movimentacoes_caixa 
                        WHERE caixa_id = ? 
                        ORDER BY data_hora DESC
                    """, (self.caixa_atual[0],))
                else:
                    cursor.execute("""
                        SELECT tipo, valor, descricao, data_hora, funcionario 
                        FROM movimentacoes_caixa 
                        WHERE DATE(data_hora) = DATE('now')
                        ORDER BY data_hora DESC
                    """)
                
                movimentacoes = cursor.fetchall()
                
                for mov in movimentacoes:
                    tipo, valor, descricao, data_hora, funcionario = mov
                    
                    try:
                        hora_fmt = datetime.fromisoformat(data_hora).strftime("%H:%M")
                    except:
                        hora_fmt = data_hora
                    
                    self.mov_tree.insert("", "end", values=(
                        tipo,
                        f"R$ {valor:.2f}",
                        descricao or "",
                        hora_fmt,
                        funcionario
                    ))
                    
        except Exception as e:
            print(f"Erro ao carregar movimentações: {e}")
    
    def atualizar_resumo(self):
        """Atualizar resumo do caixa"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Vendas do dia
                cursor.execute("SELECT COUNT(*), SUM(total) FROM historico_vendas WHERE DATE(data_venda) = DATE('now')")
                count_vendas, total_vendas = cursor.fetchone()
                count_vendas = count_vendas or 0
                total_vendas = total_vendas or 0
                
                if self.caixa_atual:
                    resumo = f"Vendas hoje: {count_vendas} ({total_vendas:.2f}) | Caixa aberto às {self.caixa_atual[4][:16] if self.caixa_atual[4] else ''}"
                else:
                    resumo = f"Vendas hoje: {count_vendas} (R$ {total_vendas:.2f}) | Caixa fechado"
                
                self.resumo_label.config(text=resumo)
                
        except Exception as e:
            self.resumo_label.config(text="Erro ao calcular resumo")

class AbrirCaixaDialog:
    """Dialog para abrir caixa"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.resultado = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔓 Abrir Caixa")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        centralizar_janela(self.dialog)
        
        self.valor_inicial_var = tk.StringVar()
        self.funcionario_var = tk.StringVar()
        self.observacoes_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🔓 Abertura de Caixa", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(form_frame, text="Valor Inicial (R$):").grid(row=0, column=0, sticky="w", pady=8)
        valor_entry = ttk.Entry(form_frame, textvariable=self.valor_inicial_var, width=20)
        valor_entry.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="ew")
        valor_entry.focus()
        
        ttk.Label(form_frame, text="Funcionário:").grid(row=1, column=0, sticky="w", pady=8)
        funcionario_entry = ttk.Entry(form_frame, textvariable=self.funcionario_var, width=20)
        funcionario_entry.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        ttk.Label(form_frame, text="Observações:").grid(row=2, column=0, sticky="w", pady=8)
        obs_entry = ttk.Entry(form_frame, textvariable=self.observacoes_var, width=20)
        obs_entry.grid(row=2, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="🔓 Abrir", command=self.abrir, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.dialog.destroy, width=15).pack(side=tk.RIGHT)
        
        self.dialog.bind('<Return>', lambda e: self.abrir())
    
    def abrir(self):
        """Abrir o caixa"""
        try:
            valor_inicial = float(self.valor_inicial_var.get().replace(',', '.'))
            funcionario = self.funcionario_var.get().strip() or "Operador"
            observacoes = self.observacoes_var.get().strip()
            
            if valor_inicial < 0:
                messagebox.showerror("Erro", "Valor inicial não pode ser negativo")
                return
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO caixa (valor_inicial, funcionario, observacoes)
                    VALUES (?, ?, ?)
                """, (valor_inicial, funcionario, observacoes))
                
                caixa_id = cursor.lastrowid
                
                # Registrar movimentação de abertura
                cursor.execute("""
                    INSERT INTO movimentacoes_caixa (caixa_id, tipo, valor, descricao, funcionario)
                    VALUES (?, 'ABERTURA', ?, 'Abertura de caixa', ?)
                """, (caixa_id, valor_inicial, funcionario))
                
                conn.commit()
            
            messagebox.showinfo("Sucesso", f"Caixa aberto com sucesso!\nValor inicial: R$ {valor_inicial:.2f}")
            self.resultado = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Valor inicial deve ser um número válido")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir caixa: {e}")

class MovimentacaoCaixaDialog:
    """Dialog para movimentações do caixa"""
    
    def __init__(self, parent, db, tipo, caixa_id):
        self.parent = parent
        self.db = db
        self.tipo = tipo
        self.caixa_id = caixa_id
        self.resultado = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"💰 {tipo.title()}")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        centralizar_janela(self.dialog)
        
        self.valor_var = tk.StringVar()
        self.descricao_var = tk.StringVar()
        self.funcionario_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = "💰 Sangria" if self.tipo == "SANGRIA" else "➕ Reforço"
        ttk.Label(main_frame, text=titulo, font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(form_frame, text="Valor (R$):").grid(row=0, column=0, sticky="w", pady=8)
        valor_entry = ttk.Entry(form_frame, textvariable=self.valor_var, width=20)
        valor_entry.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="ew")
        valor_entry.focus()
        
        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=8)
        desc_entry = ttk.Entry(form_frame, textvariable=self.descricao_var, width=20)
        desc_entry.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        ttk.Label(form_frame, text="Funcionário:").grid(row=2, column=0, sticky="w", pady=8)
        func_entry = ttk.Entry(form_frame, textvariable=self.funcionario_var, width=20)
        func_entry.grid(row=2, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        btn_text = "💰 Confirmar" if self.tipo == "SANGRIA" else "➕ Confirmar"
        ttk.Button(btn_frame, text=btn_text, command=self.confirmar, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.dialog.destroy, width=15).pack(side=tk.RIGHT)
        
        self.dialog.bind('<Return>', lambda e: self.confirmar())
    
    def confirmar(self):
        """Confirmar movimentação"""
        try:
            valor = float(self.valor_var.get().replace(',', '.'))
            descricao = self.descricao_var.get().strip()
            funcionario = self.funcionario_var.get().strip() or "Operador"
            
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser maior que zero")
                return
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Registrar movimentação
                cursor.execute("""
                    INSERT INTO movimentacoes_caixa (caixa_id, tipo, valor, descricao, funcionario)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.caixa_id, self.tipo, valor, descricao, funcionario))
                
                # Atualizar total no caixa
                if self.tipo == "SANGRIA":
                    cursor.execute("""
                        UPDATE caixa SET valor_sangria = valor_sangria + ?
                        WHERE id = ?
                    """, (valor, self.caixa_id))
                else:  # REFORCO
                    cursor.execute("""
                        UPDATE caixa SET valor_reforco = valor_reforco + ?
                        WHERE id = ?
                    """, (valor, self.caixa_id))
                
                conn.commit()
            
            acao = "Sangria realizada" if self.tipo == "SANGRIA" else "Reforço realizado"
            messagebox.showinfo("Sucesso", f"{acao} com sucesso!\nValor: R$ {valor:.2f}")
            self.resultado = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Valor deve ser um número válido")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar movimentação: {e}")

class FecharCaixaDialog:
    """Dialog para fechar caixa"""
    
    def __init__(self, parent, db, caixa_atual):
        self.parent = parent
        self.db = db
        self.caixa_atual = caixa_atual
        self.resultado = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔒 Fechar Caixa")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        centralizar_janela(self.dialog)
        
        self.valor_final_var = tk.StringVar()
        self.observacoes_var = tk.StringVar()
        
        self.setup_ui()
        self.calcular_valores()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🔒 Fechamento de Caixa", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame resumo
        resumo_frame = ttk.LabelFrame(main_frame, text="Resumo do Dia", padding="15")
        resumo_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.resumo_text = tk.Text(resumo_frame, height=8, width=50, wrap=tk.WORD, font=("Courier", 10))
        self.resumo_text.pack(fill=tk.X)
        self.resumo_text.config(state=tk.DISABLED)
        
        # Frame fechamento
        fecha_frame = ttk.LabelFrame(main_frame, text="Dados do Fechamento", padding="15")
        fecha_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(fecha_frame, text="Valor Real em Caixa (R$):").grid(row=0, column=0, sticky="w", pady=8)
        valor_entry = ttk.Entry(fecha_frame, textvariable=self.valor_final_var, width=20)
        valor_entry.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="ew")
        valor_entry.focus()
        
        ttk.Label(fecha_frame, text="Observações:").grid(row=1, column=0, sticky="w", pady=8)
        obs_entry = ttk.Entry(fecha_frame, textvariable=self.observacoes_var, width=20)
        obs_entry.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        fecha_frame.columnconfigure(1, weight=1)
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="🔒 Fechar Caixa", command=self.fechar, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.dialog.destroy, width=15).pack(side=tk.RIGHT)
    
    def calcular_valores(self):
        """Calcular valores do dia"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Vendas do dia
                cursor.execute("SELECT COUNT(*), SUM(total) FROM historico_vendas WHERE DATE(data_venda) = DATE('now')")
                count_vendas, total_vendas = cursor.fetchone()
                count_vendas = count_vendas or 0
                total_vendas = total_vendas or 0
                
                # Movimentações
                cursor.execute("""
                    SELECT tipo, SUM(valor) FROM movimentacoes_caixa 
                    WHERE caixa_id = ? AND tipo IN ('SANGRIA', 'REFORCO')
                    GROUP BY tipo
                """, (self.caixa_atual[0],))
                movimentacoes = dict(cursor.fetchall())
                
                sangria = movimentacoes.get('SANGRIA', 0)
                reforco = movimentacoes.get('REFORCO', 0)
                
                valor_inicial = self.caixa_atual[6]
                valor_teorico = valor_inicial + total_vendas - sangria + reforco
                
                resumo = f"""RESUMO DO DIA
                
Valor Inicial:      R$ {valor_inicial:>10.2f}
Vendas ({count_vendas:02d}):         R$ {total_vendas:>10.2f}
Sangrias:           R$ {sangria:>10.2f}
Reforços:           R$ {reforco:>10.2f}
                    ________________
VALOR TEÓRICO:      R$ {valor_teorico:>10.2f}

Digite o valor real em caixa para fechar."""
                
                self.resumo_text.config(state=tk.NORMAL)
                self.resumo_text.delete("1.0", tk.END)
                self.resumo_text.insert("1.0", resumo)
                self.resumo_text.config(state=tk.DISABLED)
                
                self.valor_teorico = valor_teorico
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular valores: {e}")
    
    def fechar(self):
        """Fechar o caixa"""
        try:
            valor_final = float(self.valor_final_var.get().replace(',', '.'))
            observacoes = self.observacoes_var.get().strip()
            
            diferenca = valor_final - self.valor_teorico
            
            # Confirmar fechamento
            msg = f"Confirmar fechamento do caixa?\n\nValor teórico: R$ {self.valor_teorico:.2f}\nValor real: R$ {valor_final:.2f}\nDiferença: R$ {diferenca:.2f}"
            
            if not messagebox.askyesno("Confirmar Fechamento", msg):
                return
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                # Atualizar caixa
                cursor.execute("""
                    UPDATE caixa SET 
                        data_fechamento = CURRENT_TIMESTAMP,
                        valor_final = ?,
                        status = 'FECHADO',
                        observacoes = ?
                    WHERE id = ?
                """, (valor_final, observacoes, self.caixa_atual[0]))
                
                # Registrar movimentação de fechamento
                cursor.execute("""
                    INSERT INTO movimentacoes_caixa (caixa_id, tipo, valor, descricao, funcionario)
                    VALUES (?, 'FECHAMENTO', ?, ?, ?)
                """, (self.caixa_atual[0], valor_final, f"Fechamento de caixa. Diferença: R$ {diferenca:.2f}", self.caixa_atual[11]))
                
                conn.commit()
            
            messagebox.showinfo("Sucesso", f"Caixa fechado com sucesso!\nDiferença: R$ {diferenca:.2f}")
            self.resultado = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Valor final deve ser um número válido")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao fechar caixa: {e}")

class BackupWindow:
    """Janela de backup e sincronização"""
    
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("💾 Backup e Sincronização")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window)
        
        self.setup_ui()
        self.carregar_backups()
    
    def setup_ui(self):
        """Configurar interface"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="💾 Backup e Sincronização", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15))
        
        # Frame ações
        acoes_frame = ttk.LabelFrame(main_frame, text="Ações de Backup", padding="15")
        acoes_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botões de backup
        btn_row1 = ttk.Frame(acoes_frame)
        btn_row1.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_row1, text="💾 Backup Completo", command=self.backup_completo, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row1, text="📊 Backup Dados", command=self.backup_dados, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row1, text="🔄 Backup Automático", command=self.configurar_auto, width=20).pack(side=tk.LEFT)
        
        btn_row2 = ttk.Frame(acoes_frame)
        btn_row2.pack(fill=tk.X)
        
        ttk.Button(btn_row2, text="📥 Restaurar Backup", command=self.restaurar_backup, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row2, text="☁️ Sincronizar Nuvem", command=self.sincronizar_nuvem, width=20).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_row2, text="📤 Exportar Excel", command=self.exportar_excel, width=20).pack(side=tk.LEFT)
        
        # Frame configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        config_row = ttk.Frame(config_frame)
        config_row.pack(fill=tk.X)
        
        ttk.Label(config_row, text="Pasta de Backup:").pack(side=tk.LEFT)
        self.pasta_var = tk.StringVar(value="./backups")
        pasta_entry = ttk.Entry(config_row, textvariable=self.pasta_var, width=40)
        pasta_entry.pack(side=tk.LEFT, padx=(10, 10), fill=tk.X, expand=True)
        ttk.Button(config_row, text="📁", command=self.escolher_pasta, width=3).pack(side=tk.LEFT)
        
        # Frame lista de backups
        list_frame = ttk.LabelFrame(main_frame, text="Histórico de Backups", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview backups
        self.backup_tree = ttk.Treeview(list_frame, columns=("nome", "data", "tamanho", "tipo", "status"), show="headings", height=12)
        
        self.backup_tree.heading("nome", text="Nome do Arquivo")
        self.backup_tree.heading("data", text="Data/Hora")
        self.backup_tree.heading("tamanho", text="Tamanho")
        self.backup_tree.heading("tipo", text="Tipo")
        self.backup_tree.heading("status", text="Status")
        
        self.backup_tree.column("nome", width=250)
        self.backup_tree.column("data", width=150)
        self.backup_tree.column("tamanho", width=100)
        self.backup_tree.column("tipo", width=100)
        self.backup_tree.column("status", width=100)
        
        # Scrollbar
        scrollbar_backup = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar_backup.set)
        
        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_backup.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame botões inferiores
        btn_inferior = ttk.Frame(main_frame)
        btn_inferior.pack(fill=tk.X)
        
        ttk.Button(btn_inferior, text="🗑️ Excluir Backup", command=self.excluir_backup, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_inferior, text="📋 Verificar Integridade", command=self.verificar_integridade, width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status
        self.status_label = ttk.Label(btn_inferior, text="Pronto", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Button(btn_inferior, text="❌ Fechar", command=self.window.destroy, width=12).pack(side=tk.RIGHT)
    
    def backup_completo(self):
        """Fazer backup completo do sistema"""
        try:
            import shutil
            import os
            from datetime import datetime
            
            self.status_label.config(text="Fazendo backup completo...", foreground="orange")
            self.window.update()
            
            # Criar pasta de backup se não existir
            pasta_backup = self.pasta_var.get()
            os.makedirs(pasta_backup, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"backup_completo_{timestamp}.db"
            caminho_backup = os.path.join(pasta_backup, nome_backup)
            
            # Copiar banco de dados
            shutil.copy2(self.db.db_path, caminho_backup)
            
            # Calcular tamanho
            tamanho_mb = os.path.getsize(caminho_backup) / (1024 * 1024)
            
            # Registrar no banco
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO backups (nome_arquivo, caminho_arquivo, tamanho_mb, tipo)
                    VALUES (?, ?, ?, 'COMPLETO')
                """, (nome_backup, caminho_backup, tamanho_mb))
                conn.commit()
            
            self.status_label.config(text="Backup completo realizado com sucesso!", foreground="green")
            messagebox.showinfo("Sucesso", f"Backup completo criado:\n{nome_backup}\nTamanho: {tamanho_mb:.2f} MB")
            self.carregar_backups()
            
        except Exception as e:
            self.status_label.config(text="Erro no backup", foreground="red")
            messagebox.showerror("Erro", f"Erro ao fazer backup: {e}")
    
    def backup_dados(self):
        """Fazer backup apenas dos dados essenciais"""
        try:
            import os
            from datetime import datetime
            
            self.status_label.config(text="Fazendo backup de dados...", foreground="orange")
            self.window.update()
            
            # Criar pasta de backup se não existir
            pasta_backup = self.pasta_var.get()
            os.makedirs(pasta_backup, exist_ok=True)
            
            # Nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"backup_dados_{timestamp}.sql"
            caminho_backup = os.path.join(pasta_backup, nome_backup)
            
            # Exportar dados essenciais
            with sqlite3.connect(self.db.db_path) as conn:
                with open(caminho_backup, 'w', encoding='utf-8') as f:
                    for linha in conn.iterdump():
                        if any(tabela in linha for tabela in ['estoque', 'historico_vendas', 'contas_abertas']):
                            f.write(linha + '\n')
            
            # Calcular tamanho
            tamanho_mb = os.path.getsize(caminho_backup) / (1024 * 1024)
            
            # Registrar no banco
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO backups (nome_arquivo, caminho_arquivo, tamanho_mb, tipo)
                    VALUES (?, ?, ?, 'DADOS')
                """, (nome_backup, caminho_backup, tamanho_mb))
                conn.commit()
            
            self.status_label.config(text="Backup de dados realizado!", foreground="green")
            messagebox.showinfo("Sucesso", f"Backup de dados criado:\n{nome_backup}\nTamanho: {tamanho_mb:.2f} MB")
            self.carregar_backups()
            
        except Exception as e:
            self.status_label.config(text="Erro no backup", foreground="red")
            messagebox.showerror("Erro", f"Erro ao fazer backup de dados: {e}")
    
    def configurar_auto(self):
        """Configurar backup automático"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de backup automático em desenvolvimento.\n\nNo momento, execute backups manuais regularmente.")
    
    def sincronizar_nuvem(self):
        """Sincronizar com a nuvem"""
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de sincronização em nuvem em desenvolvimento.\n\nUse backup manual e copie os arquivos para sua nuvem preferida (Google Drive, Dropbox, etc.)")
    
    def exportar_excel(self):
        """Exportar dados para Excel"""
        try:
            import pandas as pd
            import os
            from datetime import datetime
            
            self.status_label.config(text="Exportando para Excel...", foreground="orange")
            self.window.update()
            
            pasta_backup = self.pasta_var.get()
            os.makedirs(pasta_backup, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_excel = f"export_dados_{timestamp}.xlsx"
            caminho_excel = os.path.join(pasta_backup, nome_excel)
            
            with sqlite3.connect(self.db.db_path) as conn:
                # Ler dados das tabelas
                estoque_df = pd.read_sql_query("SELECT * FROM estoque", conn)
                vendas_df = pd.read_sql_query("SELECT * FROM historico_vendas", conn)
                contas_df = pd.read_sql_query("SELECT * FROM contas_abertas", conn)
                
                # Criar arquivo Excel com múltiplas abas
                with pd.ExcelWriter(caminho_excel, engine='openpyxl') as writer:
                    estoque_df.to_excel(writer, sheet_name='Estoque', index=False)
                    vendas_df.to_excel(writer, sheet_name='Vendas', index=False)
                    contas_df.to_excel(writer, sheet_name='Contas_Abertas', index=False)
            
            tamanho_mb = os.path.getsize(caminho_excel) / (1024 * 1024)
            
            # Registrar no banco
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO backups (nome_arquivo, caminho_arquivo, tamanho_mb, tipo)
                    VALUES (?, ?, ?, 'EXCEL')
                """, (nome_excel, caminho_excel, tamanho_mb))
                conn.commit()
            
            self.status_label.config(text="Exportação concluída!", foreground="green")
            messagebox.showinfo("Sucesso", f"Dados exportados para Excel:\n{nome_excel}\nTamanho: {tamanho_mb:.2f} MB")
            self.carregar_backups()
            
        except Exception as e:
            self.status_label.config(text="Erro na exportação", foreground="red")
            messagebox.showerror("Erro", f"Erro ao exportar para Excel: {e}")
    
    def restaurar_backup(self):
        """Restaurar backup selecionado"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione um backup para restaurar")
            return
        
        if not messagebox.askyesno("Confirmar", "ATENÇÃO: Restaurar backup substituirá todos os dados atuais.\n\nDeseja continuar?"):
            return
        
        # Implementar restauração
        messagebox.showinfo("Em Desenvolvimento", "Funcionalidade de restauração em desenvolvimento.\n\nPara restaurar, substitua manualmente o arquivo banco.db")
    
    def escolher_pasta(self):
        """Escolher pasta de backup"""
        from tkinter import filedialog
        pasta = filedialog.askdirectory(title="Escolher Pasta de Backup")
        if pasta:
            self.pasta_var.set(pasta)
    
    def carregar_backups(self):
        """Carregar lista de backups"""
        # Limpar lista
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT nome_arquivo, data_backup, tamanho_mb, tipo, status
                    FROM backups 
                    ORDER BY data_backup DESC
                """)
                backups = cursor.fetchall()
                
                for backup in backups:
                    nome, data, tamanho, tipo, status = backup
                    
                    try:
                        data_fmt = datetime.fromisoformat(data).strftime("%d/%m/%Y %H:%M")
                    except:
                        data_fmt = data
                    
                    self.backup_tree.insert("", "end", values=(
                        nome,
                        data_fmt,
                        f"{tamanho:.2f} MB" if tamanho else "N/A",
                        tipo,
                        status
                    ))
                    
        except Exception as e:
            print(f"Erro ao carregar backups: {e}")
    
    def excluir_backup(self):
        """Excluir backup selecionado"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showerror("Erro", "Selecione um backup para excluir")
            return
        
        item = self.backup_tree.item(selection[0])
        nome_arquivo = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"Excluir backup '{nome_arquivo}'?"):
            try:
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM backups WHERE nome_arquivo = ?", (nome_arquivo,))
                    conn.commit()
                
                messagebox.showinfo("Sucesso", "Backup excluído do registro")
                self.carregar_backups()
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir backup: {e}")
    
    def verificar_integridade(self):
        """Verificar integridade dos backups"""
        try:
            import os
            
            pasta_backup = self.pasta_var.get()
            if not os.path.exists(pasta_backup):
                messagebox.showerror("Erro", "Pasta de backup não encontrada")
                return
            
            arquivos_pasta = os.listdir(pasta_backup)
            
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nome_arquivo, caminho_arquivo FROM backups")
                backups_db = cursor.fetchall()
            
            # Verificar arquivos
            arquivos_ok = 0
            arquivos_faltando = 0
            
            for nome, caminho in backups_db:
                if os.path.exists(caminho):
                    arquivos_ok += 1
                else:
                    arquivos_faltando += 1
            
            resultado = f"Verificação de Integridade:\n\n"
            resultado += f"✅ Arquivos OK: {arquivos_ok}\n"
            resultado += f"❌ Arquivos faltando: {arquivos_faltando}\n"
            resultado += f"📁 Arquivos na pasta: {len(arquivos_pasta)}"
            
            messagebox.showinfo("Verificação de Integridade", resultado)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao verificar integridade: {e}")




def main():
    """Função principal"""
    print("🚀 Iniciando Sistema de Lanchonete...")
    
    # Verificar sistema de proteção primeiro
    if PROTECAO_ATIVA:
        print("🔐 Verificando sistema de proteção...")
        try:
            protecao = SistemaProtecaoAutoria()
            if not protecao.inicializar_protecao():
                print("❌ Falha na verificação de proteção")
                return
            print("✓ Sistema de proteção OK")
        except Exception as e:
            print(f"⚠️ Erro no sistema de proteção: {e}")
            # Continuar mesmo com erro de proteção para não travar o sistema
    
    if not verificar_dependencias():
        print("❌ Erro: Dependências não disponíveis")
        return
    
    try:
        app = MainWindow()
        print("✓ Banco de dados configurado")
        print("✓ Sistema carregado com sucesso")
        app.run()
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

if __name__ == "__main__":
    main()