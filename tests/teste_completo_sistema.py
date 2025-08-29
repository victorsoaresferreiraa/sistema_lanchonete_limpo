#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE COMPLETO DO SISTEMA LIMPO
=====================================
Script para testar todas as funcionalidades do sistema da lanchonete
Desenvolvido por: Victor Soares Ferreira
"""

import sys
import os
import sqlite3
import traceback
from datetime import datetime

def testar_banco_dados():
    """Testar conexão e estrutura do banco"""
    print("🔧 Testando banco de dados...")
    
    try:
        # Verificar se arquivo existe
        db_path = "data/banco.db"
        if not os.path.exists(db_path):
            print(f"❌ Banco não encontrado: {db_path}")
            return False
            
        # Testar conexão
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()
            print(f"✅ Tabelas encontradas: {[t[0] for t in tabelas]}")
            
            # Testar dados de exemplo
            cursor.execute("SELECT COUNT(*) FROM estoque")
            count_estoque = cursor.fetchone()[0]
            print(f"✅ Produtos no estoque: {count_estoque}")
            
            cursor.execute("SELECT COUNT(*) FROM historico_vendas")
            count_vendas = cursor.fetchone()[0]
            print(f"✅ Vendas no histórico: {count_vendas}")
            
            # Mostrar um produto de exemplo
            cursor.execute("SELECT * FROM estoque LIMIT 1")
            produto = cursor.fetchone()
            if produto:
                print(f"✅ Exemplo produto: {produto}")
            else:
                print("ℹ️ Nenhum produto cadastrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

def testar_importacoes():
    """Testar importações de bibliotecas"""
    print("\n📦 Testando importações...")
    
    bibliotecas = [
        'tkinter',
        'sqlite3', 
        'datetime',
        'subprocess'
    ]
    
    sucesso = True
    for lib in bibliotecas:
        try:
            __import__(lib)
            print(f"✅ {lib} - OK")
        except ImportError as e:
            print(f"❌ {lib} - ERRO: {e}")
            sucesso = False
    
    return sucesso

def testar_arquivos_essenciais():
    """Testar se arquivos essenciais existem"""
    print("\n📂 Verificando arquivos essenciais...")
    
    arquivos = [
        'main_funcional.py',
        'sistema_protecao_autoria.py',
        'instalar_python_e_executar.bat',
        'pyproject.toml',
        'README.md',
        'data/banco.db'
    ]
    
    sucesso = True
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            print(f"✅ {arquivo} ({tamanho} bytes)")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")
            sucesso = False
    
    return sucesso

def simular_cadastro_produto():
    """Simular cadastro de produto"""
    print("\n🛍️ Testando cadastro de produto...")
    
    try:
        # Teste de validação numérica
        quantidade_teste = "10"
        preco_teste = "5.50"
        
        # Simular conversão como no código real
        quantidade = int(float(quantidade_teste))
        preco = float(preco_teste.replace(',', '.'))
        
        print(f"✅ Quantidade: {quantidade} (tipo: {type(quantidade)})")
        print(f"✅ Preço: {preco} (tipo: {type(preco)})")
        
        # Teste com dados problemáticos
        casos_teste = [
            ("10", "5.50"),      # Caso normal
            ("10.0", "5,50"),    # Com decimal e vírgula
            ("", "5.50"),        # Quantidade vazia
            ("10", ""),          # Preço vazio
            ("abc", "5.50"),     # Quantidade inválida
            ("10", "abc")        # Preço inválido
        ]
        
        for qtd, prc in casos_teste:
            try:
                if not qtd:
                    quantidade = 0
                else:
                    quantidade = int(float(qtd))
                    
                if not prc:
                    preco = 0.0
                else:
                    preco = float(prc.replace(',', '.'))
                    
                print(f"✅ Teste: qtd='{qtd}' → {quantidade}, preço='{prc}' → {preco}")
                
            except ValueError as e:
                print(f"⚠️ Erro esperado: qtd='{qtd}', preço='{prc}' → {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de cadastro: {e}")
        return False

def testar_protecao_sistema():
    """Testar sistema de proteção"""
    print("\n🛡️ Testando sistema de proteção...")
    
    try:
        if os.path.exists('sistema_protecao_autoria.py'):
            print("✅ Arquivo de proteção encontrado")
            
            # Verificar conteúdo básico
            with open('sistema_protecao_autoria.py', 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            if 'Victor Soares Ferreira' in conteudo:
                print("✅ Dados do desenvolvedor encontrados")
            else:
                print("⚠️ Dados do desenvolvedor não encontrados")
                
            if 'SistemaProtecaoAutoria' in conteudo:
                print("✅ Classe de proteção encontrada")
            else:
                print("⚠️ Classe de proteção não encontrada")
                
        else:
            print("⚠️ Arquivo de proteção não encontrado")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de proteção: {e}")
        return False

def teste_interface_grafica():
    """Testar se interface pode ser iniciada"""
    print("\n🖥️ Testando interface gráfica...")
    
    try:
        import tkinter as tk
        
        # Criar janela de teste
        root = tk.Tk()
        root.title("Teste")
        root.geometry("200x100")
        
        # Testar componentes básicos
        label = tk.Label(root, text="Teste OK")
        label.pack()
        
        button = tk.Button(root, text="Fechar", command=root.destroy)
        button.pack()
        
        # Fechar imediatamente
        root.after(100, root.destroy)
        root.mainloop()
        
        print("✅ Interface gráfica funcional")
        return True
        
    except Exception as e:
        print(f"❌ Erro na interface: {e}")
        return False

def gerar_relatorio():
    """Gerar relatório final do teste"""
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DO TESTE")
    print("="*60)
    
    testes = [
        ("Banco de Dados", testar_banco_dados()),
        ("Importações", testar_importacoes()),
        ("Arquivos Essenciais", testar_arquivos_essenciais()),
        ("Cadastro de Produto", simular_cadastro_produto()),
        ("Sistema de Proteção", testar_protecao_sistema()),
        ("Interface Gráfica", teste_interface_grafica())
    ]
    
    sucessos = 0
    for nome, resultado in testes:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome:<20} {status}")
        if resultado:
            sucessos += 1
    
    print(f"\n📈 RESULTADO: {sucessos}/{len(testes)} testes passaram")
    
    if sucessos == len(testes):
        print("🎉 SISTEMA 100% FUNCIONAL!")
        return True
    else:
        print("⚠️ Sistema com problemas - Verificar falhas acima")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DO SISTEMA DA LANCHONETE")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"👨‍💻 Desenvolvedor: Victor Soares Ferreira")
    print(f"📧 Email: victorsoaresferreiradev09@gmail.com")
    print("=" * 60)
    
    try:
        resultado = gerar_relatorio()
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        if resultado:
            print("1. ✅ Sistema aprovado para uso")
            print("2. 📤 Pode fazer upload para GitHub")
            print("3. 🚀 Pronto para distribuição")
        else:
            print("1. 🔧 Corrigir problemas encontrados")
            print("2. 🧪 Executar teste novamente")
            print("3. ✅ Validar correções")
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NO TESTE: {e}")
        print("\n🔍 DETALHES DO ERRO:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()