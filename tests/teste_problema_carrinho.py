#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE ESPECÍFICO DO PROBLEMA DO CARRINHO
==========================================
Reproduz o cenário exato da imagem para debugar
"""

import sqlite3

def simular_selecao_coxinha():
    """Simular a seleção de Coxinha como na imagem"""
    print("🧪 SIMULANDO SELEÇÃO DE COXINHA")
    print("=" * 40)
    
    # Conectar ao banco
    db_path = "data/banco.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Buscar especificamente a Coxinha
            cursor.execute("SELECT produto, preco FROM estoque WHERE produto = 'Coxinha'")
            resultado = cursor.fetchone()
            
            if resultado:
                produto, preco = resultado
                print(f"✅ Produto encontrado: '{produto}'")
                print(f"✅ Preço no banco: R$ {preco:.2f}")
                
                # Simular dicionário de preços
                produtos_precos = {produto: preco}
                print(f"✅ Dicionário criado: {produtos_precos}")
                
                # Simular seleção
                produto_selecionado = "Coxinha"
                if produto_selecionado in produtos_precos:
                    preco_encontrado = produtos_precos[produto_selecionado]
                    preco_str = f"{preco_encontrado:.2f}"
                    print(f"✅ Preço encontrado: '{preco_str}'")
                    
                    # Simular cálculo com quantidade 3
                    quantidade = 3
                    total = quantidade * preco_encontrado
                    print(f"✅ Cálculo: {quantidade} × {preco_encontrado} = {total}")
                    print(f"✅ Total formatado: R$ {total:.2f}")
                    
                    # Verificar se seria correto
                    if total == 13.50:  # 3 × 4.50
                        print("🎯 CÁLCULO CORRETO!")
                    else:
                        print(f"❌ ERRO: esperado R$ 13.50, obtido R$ {total:.2f}")
                        
                else:
                    print(f"❌ Produto '{produto_selecionado}' NÃO encontrado no dicionário")
                    
            else:
                print("❌ Coxinha não encontrada no banco de dados")
                
                # Listar produtos disponíveis
                cursor.execute("SELECT produto, preco FROM estoque ORDER BY produto")
                produtos = cursor.fetchall()
                print("\n📦 Produtos disponíveis:")
                for i, (prod, preco) in enumerate(produtos[:5], 1):
                    print(f"   {i}. '{prod}' - R$ {preco:.2f}")
    
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_problema_interface():
    """Verificar possíveis problemas na interface"""
    print("\n🔍 VERIFICANDO POSSÍVEIS PROBLEMAS")
    print("=" * 40)
    
    # Problema 1: Campo preço não sendo preenchido
    print("1. PREENCHIMENTO AUTOMÁTICO DO PREÇO:")
    print("   - Quando seleciona 'Coxinha' no combo")
    print("   - Deveria preencher '4.50' no campo preço")
    print("   - Na imagem, campo preço está VAZIO")
    print("   → PROBLEMA: produto_selecionado() não está funcionando")
    
    # Problema 2: Cálculo do total
    print("\n2. CÁLCULO DO TOTAL:")
    print("   - Quantidade: 3")
    print("   - Preço: R$ 4.50 (deveria estar preenchido)")
    print("   - Total esperado: 3 × 4.50 = R$ 13.50")
    print("   - Total na imagem: R$ 4.50")
    print("   → PROBLEMA: calcular_total_item() usando preço 0 ou 1")
    
    # Problema 3: Total geral
    print("\n3. TOTAL GERAL:")
    print("   - Carrinho mostra: Coxinha, 1, R$ 4.50, R$ 4.50")
    print("   - Deveria ser: Coxinha, 3, R$ 4.50, R$ 13.50")
    print("   → PROBLEMA: quantidade não está sendo usada corretamente")

def main():
    """Função principal"""
    print("🔍 INVESTIGAÇÃO DO PROBLEMA DO CARRINHO")
    print("=" * 50)
    
    simular_selecao_coxinha()
    verificar_problema_interface()
    
    print("\n🎯 CONCLUSÃO:")
    print("O problema está em duas partes:")
    print("1. Campo preço não está sendo preenchido automaticamente")
    print("2. Cálculo está usando valores incorretos")
    print("\nPrecisamos corrigir o preenchimento automático do preço!")

if __name__ == "__main__":
    main()