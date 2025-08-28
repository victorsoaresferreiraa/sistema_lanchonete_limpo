#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE SIMPLES DO CADASTRO DE PRODUTO
=====================================
Teste isolado da funcionalidade de cadastro
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class TesteCadastroSimples:
    def __init__(self):
        # Criar banco temporário
        self.db_path = "data/teste_banco.db"
        os.makedirs("data", exist_ok=True)
        self.criar_tabela()
        
        # Interface
        self.root = tk.Tk()
        self.root.title("🧪 Teste Cadastro Produto")
        self.root.geometry("400x300")
        
        # Variáveis
        self.produto_var = tk.StringVar()
        self.quantidade_var = tk.StringVar()
        self.preco_var = tk.StringVar()
        
        self.setup_ui()
    
    def criar_tabela(self):
        """Criar tabela de teste"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estoque (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    produto TEXT NOT NULL,
                    categoria TEXT DEFAULT 'Outros',
                    quantidade INTEGER DEFAULT 0,
                    preco REAL DEFAULT 0.0,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def setup_ui(self):
        """Interface simples"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="🧪 TESTE DE CADASTRO", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Campos
        ttk.Label(main_frame, text="Nome do Produto:").pack(anchor="w")
        produto_entry = ttk.Entry(main_frame, textvariable=self.produto_var, width=30)
        produto_entry.pack(pady=(5, 10), fill="x")
        produto_entry.focus()
        
        ttk.Label(main_frame, text="Quantidade:").pack(anchor="w")
        quantidade_entry = ttk.Entry(main_frame, textvariable=self.quantidade_var, width=30)
        quantidade_entry.pack(pady=(5, 10), fill="x")
        
        ttk.Label(main_frame, text="Preço:").pack(anchor="w")
        preco_entry = ttk.Entry(main_frame, textvariable=self.preco_var, width=30)
        preco_entry.pack(pady=(5, 20), fill="x")
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="💾 Salvar", command=self.salvar_produto).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="🧪 Teste Debug", command=self.teste_debug).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Sair", command=self.root.destroy).pack(side="right")
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Pronto para testar", foreground="blue")
        self.status_label.pack(pady=(20, 0))
    
    def teste_debug(self):
        """Teste de debug das variáveis"""
        produto = self.produto_var.get()
        quantidade = self.quantidade_var.get()
        preco = self.preco_var.get()
        
        debug_info = f"""
🔍 DEBUG DAS VARIÁVEIS:
📝 Produto: '{produto}' (tamanho: {len(produto)})
📊 Quantidade: '{quantidade}' (tamanho: {len(quantidade)})
💰 Preço: '{preco}' (tamanho: {len(preco)})

🧪 Produto stripped: '{produto.strip()}' (tamanho: {len(produto.strip())})
🧪 Produto vazio? {not produto.strip()}
🧪 Produto None? {produto is None}
        """
        
        print(debug_info)
        messagebox.showinfo("🔍 Debug", debug_info)
        
        self.status_label.config(text="Debug executado - veja console", foreground="green")
    
    def salvar_produto(self):
        """Salvar produto com debug"""
        try:
            produto = self.produto_var.get().strip()
            quantidade_str = self.quantidade_var.get().strip()
            preco_str = self.preco_var.get().strip()
            
            print(f"\n🔍 SALVAR PRODUTO - DEBUG:")
            print(f"📝 Produto original: '{self.produto_var.get()}'")
            print(f"📝 Produto stripped: '{produto}' (tamanho: {len(produto)})")
            print(f"📊 Quantidade: '{quantidade_str}'")
            print(f"💰 Preço: '{preco_str}'")
            
            # Validação
            if not produto:
                erro = f"❌ PRODUTO VAZIO!\nCapturado: '{produto}'\nTamanho: {len(produto)}"
                print(erro)
                messagebox.showerror("Erro", erro)
                self.status_label.config(text="Erro: produto vazio", foreground="red")
                return
            
            # Conversões
            try:
                quantidade = int(float(quantidade_str)) if quantidade_str else 0
                preco = float(preco_str.replace(',', '.')) if preco_str else 0.0
            except ValueError as e:
                erro = f"Erro de conversão: {e}"
                print(erro)
                messagebox.showerror("Erro", erro)
                return
            
            # Salvar no banco
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO estoque (produto, categoria, quantidade, preco)
                    VALUES (?, ?, ?, ?)
                """, (produto, "Teste", quantidade, preco))
                conn.commit()
            
            sucesso = f"✅ SUCESSO!\nProduto: {produto}\nQuantidade: {quantidade}\nPreço: R$ {preco:.2f}"
            print(sucesso)
            messagebox.showinfo("Sucesso", sucesso)
            
            self.status_label.config(text="Produto salvo com sucesso!", foreground="green")
            
            # Limpar campos
            self.produto_var.set("")
            self.quantidade_var.set("")
            self.preco_var.set("")
            
        except Exception as e:
            erro = f"Erro inesperado: {e}"
            print(erro)
            messagebox.showerror("Erro", erro)
            self.status_label.config(text="Erro ao salvar", foreground="red")
    
    def run(self):
        """Executar teste"""
        print("🧪 INICIANDO TESTE DE CADASTRO")
        print("=" * 40)
        print("1. Digite 'hamburguer' no campo produto")
        print("2. Clique 'Teste Debug' para ver variáveis")
        print("3. Clique 'Salvar' para testar cadastro")
        print("=" * 40)
        
        self.root.mainloop()

if __name__ == "__main__":
    teste = TesteCadastroSimples()
    teste.run()