#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE DE VALIDAÇÃO DE PRODUTO - SEM GUI
==========================================
"""

def testar_validacao_produto():
    """Testar a validação que está falhando"""
    
    print("🧪 TESTE DE VALIDAÇÃO DE PRODUTO")
    print("=" * 40)
    
    # Simular os valores que o usuário digitou
    valores_teste = [
        "hamburguer",        # Caso normal
        "  hamburguer  ",    # Com espaços
        "",                  # Vazio
        "   ",              # Só espaços
        "Hamburguer",       # Capitalizado
        "HAMBURGUER",       # Maiúsculo
        "hamburguer123",    # Com números
        "hambúrguer",       # Com acentos
    ]
    
    for i, valor_original in enumerate(valores_teste, 1):
        print(f"\n🔍 TESTE {i}:")
        print(f"📝 Valor original: '{valor_original}'")
        print(f"📏 Tamanho original: {len(valor_original)}")
        
        # Aplicar a mesma lógica do código
        produto = valor_original.strip()
        print(f"✂️  Após strip(): '{produto}'")
        print(f"📏 Tamanho após strip: {len(produto)}")
        
        # Testar a validação
        if not produto:
            print("❌ RESULTADO: Produto vazio - seria rejeitado")
            print(f"   Motivo: not produto = {not produto}")
        else:
            print("✅ RESULTADO: Produto válido - seria aceito")
        
        print("-" * 30)

def testar_conversao_numeros():
    """Testar conversão de números"""
    print("\n🔢 TESTE DE CONVERSÃO DE NÚMEROS")
    print("=" * 40)
    
    testes_quantidade = ["10", "10.0", "10,0", "  10  ", "", "abc", "10.5"]
    testes_preco = ["5.50", "5,50", "  5.50  ", "", "abc", "5"]
    
    print("\n📊 TESTE QUANTIDADE:")
    for valor in testes_quantidade:
        try:
            if not valor.strip():
                resultado = 0
            else:
                resultado = int(float(valor.strip()))
            print(f"✅ '{valor}' → {resultado}")
        except Exception as e:
            print(f"❌ '{valor}' → ERRO: {e}")
    
    print("\n💰 TESTE PREÇO:")
    for valor in testes_preco:
        try:
            if not valor.strip():
                resultado = 0.0
            else:
                resultado = float(valor.strip().replace(',', '.'))
            print(f"✅ '{valor}' → {resultado}")
        except Exception as e:
            print(f"❌ '{valor}' → ERRO: {e}")

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTES DE VALIDAÇÃO")
    print("=" * 50)
    
    testar_validacao_produto()
    testar_conversao_numeros()
    
    print("\n🎯 CONCLUSÃO:")
    print("Se 'hamburguer' está sendo rejeitado, o problema pode ser:")
    print("1. Campo não está capturando o valor")
    print("2. Caracteres invisíveis no texto")
    print("3. Problema na variável tkinter")
    print("4. Encoding de caracteres")

if __name__ == "__main__":
    main()