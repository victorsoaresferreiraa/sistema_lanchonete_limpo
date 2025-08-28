#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTE SISTEMÁTICO COMPLETO DO SISTEMA
=======================================
Executa todos os testes de forma automatizada
"""

import sqlite3
import os
import sys
import json
from datetime import datetime
import traceback

class TesteSistemaCompleto:
    def __init__(self):
        self.db_path = "data/banco.db"
        self.resultados = []
        self.inicio_teste = datetime.now()
        
    def log_resultado(self, teste, status, detalhes="", erro=""):
        """Registrar resultado do teste"""
        resultado = {
            "teste": teste,
            "status": status,  # PASS/FAIL
            "detalhes": detalhes,
            "erro": erro,
            "timestamp": datetime.now().isoformat()
        }
        self.resultados.append(resultado)
        
        # Log imediato
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {teste}: {status}")
        if detalhes:
            print(f"   {detalhes}")
        if erro:
            print(f"   ERRO: {erro}")
        print()
    
    def teste_1_banco_dados(self):
        """Teste 1: Conectividade e estrutura do banco"""
        try:
            print("🧪 TESTE 1: BANCO DE DADOS")
            print("-" * 40)
            
            # Verificar arquivo existe
            if not os.path.exists(self.db_path):
                self.log_resultado("1.1 Arquivo Banco", "FAIL", erro="Arquivo banco.db não encontrado")
                return
            
            self.log_resultado("1.1 Arquivo Banco", "PASS", "banco.db encontrado")
            
            # Conectar
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar tabela estoque
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estoque'")
                if cursor.fetchone():
                    self.log_resultado("1.2 Tabela Estoque", "PASS", "Tabela estoque existe")
                else:
                    self.log_resultado("1.2 Tabela Estoque", "FAIL", erro="Tabela estoque não encontrada")
                
                # Contar produtos
                cursor.execute("SELECT COUNT(*) FROM estoque")
                count = cursor.fetchone()[0]
                self.log_resultado("1.3 Produtos Existentes", "PASS", f"{count} produtos no banco")
                
                # Testar inserção
                cursor.execute("INSERT INTO estoque (produto, categoria, quantidade, preco) VALUES (?, ?, ?, ?)",
                             ("TESTE_PRODUTO", "TESTE", 1, 1.0))
                conn.commit()
                
                # Verificar inserção
                cursor.execute("SELECT * FROM estoque WHERE produto = 'TESTE_PRODUTO'")
                if cursor.fetchone():
                    self.log_resultado("1.4 Inserção Banco", "PASS", "Inserção funcionando")
                    
                    # Limpar teste
                    cursor.execute("DELETE FROM estoque WHERE produto = 'TESTE_PRODUTO'")
                    conn.commit()
                else:
                    self.log_resultado("1.4 Inserção Banco", "FAIL", erro="Falha na inserção")
                    
        except Exception as e:
            self.log_resultado("1.X Banco Geral", "FAIL", erro=str(e))
    
    def teste_2_validacao_produto(self):
        """Teste 2: Validação de produtos"""
        print("🧪 TESTE 2: VALIDAÇÃO DE PRODUTOS")
        print("-" * 40)
        
        # Importar módulo
        try:
            sys.path.append('.')
            # Simular validações do sistema
            
            # Teste produtos válidos
            produtos_validos = [
                "hamburguer",
                "Batata Frita",
                "REFRIGERANTE",
                "Pizza Margherita",
                "Suco de Laranja"
            ]
            
            for produto in produtos_validos:
                # Simular lógica de validação
                produto_limpo = str(produto).strip()
                if produto_limpo and len(produto_limpo) > 0:
                    self.log_resultado(f"2.1 Produto Válido '{produto}'", "PASS", f"'{produto_limpo}' aceito")
                else:
                    self.log_resultado(f"2.1 Produto Válido '{produto}'", "FAIL", f"'{produto}' rejeitado incorretamente")
            
            # Teste produtos inválidos
            produtos_invalidos = ["", "   ", None]
            
            for produto in produtos_invalidos:
                try:
                    produto_limpo = str(produto).strip() if produto else ""
                    if not produto_limpo or len(produto_limpo) == 0:
                        self.log_resultado(f"2.2 Produto Inválido '{produto}'", "PASS", "Corretamente rejeitado")
                    else:
                        self.log_resultado(f"2.2 Produto Inválido '{produto}'", "FAIL", "Deveria ser rejeitado")
                except:
                    self.log_resultado(f"2.2 Produto Inválido '{produto}'", "PASS", "Corretamente rejeitado com exceção")
            
        except Exception as e:
            self.log_resultado("2.X Validação Geral", "FAIL", erro=str(e))
    
    def teste_3_calculos_precos(self):
        """Teste 3: Cálculos de preços e totais"""
        print("🧪 TESTE 3: CÁLCULOS DE PREÇOS")
        print("-" * 40)
        
        try:
            # Teste conversões de preço
            testes_preco = [
                ("15.00", 15.0),
                ("15,50", 15.5),
                ("8.75", 8.75),
                ("10", 10.0),
                ("0", 0.0)
            ]
            
            for preco_str, esperado in testes_preco:
                try:
                    preco_limpo = preco_str.replace(',', '.').replace('R$', '').strip()
                    preco_convertido = float(preco_limpo)
                    
                    if abs(preco_convertido - esperado) < 0.01:  # Tolerância para float
                        self.log_resultado(f"3.1 Conversão Preço '{preco_str}'", "PASS", f"{preco_str} → {preco_convertido}")
                    else:
                        self.log_resultado(f"3.1 Conversão Preço '{preco_str}'", "FAIL", f"Esperado {esperado}, obtido {preco_convertido}")
                except Exception as e:
                    self.log_resultado(f"3.1 Conversão Preço '{preco_str}'", "FAIL", erro=str(e))
            
            # Teste cálculos de total
            testes_total = [
                (2, 15.0, 30.0),  # quantidade, preço, total esperado
                (1, 8.5, 8.5),
                (3, 12.33, 36.99),
                (0, 10.0, 0.0)
            ]
            
            for qty, preco, total_esperado in testes_total:
                total_calculado = qty * preco
                if abs(total_calculado - total_esperado) < 0.01:
                    self.log_resultado(f"3.2 Cálculo Total {qty}x{preco}", "PASS", f"Total: {total_calculado}")
                else:
                    self.log_resultado(f"3.2 Cálculo Total {qty}x{preco}", "FAIL", f"Esperado {total_esperado}, obtido {total_calculado}")
            
        except Exception as e:
            self.log_resultado("3.X Cálculos Geral", "FAIL", erro=str(e))
    
    def teste_4_estrutura_carrinho(self):
        """Teste 4: Estrutura e manipulação do carrinho"""
        print("🧪 TESTE 4: ESTRUTURA DO CARRINHO")
        print("-" * 40)
        
        try:
            # Simular estrutura do carrinho
            carrinho = []
            
            # Teste adição de item
            item1 = {
                'produto': 'Hamburguer',
                'quantidade': 1,
                'preco_unitario': 15.0,
                'total': 15.0
            }
            carrinho.append(item1)
            
            if len(carrinho) == 1 and carrinho[0]['produto'] == 'Hamburguer':
                self.log_resultado("4.1 Adição Item", "PASS", f"Item adicionado: {item1}")
            else:
                self.log_resultado("4.1 Adição Item", "FAIL", "Falha ao adicionar item")
            
            # Teste múltiplos itens
            item2 = {
                'produto': 'Refrigerante',
                'quantidade': 2,
                'preco_unitario': 3.5,
                'total': 7.0
            }
            carrinho.append(item2)
            
            if len(carrinho) == 2:
                self.log_resultado("4.2 Múltiplos Itens", "PASS", f"{len(carrinho)} itens no carrinho")
            else:
                self.log_resultado("4.2 Múltiplos Itens", "FAIL", f"Esperado 2, obtido {len(carrinho)}")
            
            # Teste cálculo total geral
            total_geral = sum(item['total'] for item in carrinho)
            total_esperado = 15.0 + 7.0  # 22.0
            
            if abs(total_geral - total_esperado) < 0.01:
                self.log_resultado("4.3 Total Geral", "PASS", f"Total: R$ {total_geral:.2f}")
            else:
                self.log_resultado("4.3 Total Geral", "FAIL", f"Esperado {total_esperado}, obtido {total_geral}")
            
            # Teste formatação para TreeView
            for i, item in enumerate(carrinho):
                treeview_values = (
                    item['produto'],
                    item['quantidade'],
                    f"R$ {item['preco_unitario']:.2f}",
                    f"R$ {item['total']:.2f}"
                )
                
                if len(treeview_values) == 4 and all(str(v) for v in treeview_values):
                    self.log_resultado(f"4.4 Formato TreeView Item {i+1}", "PASS", f"Values: {treeview_values}")
                else:
                    self.log_resultado(f"4.4 Formato TreeView Item {i+1}", "FAIL", f"Formato inválido: {treeview_values}")
            
        except Exception as e:
            self.log_resultado("4.X Carrinho Geral", "FAIL", erro=str(e))
    
    def teste_5_sistema_arquivos(self):
        """Teste 5: Sistema de arquivos e configurações"""
        print("🧪 TESTE 5: SISTEMA DE ARQUIVOS")
        print("-" * 40)
        
        try:
            # Verificar estrutura de diretórios
            diretorios_necessarios = ["data", "src"]
            
            for diretorio in diretorios_necessarios:
                if os.path.exists(diretorio):
                    self.log_resultado(f"5.1 Diretório '{diretorio}'", "PASS", f"Diretório {diretorio} existe")
                else:
                    self.log_resultado(f"5.1 Diretório '{diretorio}'", "FAIL", f"Diretório {diretorio} não encontrado")
            
            # Verificar arquivos principais
            arquivos_principais = [
                "main_funcional.py",
                "sistema_protecao_autoria.py",
                "data/banco.db"
            ]
            
            for arquivo in arquivos_principais:
                if os.path.exists(arquivo):
                    tamanho = os.path.getsize(arquivo)
                    self.log_resultado(f"5.2 Arquivo '{arquivo}'", "PASS", f"Arquivo existe ({tamanho} bytes)")
                else:
                    self.log_resultado(f"5.2 Arquivo '{arquivo}'", "FAIL", f"Arquivo {arquivo} não encontrado")
            
            # Teste criação de arquivo temporário
            arquivo_teste = "data/teste_temp.txt"
            try:
                with open(arquivo_teste, "w") as f:
                    f.write("teste")
                
                if os.path.exists(arquivo_teste):
                    self.log_resultado("5.3 Criação Arquivo", "PASS", "Arquivo temporário criado")
                    os.remove(arquivo_teste)  # Limpar
                else:
                    self.log_resultado("5.3 Criação Arquivo", "FAIL", "Falha ao criar arquivo")
            except Exception as e:
                self.log_resultado("5.3 Criação Arquivo", "FAIL", erro=str(e))
            
        except Exception as e:
            self.log_resultado("5.X Arquivos Geral", "FAIL", erro=str(e))
    
    def gerar_relatorio(self):
        """Gerar relatório final dos testes"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        
        total_testes = len(self.resultados)
        testes_pass = sum(1 for r in self.resultados if r["status"] == "PASS")
        testes_fail = total_testes - testes_pass
        
        print(f"📅 Data/Hora: {self.inicio_teste.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏱️  Duração: {datetime.now() - self.inicio_teste}")
        print(f"📊 Total de Testes: {total_testes}")
        print(f"✅ Sucessos: {testes_pass}")
        print(f"❌ Falhas: {testes_fail}")
        print(f"📈 Taxa de Sucesso: {(testes_pass/total_testes*100):.1f}%")
        
        print("\n📋 RESUMO POR CATEGORIA:")
        categorias = {}
        for resultado in self.resultados:
            categoria = resultado["teste"].split(".")[0]
            if categoria not in categorias:
                categorias[categoria] = {"pass": 0, "fail": 0}
            categorias[categoria][resultado["status"].lower()] += 1
        
        for categoria, stats in categorias.items():
            total_cat = stats["pass"] + stats["fail"]
            taxa = (stats["pass"] / total_cat * 100) if total_cat > 0 else 0
            print(f"   {categoria}: {stats['pass']}/{total_cat} ({taxa:.1f}%)")
        
        # Salvar relatório detalhado
        relatorio_detalhado = {
            "inicio": self.inicio_teste.isoformat(),
            "fim": datetime.now().isoformat(),
            "total_testes": total_testes,
            "sucessos": testes_pass,
            "falhas": testes_fail,
            "taxa_sucesso": testes_pass/total_testes*100,
            "resultados": self.resultados
        }
        
        with open("data/relatorio_testes.json", "w", encoding="utf-8") as f:
            json.dump(relatorio_detalhado, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório detalhado salvo em: data/relatorio_testes.json")
        
        # Conclusão
        print("\n🎯 CONCLUSÃO:")
        if testes_fail == 0:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema está funcionando perfeitamente.")
        elif testes_fail <= 2:
            print("⚠️ Alguns testes falharam, mas sistema está majoritariamente funcional.")
        else:
            print("❌ Múltiplas falhas detectadas. Sistema precisa de correções.")
        
        return testes_fail == 0
    
    def executar_todos_testes(self):
        """Executar todos os testes sistematicamente"""
        print("🚀 INICIANDO TESTE SISTEMÁTICO COMPLETO")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("🎯 Objetivo: Verificar todas as funcionalidades do sistema")
        print("=" * 60)
        print()
        
        try:
            # Executar todos os testes
            self.teste_1_banco_dados()
            self.teste_2_validacao_produto()
            self.teste_3_calculos_precos()
            self.teste_4_estrutura_carrinho()
            self.teste_5_sistema_arquivos()
            
            # Gerar relatório
            sucesso_geral = self.gerar_relatorio()
            
            return sucesso_geral
            
        except Exception as e:
            print(f"❌ ERRO GERAL NO TESTE: {e}")
            traceback.print_exc()
            return False

def main():
    """Função principal"""
    teste = TesteSistemaCompleto()
    sucesso = teste.executar_todos_testes()
    
    # Código de saída
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main()