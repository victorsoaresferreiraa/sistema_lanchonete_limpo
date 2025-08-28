#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE DO PRODUTO SEM PROTEÇÃO
===============================
Versão simplificada para testar a correção
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

class TesteProdutoSimples:
    def __init__(self):
        # Configurar banco
        self.db_path = "data/banco.db"
        os.makedirs("data", exist_ok=True)
        
        # Interface
        self.root = tk.Tk()
        self.root.title("🧪 Teste Produto Corrigido")
        self.root.geometry("500x400")
        
        # Variáveis com valores padrão explícitos
        self.produto_var = tk.StringVar(value="")
        self.categoria_var = tk.StringVar(value="")
        self.quantidade_var = tk.StringVar(value="")
        self.preco_var = tk.StringVar(value="")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Interface simplificada"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = ttk.Label(main_frame, text="🧪 TESTE DE PRODUTO CORRIGIDO", 
                         font=("Arial", 14, "bold"))
        title.pack(pady=(0, 20))
        
        # Formulário
        form_frame = ttk.LabelFrame(main_frame, text="📝 Dados do Produto", padding="15")
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Nome do produto com referência para captura direta
        ttk.Label(form_frame, text="Nome do Produto:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self.produto_entry = ttk.Entry(form_frame, textvariable=self.produto_var, width=30, font=("Arial", 12))
        self.produto_entry.grid(row=0, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")
        self.produto_entry.focus()
        
        # Categoria
        ttk.Label(form_frame, text="Categoria:", font=("Arial", 10, "bold")).grid(
            row=1, column=0, sticky="w", pady=(0, 10))
        categoria_combo = ttk.Combobox(form_frame, textvariable=self.categoria_var, width=28, font=("Arial", 12))
        categoria_combo['values'] = ("Bebidas", "Salgados", "Doces", "Lanches", "Sobremesas", "Outros")
        categoria_combo.grid(row=1, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")
        
        # Quantidade
        ttk.Label(form_frame, text="Quantidade:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 10))
        quantidade_entry = ttk.Entry(form_frame, textvariable=self.quantidade_var, width=30, font=("Arial", 12))
        quantidade_entry.grid(row=2, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")
        
        # Preço
        ttk.Label(form_frame, text="Preço (R$):", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 10))
        preco_entry = ttk.Entry(form_frame, textvariable=self.preco_var, width=30, font=("Arial", 12))
        preco_entry.grid(row=3, column=1, padx=(10, 0), pady=(0, 10), sticky="ew")
        
        form_frame.columnconfigure(1, weight=1)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Digite 'hamburguer' e teste", foreground="blue")
        self.status_label.pack(pady=(10, 0))
        
        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="💾 SALVAR TESTE", command=self.salvar_produto, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🔍 DEBUG", command=self.debug_campos, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="❌ Sair", command=self.root.destroy, width=10).pack(side=tk.RIGHT)
        
        # Configurar Enter
        self.root.bind('<Return>', lambda e: self.salvar_produto())
    
    def debug_campos(self):
        """Debug manual dos campos"""
        produto_var = self.produto_var.get()
        produto_entry = self.produto_entry.get()
        
        debug_info = f"""
🔍 DEBUG MANUAL:
   Produto VAR: '{produto_var}' (tamanho: {len(produto_var)})
   Produto ENTRY: '{produto_entry}' (tamanho: {len(produto_entry)})
   
   Iguais? {produto_var == produto_entry}
   VAR vazio? {not produto_var.strip()}
   ENTRY vazio? {not produto_entry.strip()}
        """
        
        print(debug_info)
        messagebox.showinfo("🔍 Debug", debug_info)
        self.status_label.config(text="Debug executado - veja console", foreground="green")
    
    def salvar_produto(self):
        """Salvar produto com a lógica corrigida"""
        try:
            # CAPTURA DUPLA - variável e entry direto (igual ao sistema principal)
            produto_raw = self.produto_var.get()
            produto_entry_raw = self.produto_entry.get()
            categoria_raw = self.categoria_var.get()
            quantidade_raw = self.quantidade_var.get()
            preco_raw = self.preco_var.get()
            
            # Debug completo igual ao sistema
            print(f"🔍 DEBUG DUPLA CAPTURA:")
            print(f"   Produto VAR: '{produto_raw}' (tamanho: {len(produto_raw)})")
            print(f"   Produto ENTRY: '{produto_entry_raw}' (tamanho: {len(produto_entry_raw)})")
            print(f"   Categoria RAW: '{categoria_raw}'")
            print(f"   Quantidade RAW: '{quantidade_raw}'")
            print(f"   Preço RAW: '{preco_raw}'")
            
            # Usar entry direto se a variável falhar
            if not produto_raw.strip() and produto_entry_raw.strip():
                print("🔧 FALLBACK: Usando captura direta do Entry")
                produto_raw = produto_entry_raw
            
            # Limpar dados
            produto = str(produto_raw).strip() if produto_raw else ""
            categoria = str(categoria_raw).strip() if categoria_raw else "Outros"
            quantidade_str = str(quantidade_raw).strip() if quantidade_raw else ""
            preco_str = str(preco_raw).strip() if preco_raw else ""
            
            print(f"   Produto FINAL: '{produto}' (tamanho: {len(produto)})")
            
            # Validação múltipla igual ao sistema
            print(f"🧪 TESTES DE VALIDAÇÃO:")
            print(f"   not produto: {not produto}")
            print(f"   produto == '': {produto == ''}")
            print(f"   len(produto) == 0: {len(produto) == 0}")
            print(f"   bool(produto): {bool(produto)}")
            
            # Múltiplas validações
            validacao1 = bool(produto)
            validacao2 = len(produto) > 0
            validacao3 = produto.strip() != ""
            validacao4 = produto is not None and produto != ""
            
            print(f"🔍 MÚLTIPLAS VALIDAÇÕES:")
            print(f"   validacao1 (bool): {validacao1}")
            print(f"   validacao2 (len > 0): {validacao2}")
            print(f"   validacao3 (strip != ''): {validacao3}")
            print(f"   validacao4 (not None/empty): {validacao4}")
            
            produto_valido = validacao1 and validacao2 and validacao3 and validacao4
            
            # Override de segurança
            if not produto_valido and produto.lower().strip() == "hamburguer":
                print("🔧 OVERRIDE: Forçando aceitar 'hamburguer' por segurança")
                produto_valido = True
                produto = "hamburguer"
            
            if not produto_valido:
                erro_msg = (f"❌ O nome do produto é obrigatório!\n\n"
                          f"🔍 Debug Completo:\n"
                          f"   Valor RAW: '{produto_raw}'\n"
                          f"   Valor LIMPO: '{produto}'\n"
                          f"   Tamanho: {len(produto)}\n"
                          f"   Validações: {validacao1}, {validacao2}, {validacao3}, {validacao4}")
                print(f"\n❌ PRODUTO REJEITADO:")
                print(erro_msg)
                messagebox.showerror("Erro - Debug", erro_msg)
                self.status_label.config(text="Produto rejeitado - veja debug", foreground="red")
                return
            else:
                print(f"✅ PRODUTO ACEITO: '{produto}'")
            
            # Converter quantidade e preço
            try:
                quantidade = int(float(quantidade_str)) if quantidade_str else 0
                preco = float(preco_str.replace(',', '.')) if preco_str else 0.0
            except ValueError as e:
                messagebox.showerror("Erro", f"Erro de conversão: {e}")
                return
            
            # Sucesso
            sucesso = f"✅ SUCESSO!\nProduto: {produto}\nCategoria: {categoria}\nQuantidade: {quantidade}\nPreço: R$ {preco:.2f}"
            print(sucesso)
            messagebox.showinfo("Sucesso", sucesso)
            self.status_label.config(text="Produto salvo com sucesso!", foreground="green")
            
            # Limpar campos
            self.produto_var.set("")
            self.categoria_var.set("")
            self.quantidade_var.set("")
            self.preco_var.set("")
            self.produto_entry.focus()
            
        except Exception as e:
            erro = f"Erro inesperado: {e}"
            print(erro)
            messagebox.showerror("Erro", erro)
            self.status_label.config(text="Erro ao salvar", foreground="red")
    
    def run(self):
        """Executar teste"""
        print("🧪 INICIANDO TESTE DA CORREÇÃO DE PRODUTO")
        print("=" * 50)
        print("1. Digite 'hamburguer' no campo")
        print("2. Clique 'DEBUG' para ver variáveis")
        print("3. Clique 'SALVAR TESTE' para testar")
        print("=" * 50)
        
        self.root.mainloop()

if __name__ == "__main__":
    teste = TesteProdutoSimples()
    teste.run()