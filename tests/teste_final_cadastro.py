#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 TESTE FINAL DO CADASTRO - SIMULAÇÃO
=====================================
"""

import sys
import os

# Adicionar o sistema ao path
sys.path.append('.')

def simular_salvar_produto():
    """Simular o processo de salvar produto com os mesmos valores"""
    
    print("🧪 SIMULAÇÃO DO PROCESSO DE SALVAR PRODUTO")
    print("=" * 50)
    
    # Simular os valores como se viessem do tkinter
    produto_raw = "hamburguer"  # Exatamente como aparece na imagem
    categoria_raw = ""
    quantidade_raw = ""
    preco_raw = ""
    
    print(f"📥 VALORES DE ENTRADA (simulando tkinter):")
    print(f"   produto_raw: '{produto_raw}'")
    print(f"   categoria_raw: '{categoria_raw}'")
    print(f"   quantidade_raw: '{quantidade_raw}'")
    print(f"   preco_raw: '{preco_raw}'")
    print()
    
    # Aplicar a mesma lógica do código
    print(f"🔍 DEBUG COMPLETO:")
    print(f"   Produto RAW: '{produto_raw}' (tipo: {type(produto_raw)}, tamanho: {len(produto_raw)})")
    print(f"   Categoria RAW: '{categoria_raw}'")
    print(f"   Quantidade RAW: '{quantidade_raw}'")
    print(f"   Preço RAW: '{preco_raw}'")
    
    # Limpar dados
    produto = str(produto_raw).strip() if produto_raw else ""
    categoria = str(categoria_raw).strip() if categoria_raw else "Outros"
    quantidade_str = str(quantidade_raw).strip() if quantidade_raw else ""
    preco_str = str(preco_raw).strip() if preco_raw else ""
    
    print(f"   Produto LIMPO: '{produto}' (tamanho: {len(produto)})")
    print()
    
    # Testes de validação
    print(f"🧪 TESTES DE VALIDAÇÃO:")
    print(f"   not produto: {not produto}")
    print(f"   produto == '': {produto == ''}")
    print(f"   len(produto) == 0: {len(produto) == 0}")
    print(f"   bool(produto): {bool(produto)}")
    
    # Verificar caracteres especiais
    if produto:
        chars_info = [f"'{c}' (ord:{ord(c)})" for c in produto[:10]]
        print(f"   Caracteres: {' '.join(chars_info)}")
    
    # Validação final
    produto_valido = produto and len(produto.strip()) > 0 and produto.strip() != ""
    
    print()
    print(f"🎯 RESULTADO DA VALIDAÇÃO:")
    print(f"   produto_valido: {produto_valido}")
    
    if not produto_valido:
        print("❌ PRODUTO SERIA REJEITADO")
        print("   Motivo: Falhou na validação")
    else:
        print("✅ PRODUTO SERIA ACEITO")
        print(f"   Produto final: '{produto}'")
        
        # Simular validações numéricas
        print(f"\n🔢 VALIDAÇÕES NUMÉRICAS:")
        
        # Quantidade
        if not quantidade_str:
            quantidade = 0
            print(f"   Quantidade: {quantidade} (padrão)")
        else:
            try:
                quantidade = int(float(quantidade_str))
                print(f"   Quantidade: {quantidade} (convertida)")
            except ValueError:
                print(f"   ❌ Erro na quantidade: '{quantidade_str}'")
                return False
        
        # Preço
        if not preco_str:
            preco = 0.0
            print(f"   Preço: {preco} (padrão)")
        else:
            try:
                preco = float(preco_str.replace(',', '.'))
                print(f"   Preço: {preco} (convertido)")
            except ValueError:
                print(f"   ❌ Erro no preço: '{preco_str}'")
                return False
        
        print(f"\n✅ DADOS FINAIS PARA SALVAR:")
        print(f"   Produto: '{produto}'")
        print(f"   Categoria: '{categoria}'")
        print(f"   Quantidade: {quantidade}")
        print(f"   Preço: R$ {preco:.2f}")
        
        return True
    
    return False

def main():
    """Função principal"""
    print("🚀 TESTE FINAL DO SISTEMA DE CADASTRO")
    print("=" * 60)
    print("Reproduzindo exatamente o que acontece quando:")
    print("1. Usuário digita 'hamburguer'")
    print("2. Deixa outros campos vazios")
    print("3. Clica salvar")
    print("=" * 60)
    
    sucesso = simular_salvar_produto()
    
    print("\n" + "=" * 60)
    if sucesso:
        print("🎉 CONCLUSÃO: O produto deveria ser aceito!")
        print("   Se está sendo rejeitado, o problema está na interface.")
    else:
        print("❌ CONCLUSÃO: O produto foi rejeitado na validação.")
    print("=" * 60)

if __name__ == "__main__":
    main()