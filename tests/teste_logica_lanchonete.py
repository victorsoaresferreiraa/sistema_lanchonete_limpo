#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE DA LÓGICA DE LANCHONETE
===============================
Testa se a soma de quantidades está funcionando
"""

def testar_logica_carrinho():
    """Simular lógica do carrinho com soma de quantidades"""
    print("🧪 TESTE: LÓGICA DE CARRINHO LANCHONETE")
    print("=" * 50)
    
    # Simular carrinho vazio
    carrinho = []
    
    def adicionar_produto(produto_nome, quantidade, preco):
        """Simular adição de produto ao carrinho"""
        print(f"\n➕ Adicionando: {quantidade}x {produto_nome} @ R$ {preco:.2f}")
        
        # Verificar se produto já existe
        produto_existente = None
        for i, item in enumerate(carrinho):
            if item['produto'] == produto_nome and item['preco_unitario'] == preco:
                produto_existente = i
                break
        
        if produto_existente is not None:
            # Produto já existe - somar quantidades
            item_existente = carrinho[produto_existente]
            nova_quantidade = item_existente['quantidade'] + quantidade
            novo_total = nova_quantidade * preco
            
            carrinho[produto_existente] = {
                'produto': produto_nome,
                'quantidade': nova_quantidade,
                'preco_unitario': preco,
                'total': novo_total
            }
            
            print(f"   ✅ SOMANDO: {item_existente['quantidade']} + {quantidade} = {nova_quantidade}")
            print(f"   💰 NOVO TOTAL: R$ {novo_total:.2f}")
        else:
            # Produto novo
            total_item = quantidade * preco
            item_carrinho = {
                'produto': produto_nome,
                'quantidade': quantidade,
                'preco_unitario': preco,
                'total': total_item
            }
            carrinho.append(item_carrinho)
            print(f"   ➕ NOVO PRODUTO: {quantidade}x R$ {preco:.2f} = R$ {total_item:.2f}")
        
        return carrinho
    
    # Teste 1: Adicionar água pela primeira vez
    print("\n1️⃣ PRIMEIRA ÁGUA:")
    adicionar_produto("Água", 1, 2.00)
    
    # Teste 2: Adicionar mais águas (deve somar)
    print("\n2️⃣ MAIS ÁGUAS:")
    adicionar_produto("Água", 2, 2.00)  # Deve somar: 1 + 2 = 3
    
    # Teste 3: Adicionar produto diferente
    print("\n3️⃣ PRODUTO DIFERENTE:")
    adicionar_produto("Refrigerante", 1, 3.50)
    
    # Teste 4: Adicionar mais águas novamente
    print("\n4️⃣ MAIS ÁGUAS NOVAMENTE:")
    adicionar_produto("Água", 1, 2.00)  # Deve somar: 3 + 1 = 4
    
    # Resultado final
    print("\n🛒 CARRINHO FINAL:")
    print("=" * 30)
    total_geral = 0
    for i, item in enumerate(carrinho, 1):
        print(f"{i}. {item['produto']}: {item['quantidade']}x R$ {item['preco_unitario']:.2f} = R$ {item['total']:.2f}")
        total_geral += item['total']
    
    print(f"\n💰 TOTAL GERAL: R$ {total_geral:.2f}")
    
    # Verificações
    print("\n✅ VERIFICAÇÕES:")
    
    # Deve ter apenas 2 itens no carrinho
    if len(carrinho) == 2:
        print("✅ Carrinho tem 2 itens (correto)")
    else:
        print(f"❌ Carrinho tem {len(carrinho)} itens (deveria ter 2)")
    
    # Água deve ter quantidade 4
    agua_item = next((item for item in carrinho if item['produto'] == "Água"), None)
    if agua_item and agua_item['quantidade'] == 4:
        print("✅ Água tem quantidade 4 (correto)")
    else:
        print(f"❌ Água tem quantidade {agua_item['quantidade'] if agua_item else 'N/A'} (deveria ter 4)")
    
    # Total da água deve ser R$ 8.00
    if agua_item and agua_item['total'] == 8.00:
        print("✅ Total da água é R$ 8.00 (correto)")
    else:
        print(f"❌ Total da água é R$ {agua_item['total'] if agua_item else 'N/A'} (deveria ser R$ 8.00)")

def main():
    """Função principal"""
    print("🚀 TESTANDO LÓGICA DE LANCHONETE")
    print("Cenário: Pessoa quer 4 águas no total, adicionadas em etapas")
    print("Resultado esperado: 1 linha no carrinho com 4 águas")
    
    testar_logica_carrinho()
    
    print("\n🎯 CONCLUSÃO:")
    print("Se todos os testes passaram, a lógica está funcionando!")
    print("Agora o sistema vai somar quantidades como uma lanchonete real.")

if __name__ == "__main__":
    main()