#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICAÇÃO DA TABELA CONTAS_ABERTAS
======================================
Verifica se a tabela existe e tem a estrutura correta
"""

import sqlite3
import traceback

def verificar_tabela_fiado():
    """Verificar estrutura da tabela contas_abertas"""
    print("🔍 VERIFICANDO TABELA CONTAS_ABERTAS")
    print("=" * 50)
    
    db_path = "data/banco.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar se tabela existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='contas_abertas'
            """)
            tabela_existe = cursor.fetchone()
            
            if tabela_existe:
                print("✅ Tabela 'contas_abertas' existe")
                
                # Verificar estrutura
                cursor.execute("PRAGMA table_info(contas_abertas)")
                colunas = cursor.fetchall()
                
                print("\n📋 ESTRUTURA DA TABELA:")
                for coluna in colunas:
                    cid, nome, tipo, notnull, default, pk = coluna
                    print(f"   {nome}: {tipo} {'(PK)' if pk else ''} {'NOT NULL' if notnull else ''}")
                
                # Verificar alguns registros
                cursor.execute("SELECT COUNT(*) FROM contas_abertas")
                total = cursor.fetchone()[0]
                print(f"\n📊 Total de registros: {total}")
                
                if total > 0:
                    cursor.execute("SELECT * FROM contas_abertas LIMIT 3")
                    registros = cursor.fetchall()
                    print("\n🔍 Primeiros registros:")
                    for i, registro in enumerate(registros, 1):
                        print(f"   {i}. {registro}")
            
            else:
                print("❌ Tabela 'contas_abertas' NÃO existe!")
                print("\n🔧 CRIANDO TABELA...")
                
                # Criar tabela
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS contas_abertas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente_nome TEXT NOT NULL,
                        cliente_telefone TEXT,
                        produto TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco_unitario REAL NOT NULL,
                        total REAL NOT NULL,
                        data_vencimento TEXT,
                        observacoes TEXT,
                        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'pendente'
                    )
                """)
                conn.commit()
                print("✅ Tabela criada com sucesso!")
                
            # Testar inserção
            print("\n🧪 TESTANDO INSERÇÃO...")
            cursor.execute("""
                INSERT INTO contas_abertas 
                (cliente_nome, cliente_telefone, produto, quantidade, preco_unitario, total, data_vencimento, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ("TESTE VICTOR", "(11) 99999-9999", "Água", 3, 2.00, 6.00, "28/09/2025", "Teste de inserção"))
            conn.commit()
            
            # Verificar se inseriu
            cursor.execute("SELECT * FROM contas_abertas WHERE cliente_nome = 'TESTE VICTOR'")
            teste = cursor.fetchone()
            
            if teste:
                print("✅ Inserção de teste funcionou!")
                print(f"   Registro: {teste}")
                
                # Limpar teste
                cursor.execute("DELETE FROM contas_abertas WHERE cliente_nome = 'TESTE VICTOR'")
                conn.commit()
                print("🧹 Registro de teste removido")
            else:
                print("❌ Falha na inserção de teste")
                
    except Exception as e:
        print(f"❌ ERRO: {e}")
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO: VENDA FIADO")
    print("Verificando se o problema está na tabela do banco")
    
    verificar_tabela_fiado()
    
    print("\n🎯 CONCLUSÃO:")
    print("Se a tabela existe e o teste passou, o problema pode estar:")
    print("1. Na validação do nome do cliente")
    print("2. Na abertura da janela de confirmação")
    print("3. No processamento do carrinho")

if __name__ == "__main__":
    main()