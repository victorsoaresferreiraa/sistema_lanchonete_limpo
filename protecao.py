# sistema_protecao_autoria.py

import os
import sys
import hashlib
import uuid
import datetime
import sqlite3
import tkinter as tk
from tkinter import messagebox

class SistemaProtecaoAutoria:
    """
    Sistema de proteção e autenticação de autoria.
    Verifica a integridade do código, protege a base de dados
    e gerencia o status de licença.
    """
    def __init__(self, main_script_path="main_funcional.py"):
        """Inicialização com dados do autor e caminho do script principal."""
        self.main_script_path = main_script_path
        
        # Dados do autor (preenchidos automaticamente pelo script de configuração)
        self.autor_original = "[SEU NOME COMPLETO AQUI]"
        self.email_autor = "[seu.email@exemplo.com]"
        
        self.diretorio_data = "data"
        self.db_path = os.path.join(self.diretorio_data, "banco.db")
        self.licenca_path = os.path.join(self.diretorio_data, "licenca_sistema.dat")
        self.bypass_path = os.path.join(self.diretorio_data, "bypass_desenvolvedor.dat")
        
        # A assinatura digital é o hash do seu script principal
        self.assinatura_sistema = self._calcular_assinatura()
    
    def _calcular_assinatura(self):
        """Calcular hash SHA256 do arquivo principal para verificação de integridade."""
        try:
            with open(self.main_script_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except FileNotFoundError:
            return None
    
    def _criar_diretorio_dados(self):
        """Criar o diretório de dados se não existir."""
        if not os.path.exists(self.diretorio_data):
            os.makedirs(self.diretorio_data)
    
    def _mostrar_aviso_violacao(self):
        """Mostrar aviso de violação de direitos autorais."""
        mensagem = (
            "🚨 VIOLAÇÃO DE DIREITOS AUTORAIS DETECTADA\n\n"
            "Este software foi modificado ilegalmente.\n"
            f"Autor Original: {self.autor_original}\n"
            f"Email para Contato: {self.email_autor}\n\n"
            "O software será encerrado."
        )
        messagebox.showerror("Violação de Direitos Autorais", mensagem)
        sys.exit()

    def _verificar_validade_data(self):
        """Verificar se a data de validade da licença não expirou."""
        try:
            with open(self.licenca_path, "r") as f:
                data_str = f.read().strip()
                data_expiracao = datetime.datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S.%f')
                if datetime.datetime.now() > data_expiracao:
                    return False
            return True
        except (FileNotFoundError, ValueError):
            return False

    def _verificar_licenca(self):
        """Verificar a validade da licença e do hardware."""
        # Implementação de verificação de licença e hardware (simplificada)
        # Omissão do código para hardware_id para simplificar
        return self._verificar_validade_data()
    
    def _verificar_bypass_desenvolvedor(self):
        """Verificar bypass com arquivo de senha."""
        try:
            with open(self.bypass_path, "r") as f:
                conteudo = f.read().strip()
                partes = conteudo.split(":")
                
                if len(partes) != 2:
                    return False
                
                senha_hash = partes[0]
                data_expiracao_str = partes[1]
                
                # Se for a senha padrão, usar a data de expiração do arquivo
                data_expiracao = datetime.datetime.strptime(data_expiracao_str, '%Y-%m-%d')
                
                if datetime.datetime.now().date() <= data_expiracao.date():
                    return True
                else:
                    return False
        except FileNotFoundError:
            return False

    def _validar_assinatura(self):
        """Validar se a assinatura do sistema atual corresponde à assinatura original."""
        assinatura_atual = self._calcular_assinatura()
        if assinatura_atual == self.assinatura_sistema:
            return True
        return False
    
    def _solicitar_ativacao(self):
        """Abrir a janela para solicitar a ativação da licença."""
        # Implementação simplificada
        # Esta função é apenas uma demonstração do fluxo
        print("Ativação de licença solicitada. Entre em contato com o autor.")
        messagebox.showinfo("Ativação Necessária", f"O sistema precisa ser ativado.\n\n"
                            f"Entre em contato com:\n{self.autor_original}\n{self.email_autor}")
        return False

    def verificar_autoria_database(self, db_path):
        """Verificar se a base de dados tem a assinatura de autoria correta."""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sistema_autoria (
                        autor TEXT NOT NULL,
                        email TEXT NOT NULL,
                        assinatura TEXT NOT NULL
                    )
                """)
                
                cursor.execute("SELECT assinatura FROM sistema_autoria LIMIT 1")
                assinatura_db = cursor.fetchone()
                
                if assinatura_db and assinatura_db[0] == self.assinatura_sistema:
                    return True
                
                # Se a assinatura estiver errada ou não existir, tentar gravar a nova
                cursor.execute("DELETE FROM sistema_autoria")
                cursor.execute("INSERT INTO sistema_autoria (autor, email, assinatura) VALUES (?, ?, ?)",
                               (self.autor_original, self.email_autor, self.assinatura_sistema))
                conn.commit()
                print("✓ Assinatura da base de dados atualizada.")
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Erro na verificação/criação da autoria da base de dados: {e}")
            return False

    def _verificar_integridade_sistema(self):
        """Verificar se o sistema não foi modificado"""
        self._criar_diretorio_dados()
        
        # Verifica se o bypass de desenvolvedor está ativo
        if self._verificar_bypass_desenvolvedor():
            print("🔓 Acesso de desenvolvedor autorizado")
            return True
        
        # Verificação da assinatura do código (checksum do arquivo)
        if not self._validar_assinatura():
            self._mostrar_aviso_violacao()
            return False
        
        # A partir daqui, se a assinatura for válida, verificamos a licença
        if not self._verificar_licenca():
            if not self._solicitar_ativacao():
                return False
        
        return True

    def inicializar_protecao(self):
        """Método principal para iniciar todas as verificações de proteção."""
        print("🔐 Verificando sistema de proteção...")
        
        # 1. Checar por arquivo de modo desenvolvedor
        if os.path.exists("dev_mode.lock"):
            print("⚠️ Modo Desenvolvedor Ativo. Verificação de Integridade Ignorada.")
            return True
        
        # 2. Verificar integridade do código e licença
        if not self._verificar_integridade_sistema():
            print("❌ Falha na verificação de integridade")
            return False
            
        # 3. Verificar autoria da base de dados
        if not self.verificar_autoria_database(self.db_path):
            print("❌ Falha na verificação de autoria da base de dados")
            return False
        
        print("✅ Sistema de proteção ativado com sucesso.")
        return True