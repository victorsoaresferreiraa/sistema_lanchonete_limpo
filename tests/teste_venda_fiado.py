#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE ESPECÍFICO DA VENDA FIADO
=================================
Simula o problema relatado com "VICTOR SOARES FERREIRA"
"""

def simular_venda_fiado():
    """Simular processo de venda fiado"""
    print("🧪 SIMULANDO VENDA FIADO")
    print("=" * 40)
    
    # Cenário reportado pelo usuário
    cliente_nome = "VICTOR SOARES FERREIRA"
    carrinho = [
        {'produto': 'Misto Quente', 'quantidade': 1, 'preco_unitario': 7.50, 'total': 7.50},
        {'produto': 'Hamburguer', 'quantidade': 1, 'preco_unitario': 15.00, 'total': 15.00},
        {'produto': 'Refrigerante', 'quantidade': 1, 'preco_unitario': 3.50, 'total': 3.50}
    ]
    total_geral = 26.00
    
    print(f"Cliente: '{cliente_nome}'")
    print(f"Carrinho: {len(carrinho)} itens")
    print(f"Total: R$ {total_geral:.2f}")
    
    # Verificações que o sistema faz
    print("\n🔍 VERIFICAÇÕES DO SISTEMA:")
    
    # 1. Carrinho vazio?
    carrinho_vazio = not carrinho
    print(f"1. Carrinho vazio: {carrinho_vazio}")
    if carrinho_vazio:
        print("   ❌ PROBLEMA: Carrinho está vazio")
        return False
    
    # 2. Nome do cliente válido?
    cliente_valido = bool(cliente_nome.strip())
    print(f"2. Cliente válido: {cliente_valido}")
    print(f"   Nome: '{cliente_nome.strip()}'")
    print(f"   Tamanho: {len(cliente_nome.strip())} caracteres")
    if not cliente_valido:
        print("   ❌ PROBLEMA: Nome do cliente está vazio")
        return False
    
    # 3. Total válido?
    total_valido = total_geral > 0
    print(f"3. Total válido: {total_valido} (R$ {total_geral:.2f})")
    if not total_valido:
        print("   ❌ PROBLEMA: Total é zero ou negativo")
        return False
    
    # 4. Itens do carrinho válidos?
    print("4. Validando itens do carrinho:")
    for i, item in enumerate(carrinho, 1):
        produto_ok = bool(item.get('produto', '').strip())
        quantidade_ok = item.get('quantidade', 0) > 0
        preco_ok = item.get('preco_unitario', 0) > 0
        total_ok = item.get('total', 0) > 0
        
        print(f"   Item {i}: {item['produto']}")
        print(f"     Produto OK: {produto_ok}")
        print(f"     Quantidade OK: {quantidade_ok} ({item.get('quantidade', 0)})")
        print(f"     Preço OK: {preco_ok} (R$ {item.get('preco_unitario', 0):.2f})")
        print(f"     Total OK: {total_ok} (R$ {item.get('total', 0):.2f})")
        
        if not (produto_ok and quantidade_ok and preco_ok and total_ok):
            print(f"   ❌ PROBLEMA: Item {i} tem dados inválidos")
            return False
    
    print("\n✅ TODAS AS VERIFICAÇÕES PASSARAM!")
    
    # Simular inserção no banco
    print("\n💾 SIMULANDO INSERÇÃO NO BANCO:")
    
    try:
        import sqlite3
        
        with sqlite3.connect("data/banco.db") as conn:
            cursor = conn.cursor()
            
            # Testar inserção para cada item
            for i, item in enumerate(carrinho, 1):
                print(f"   Inserindo item {i}: {item['produto']}")
                
                cursor.execute("""
                    INSERT INTO contas_abertas 
                    (cliente_nome, cliente_telefone, produto, quantidade, preco_unitario, total, data_vencimento, observacoes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cliente_nome,
                    "(11) 99999-9999",  # Telefone teste
                    item['produto'],
                    item['quantidade'],
                    item['preco_unitario'],
                    item['total'],
                    "28/09/2025",  # Data vencimento teste
                    "Teste de venda fiado"
                ))
            
            conn.commit()
            print("   ✅ Todas as inserções foram bem-sucedidas!")
            
            # Verificar se realmente inseriu
            cursor.execute("SELECT COUNT(*) FROM contas_abertas WHERE cliente_nome = ? AND observacoes = ?", 
                         (cliente_nome, "Teste de venda fiado"))
            count = cursor.fetchone()[0]
            print(f"   ✅ {count} registros inseridos no banco")
            
            # Limpar registros de teste
            cursor.execute("DELETE FROM contas_abertas WHERE cliente_nome = ? AND observacoes = ?", 
                         (cliente_nome, "Teste de venda fiado"))
            conn.commit()
            print("   🧹 Registros de teste removidos")
            
            return True
            
    except Exception as e:
        print(f"   ❌ ERRO na inserção: {e}")
        return False

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO: VENDA FIADO NÃO FUNCIONA")
    print("Testando cenário: VICTOR SOARES FERREIRA")
    print("=" * 50)
    
    sucesso = simular_venda_fiado()
    
    print("\n🎯 RESULTADO:")
    if sucesso:
        print("✅ SIMULAÇÃO PASSOU - O sistema deveria funcionar!")
        print("O problema pode estar na interface (janela não abrindo)")
    else:
        print("❌ SIMULAÇÃO FALHOU - Problema identificado!")
        
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Verifique o console quando clicar 'FIADO (F3)'")
    print("2. Observe se aparece 'FINALIZAR FIADO DEBUG'")
    print("3. Veja se a janela de confirmação abre")

if __name__ == "__main__":
    main()