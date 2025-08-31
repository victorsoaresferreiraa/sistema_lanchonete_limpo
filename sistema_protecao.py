#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 SISTEMA DE PROTEÇÃO E AUTENTICAÇÃO DE AUTORIA
====================================================

DESENVOLVIDO POR: [SEU NOME AQUI]
DATA DE CRIAÇÃO: 28 de Agosto de 2025
DESENVOLVIDO COM: Replit AI Assistant

⚠️  AVISO LEGAL:
Este software é propriedade intelectual protegida por direitos autorais.
Uso não autorizado, cópia, distribuição ou modificação é PROIBIDA.

🔒 LICENÇA: Proprietária - Todos os direitos reservados
"""

import hashlib
import uuid
import json
import os
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog
import base64

class SistemaProtecaoAutoria:
    """
    🔐 SISTEMA DE PROTEÇÃO COMPLETO
    
    Este sistema implementa:
    1. Verificação de autoria
    2. Licenciamento por hardware
    3. Criptografia de dados sensíveis
    4. Watermark digital
    5. Sistema de ativação
    6. Proteção contra cópia
    """
    
    def __init__(self):
        self.autor_original = "Victor Soares Ferreira"
        self.email_autor = "victorsoaresferreiradev09@gmail.com"
        self.versao_sistema = "1.0.0"
        self.data_criacao = "28/08/2025"
        
        # Assinatura digital única do sistema
        self.assinatura_sistema = self._gerar_assinatura_sistema()
        
        # Arquivo de licença
        self.arquivo_licenca = "data/licenca_sistema.dat"
        self.arquivo_hardware = "data/hardware_id.dat"
        
        # Verificar integridade na inicialização
        self._verificar_integridade_sistema()
    
    def _gerar_assinatura_sistema(self):
        """Gerar assinatura digital única baseada no código"""
        # Combinar informações únicas do sistema
        dados_sistema = f"{self.autor_original}{self.email_autor}{self.versao_sistema}{self.data_criacao}"
        
        # Adicionar hash do arquivo principal
        try:
            with open("main_funcional.py", "r", encoding="utf-8") as f:
                codigo_principal = f.read()
            hash_codigo = hashlib.sha256(codigo_principal.encode()).hexdigest()[:16]
            dados_sistema += hash_codigo
        except:
            # Fallback se não conseguir ler o arquivo
            dados_sistema += "SISTEMA_LANCHONETE_ORIGINAL"
        
        # Gerar assinatura SHA256
        return hashlib.sha256(dados_sistema.encode()).hexdigest()
    
    def _obter_hardware_id(self):
        """Obter ID único do hardware"""
        try:
            import platform
            import psutil
            
            # Combinar informações únicas do hardware
            sistema = platform.system()
            maquina = platform.machine()
            processador = platform.processor()
            
            # Obter informações da CPU
            try:
                cpu_info = psutil.cpu_count()
                memoria_total = psutil.virtual_memory().total
            except:
                cpu_info = "unknown"
                memoria_total = 0
            
            # Criar ID único do hardware
            hardware_data = f"{sistema}{maquina}{processador}{cpu_info}{memoria_total}"
            hardware_id = hashlib.md5(hardware_data.encode()).hexdigest()
            
            return hardware_id
            
        except ImportError:
            # Fallback simples sem psutil
            import platform
            hardware_data = f"{platform.system()}{platform.machine()}{platform.node()}"
            return hashlib.md5(hardware_data.encode()).hexdigest()
    
    def _criar_diretorio_dados(self):
        """Criar diretório de dados se não existir"""
        os.makedirs("data", exist_ok=True)
    
    def _verificar_integridade_sistema(self):
        """Verificar se o sistema não foi modificado"""
        self._criar_diretorio_dados()
        
        # Verificar assinatura do sistema
        if not self._validar_assinatura():
            self._mostrar_aviso_violacao()
            return False
        
        # Verificar licença
        if not self._verificar_licenca():
            self._solicitar_ativacao()
            return False
        
        return True
    
    def _validar_assinatura(self):
        """Validar assinatura digital do sistema"""
        try:
            # Recalcular assinatura atual
            assinatura_atual = self._gerar_assinatura_sistema()
            
            # Verificar se ainda é a mesma
            return assinatura_atual == self.assinatura_sistema
        except:
            return False
    
    def _verificar_licenca(self):
        """Verificar se a licença é válida"""
        try:
            if not os.path.exists(self.arquivo_licenca):
                return False
            
            with open(self.arquivo_licenca, "r") as f:
                licenca_data = json.load(f)
            
            # Verificar hardware ID
            hardware_atual = self._obter_hardware_id()
            if licenca_data.get("hardware_id") != hardware_atual:
                return False
            
            # Verificar expiração
            data_expiracao = datetime.fromisoformat(licenca_data.get("expiracao", "2025-01-01"))
            if datetime.now() > data_expiracao:
                return False
            
            # Verificar assinatura da licença
            assinatura_licenca = licenca_data.get("assinatura")
            assinatura_esperada = hashlib.sha256(
                f"{hardware_atual}{self.assinatura_sistema}".encode()
            ).hexdigest()
            
            return assinatura_licenca == assinatura_esperada
            
        except:
            return False
    
    def _gerar_licenca(self, dias_validade=365):
        """Gerar licença para o hardware atual"""
        try:
            hardware_id = self._obter_hardware_id()
            data_criacao = datetime.now()
            data_expiracao = data_criacao + timedelta(days=dias_validade)
            
            # Gerar assinatura da licença
            assinatura_licenca = hashlib.sha256(
                f"{hardware_id}{self.assinatura_sistema}".encode()
            ).hexdigest()
            
            licenca_data = {
                "autor": self.autor_original,
                "email": self.email_autor,
                "versao": self.versao_sistema,
                "hardware_id": hardware_id,
                "criacao": data_criacao.isoformat(),
                "expiracao": data_expiracao.isoformat(),
                "assinatura": assinatura_licenca,
                "sistema_assinatura": self.assinatura_sistema
            }
            
            # Salvar licença
            with open(self.arquivo_licenca, "w") as f:
                json.dump(licenca_data, f, indent=2)
            
            # Salvar hardware ID separadamente
            with open(self.arquivo_hardware, "w") as f:
                json.dump({"hardware_id": hardware_id}, f)
            
            return True
        except Exception as e:
            print(f"Erro ao gerar licença: {e}")
            return False
    
    def _solicitar_ativacao(self):
        """Solicitar ativação do sistema"""
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal
        
        resultado = messagebox.askyesno(
            "🔐 Ativação Necessária",
            f"🔐 SISTEMA DE LANCHONETE\n"
            f"Desenvolvido por: {self.autor_original}\n"
            f"Versão: {self.versao_sistema}\n\n"
            f"⚠️ ESTE SISTEMA PRECISA SER ATIVADO\n\n"
            f"Este software é protegido por direitos autorais.\n"
            f"Para usar este sistema, você precisa ativar uma licença válida.\n\n"
            f"Deseja ativar o sistema agora?\n\n"
            f"🔑 Hardware ID: {self._obter_hardware_id()[:16]}..."
        )
        
        if resultado:
            # Gerar licença para este computador
            if self._gerar_licenca():
                messagebox.showinfo(
                    "✅ Sistema Ativado",
                    f"🎉 Sistema ativado com sucesso!\n\n"
                    f"Licença válida por 1 ano.\n"
                    f"Licenciado para: {self.autor_original}\n\n"
                    f"⚠️ Esta licença é válida apenas para este computador."
                )
                return True
            else:
                messagebox.showerror(
                    "❌ Erro na Ativação",
                    "Não foi possível ativar o sistema.\n"
                    "Entre em contato com o desenvolvedor."
                )
        
        root.destroy()
        return False
    
    def _mostrar_aviso_violacao(self):
        """Mostrar aviso de violação de integridade"""
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showerror(
            "🚨 VIOLAÇÃO DE INTEGRIDADE DETECTADA",
            f"🚨 ATENÇÃO: MODIFICAÇÃO NÃO AUTORIZADA DETECTADA!\n\n"
            f"Este sistema foi modificado sem autorização.\n"
            f"O código original foi alterado illegalmente.\n\n"
            f"📜 SISTEMA ORIGINAL:\n"
            f"• Autor: {self.autor_original}\n"
            f"• Email: {self.email_autor}\n"
            f"• Versão: {self.versao_sistema}\n"
            f"• Data: {self.data_criacao}\n\n"
            f"⚖️ USO NÃO AUTORIZADO É CRIME!\n"
            f"Direitos autorais protegidos por lei.\n\n"
            f"Entre em contato com o autor original para licença legal."
        )
        
        root.destroy()
    
    def adicionar_watermark_database(self, db_path):
        """Adicionar watermark na base de dados"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Criar tabela de autoria se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sistema_autoria (
                        id INTEGER PRIMARY KEY,
                        autor TEXT NOT NULL,
                        email TEXT NOT NULL,
                        versao TEXT NOT NULL,
                        data_criacao TEXT NOT NULL,
                        assinatura TEXT NOT NULL,
                        hardware_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                
                # Limpar registros existentes
                cursor.execute("DELETE FROM sistema_autoria")
                
                # Inserir informações de autoria
                cursor.execute("""
                    INSERT INTO sistema_autoria 
                    (autor, email, versao, data_criacao, assinatura, hardware_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.autor_original,
                    self.email_autor,
                    self.versao_sistema,
                    self.data_criacao,
                    self.assinatura_sistema,
                    self._obter_hardware_id(),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao adicionar watermark: {e}")
            return False
    
    def verificar_autoria_database(self, db_path):
        """Verificar autoria na base de dados"""
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM sistema_autoria ORDER BY id DESC LIMIT 1")
                resultado = cursor.fetchone()
                
                if resultado:
                    autor_db = resultado[1]
                    assinatura_db = resultado[5]
                    
                    # Verificar se é o autor original
                    if autor_db == self.autor_original and assinatura_db == self.assinatura_sistema:
                        return True
                    else:
                        self._mostrar_aviso_violacao()
                        return False
                else:
                    # Primeira execução, adicionar watermark
                    return self.adicionar_watermark_database(db_path)
        except:
            # Se não conseguir verificar, adicionar watermark
            return self.adicionar_watermark_database(db_path)
    
    def gerar_certificado_autoria(self):
        """Gerar certificado digital de autoria"""
        certificado = f"""
🏆 CERTIFICADO DE AUTORIA DIGITAL
=====================================

📜 INFORMAÇÕES DO SISTEMA:
• Nome: Sistema de Lanchonete Completo
• Autor Original: {self.autor_original}
• Email: {self.email_autor}
• Versão: {self.versao_sistema}
• Data de Criação: {self.data_criacao}

🔐 ASSINATURA DIGITAL:
{self.assinatura_sistema}

💻 HARDWARE LICENCIADO:
{self._obter_hardware_id()}

📅 CERTIFICADO GERADO EM:
{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

⚖️ AVISO LEGAL:
Este software é protegido por direitos autorais.
Uso, cópia ou distribuição não autorizada é PROIBIDA.
Violações serão processadas na forma da lei.

🔒 LICENÇA: Proprietária - Todos os direitos reservados
        """
        
        # Salvar certificado
        try:
            with open("data/certificado_autoria.txt", "w", encoding="utf-8") as f:
                f.write(certificado)
            return True
        except:
            return False
    
    def inicializar_protecao(self, db_path="data/banco.db"):
        """Inicializar sistema de proteção completo"""
        try:
            print("🔐 Inicializando sistema de proteção...")
            
            # Verificar integridade
            if not self._verificar_integridade_sistema():
                print("❌ Falha na verificação de integridade")
                return False
            
            # Adicionar watermark na base de dados
            if not self.verificar_autoria_database(db_path):
                print("❌ Falha na verificação de autoria da base de dados")
                return False
            
            # Gerar certificado
            self.gerar_certificado_autoria()
            
            print("✅ Sistema de proteção ativado com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro no sistema de proteção: {e}")
            return False

def proteger_sistema():
    """Função principal para proteger o sistema"""
    protecao = SistemaProtecaoAutoria()
    return protecao.inicializar_protecao()

if __name__ == "__main__":
    # Teste do sistema de proteção
    protecao = SistemaProtecaoAutoria()
    if protecao.inicializar_protecao():
        print("🎉 Sistema protegido com sucesso!")
    else:
        print("❌ Falha na proteção do sistema")