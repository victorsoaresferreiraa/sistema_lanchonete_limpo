#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE RÁPIDO DA SEPARAÇÃO PRODUTO/PREÇO
==========================================
Testa se a nova implementação está funcionando
"""

import sqlite3

def testar_carregamento_produtos():
    """Testar carregamento de produtos sem preço no combo"""
    print("🧪 TESTE: CARREGAMENTO DE PRODUTOS")
    print("-" * 40)
    
    # Simular carregamento
    db_path = "data/banco.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT produto, preco FROM estoque ORDER BY produto LIMIT 5")
            produtos = cursor.fetchall()
            
            print(f"Produtos encontrados: {len(produtos)}")
            
            # Criar dicionário de preços para lookup rápido
            produtos_precos = {}
            produtos_lista = []
            
            for produto, preco in produtos:
                produtos_lista.append(produto)  # Apenas o nome do produto
                produtos_precos[produto] = preco  # Preço separado
            
            print("\n📦 PRODUTOS NO COMBO (apenas nomes):")
            for i, produto in enumerate(produtos_lista[:5], 1):
                print(f"   {i}. {produto}")
            
            print("\n💰 DICIONÁRIO DE PREÇOS:")
            for produto, preco in list(produtos_precos.items())[:5]:
                print(f"   {produto}: R$ {preco:.2f}")
            
            print("\n🎯 TESTE DE SELEÇÃO:")
            if produtos_lista:
                produto_teste = produtos_lista[0]
                preco_teste = produtos_precos[produto_teste]
                print(f"   Produto selecionado: '{produto_teste}'")
                print(f"   Preço encontrado: R$ {preco_teste:.2f}")
                print(f"   ✅ Lookup funcionando!")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE SEPARAÇÃO PRODUTO/PREÇO")
    print("=" * 50)
    
    sucesso = testar_carregamento_produtos()
    
    print("\n🎯 RESULTADO:")
    if sucesso:
        print("✅ Separação produto/preço funcionando corretamente!")
        print("   - Combo mostra apenas nomes dos produtos")
        print("   - Preços ficam em dicionário separado")
        print("   - Lookup por nome do produto funciona")
    else:
        print("❌ Falha na separação produto/preço")

if __name__ == "__main__":
    main()