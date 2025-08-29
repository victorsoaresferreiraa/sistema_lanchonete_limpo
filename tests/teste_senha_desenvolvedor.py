#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 TESTE DA SENHA DE DESENVOLVEDOR
=================================
Script para testar a funcionalidade de bypass com senha
"""

import hashlib
import json
import os
from datetime import datetime, timedelta

def testar_hash_senha():
    """Testar hash da senha"""
    senha = "Victor@1307"
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    print("🔑 TESTE DE HASH DA SENHA")
    print("=" * 40)
    print(f"Senha: {senha}")
    print(f"Hash: {senha_hash}")
    print()
    
    return senha_hash

def simular_bypass_desenvolvedor():
    """Simular criação de bypass"""
    print("💾 SIMULANDO BYPASS DE DESENVOLVEDOR")
    print("=" * 40)
    
    try:
        os.makedirs("data", exist_ok=True)
        
        data_expiracao = datetime.now() + timedelta(days=30)
        
        bypass_data = {
            "desenvolvedor": "Victor Soares Ferreira",
            "email": "victorsoaresferreiradev09@gmail.com",
            "hardware_id": "teste_hardware_123",
            "criacao": datetime.now().isoformat(),
            "expiracao": data_expiracao.isoformat(),
            "tipo": "bypass_desenvolvedor",
            "versao": "1.0.0"
        }
        
        arquivo_bypass = "data/bypass_desenvolvedor.dat"
        with open(arquivo_bypass, "w") as f:
            json.dump(bypass_data, f, indent=2)
        
        print(f"✅ Bypass criado: {arquivo_bypass}")
        print(f"📅 Válido até: {data_expiracao.strftime('%d/%m/%Y %H:%M')}")
        print(f"💻 Hardware: {bypass_data['hardware_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def verificar_arquivos_protecao():
    """Verificar arquivos de proteção"""
    print("\n📂 VERIFICANDO ARQUIVOS DE PROTEÇÃO")
    print("=" * 40)
    
    arquivos = [
        "sistema_protecao_autoria.py",
        "data/bypass_desenvolvedor.dat",
        "data/banco.db"
    ]
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            print(f"✅ {arquivo} ({tamanho} bytes)")
        else:
            print(f"❌ {arquivo} - NÃO ENCONTRADO")

def testar_importacao_protecao():
    """Testar importação do sistema de proteção"""
    print("\n🔧 TESTANDO IMPORTAÇÃO DE PROTEÇÃO")
    print("=" * 40)
    
    try:
        from sistema_protecao_autoria import SistemaProtecaoAutoria
        print("✅ Importação bem-sucedida")
        
        # Testar criação do objeto
        protecao = SistemaProtecaoAutoria()
        print(f"✅ Objeto criado - Autor: {protecao.autor_original}")
        print(f"✅ Email: {protecao.email_autor}")
        print(f"✅ Hash senha configurado: {protecao.senha_desenvolvedor_hash[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def main():
    """Função principal"""
    print("🔐 TESTE COMPLETO DA SENHA DE DESENVOLVEDOR")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("👨‍💻 Desenvolvedor: Victor Soares Ferreira")
    print("🔑 Senha: Victor@1307")
    print("=" * 50)
    
    # Executar testes
    testes = [
        ("Hash da Senha", testar_hash_senha),
        ("Bypass Desenvolvedor", simular_bypass_desenvolvedor),
        ("Arquivos de Proteção", verificar_arquivos_protecao),
        ("Importação de Proteção", testar_importacao_protecao)
    ]
    
    sucessos = 0
    for nome, funcao in testes:
        try:
            resultado = funcao()
            if resultado:
                sucessos += 1
            print()
        except Exception as e:
            print(f"❌ Erro em {nome}: {e}")
    
    print("📊 RESULTADO FINAL")
    print("=" * 30)
    print(f"✅ Sucessos: {sucessos}/{len(testes)}")
    
    if sucessos == len(testes):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n🎯 FUNCIONAMENTO:")
        print("1. Sistema detecta hardware diferente")
        print("2. Oferece opção 'Acesso de Desenvolvedor'")
        print("3. Solicita senha: Victor@1307")
        print("4. Libera sistema por 30 dias")
    else:
        print("⚠️ Alguns testes falharam")
    
    return sucessos == len(testes)

if __name__ == "__main__":
    main()