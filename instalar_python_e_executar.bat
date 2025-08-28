@echo off
title Sistema Lanchonete - Victor Soares Ferreira
color 0A

echo.
echo   ===============================================================
echo   🔐 SISTEMA DE LANCHONETE - INSTALADOR SEGURO AUTOMATICO
echo   ===============================================================
echo   👨‍💻 Desenvolvido por: Victor Soares Ferreira
echo   📧 Email: victorsoaresferreiradev09@gmail.com
echo   📅 Data: 28/08/2025
echo   🛡️ Sistema protegido contra roubo e uso nao autorizado
echo   ===============================================================
echo.

REM ========= VERIFICACOES DE SEGURANCA =========
echo [SEGURANCA] Verificando integridade do sistema...

REM Verificar se arquivos principais existem
if not exist "main_funcional.py" (
    echo ❌ [ERRO CRITICO] Arquivo principal nao encontrado!
    echo Este pode ser um sistema roubado ou corrompido.
    echo Entre em contato com: victorsoaresferreiradev09@gmail.com
    pause
    exit /b 1
)

if not exist "sistema_protecao_autoria.py" (
    echo ❌ [ERRO DE SEGURANCA] Sistema de protecao removido!
    echo USO NAO AUTORIZADO DETECTADO!
    echo Sistema original: Victor Soares Ferreira
    echo Email: victorsoaresferreiradev09@gmail.com
    pause
    exit /b 1
)

echo ✅ [SEGURANCA] Arquivos principais verificados
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python ja esta instalado!
    goto :executar_sistema
)

echo [INFO] Python nao encontrado. Instalando automaticamente...
echo.

REM Criar pasta temporaria para downloads
if not exist "temp_install" mkdir temp_install
cd temp_install

echo [1/4] Baixando Python 3.11.9 (64-bit)...
echo Aguarde, fazendo download do Python...

REM Baixar Python usando PowerShell (funciona no Windows 10/11)
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'}"

if not exist "python_installer.exe" (
    echo [ERRO] Falha ao baixar Python. Verifique sua conexao com internet.
    echo.
    echo SOLUCAO MANUAL:
    echo 1. Baixe Python em: https://www.python.org/downloads/
    echo 2. Instale marcando "Add Python to PATH"
    echo 3. Execute este arquivo novamente
    pause
    exit /b 1
)

echo [2/4] Instalando Python...
echo IMPORTANTE: O instalador ira abrir. Marque "Add Python to PATH"!
echo.
pause

REM Instalar Python silenciosamente com PATH
python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo [3/4] Aguardando instalacao finalizar...
timeout /t 30 >nul

echo [4/4] Verificando instalacao...
REM Atualizar PATH para sessao atual
set PATH=%PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts

REM Testar novamente
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [SUCESSO] Python instalado com sucesso!
) else (
    echo [AVISO] Pode ser necessario reiniciar o computador.
    echo Execute este arquivo novamente apos reiniciar.
    pause
    exit /b 1
)

REM Limpar arquivos temporarios
cd ..
rmdir /s /q temp_install

:executar_sistema
echo.
echo   ===============================================================
echo   🚀 INICIALIZANDO SISTEMA LANCHONETE PROTEGIDO
echo   ===============================================================
echo.

REM ========= VERIFICACAO FINAL DE SEGURANCA =========
echo [SEGURANCA] Verificacao final de integridade...

REM Verificar assinatura do desenvolvedor no codigo
findstr /C:"Victor Soares Ferreira" main_funcional.py >nul
if %errorlevel% neq 0 (
    echo ❌ [VIOLACAO] Assinatura do autor removida!
    echo SISTEMA ADULTERADO OU ROUBADO!
    echo.
    echo 🔒 AUTOR ORIGINAL: Victor Soares Ferreira
    echo 📧 EMAIL ORIGINAL: victorsoaresferreiradev09@gmail.com
    echo 📅 DATA CRIACAO: 28/08/2025
    echo.
    echo ⚖️ USO NAO AUTORIZADO E CRIME!
    echo Entre em contato para licenciamento legal.
    pause
    exit /b 1
)

echo ✅ [SEGURANCA] Assinatura do autor verificada
echo.

REM ========= INSTALACAO SEGURA DE DEPENDENCIAS =========
echo [SETUP] Instalando bibliotecas de forma segura...
echo.

python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ [AVISO] Falha ao atualizar pip. Continuando...
)

echo [LIBS] pandas, openpyxl, matplotlib, pillow...
python -m pip install pandas openpyxl matplotlib pillow --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ [ERRO] Falha na instalacao de dependencias.
    echo Verifique sua conexao com internet e tente novamente.
    pause
    exit /b 1
)

echo ✅ [LIBS] Todas as bibliotecas instaladas com sucesso
echo.

REM ========= CRIACAO DE AMBIENTE SEGURO =========
echo [AMBIENTE] Preparando ambiente de execucao...

REM Criar pasta de dados se nao existir
if not exist "data" mkdir data

REM Verificar permissoes de escrita
echo teste > data\teste_permissao.tmp 2>nul
if exist "data\teste_permissao.tmp" (
    del data\teste_permissao.tmp
    echo ✅ [PERMISSOES] Pasta de dados configurada
) else (
    echo ❌ [ERRO] Sem permissao para criar arquivos.
    echo Execute como Administrador se necessario.
    pause
    exit /b 1
)

REM ========= EXECUCAO DO SISTEMA =========
echo.
echo   ===============================================================
echo   🎯 EXECUTANDO SISTEMA - Victor Soares Ferreira
echo   ===============================================================
echo.
echo 📋 ATALHOS RAPIDOS DO SISTEMA:
echo   F1 = Ajuda Completa     F2 = Venda a Vista    F3 = Venda Fiado
echo   F4 = Gerenciar Estoque  F5 = Historico       F6 = Dashboard
echo   F7 = Relatorios        F8 = Contas Abertas   F9 = Backup
echo   ESC = Fechar Sistema    Enter = Confirmar     Tab = Navegar
echo.
echo 🔐 SISTEMA PROTEGIDO: Este software possui proteção anti-roubo
echo 📧 SUPORTE TECNICO: victorsoaresferreiradev09@gmail.com
echo.
echo [INICIANDO] Abrindo interface grafica...
echo.

REM Executar com verificacao de erro
python main_funcional.py
set RESULTADO=%errorlevel%

echo.
echo   ===============================================================
echo   📊 RELATORIO DE EXECUCAO
echo   ===============================================================

if %RESULTADO% == 0 (
    echo ✅ Sistema finalizado normalmente
) else (
    echo ❌ Sistema encerrado com erro (codigo: %RESULTADO%)
    echo.
    echo 🔧 SOLUCOES POSSIVEIS:
    echo • Verifique se todos os arquivos estao presentes
    echo • Execute como Administrador
    echo • Entre em contato: victorsoaresferreiradev09@gmail.com
)

echo.
echo 💼 Para uso comercial, entre em contato para licenciamento.
echo 🛡️ Este sistema e protegido por direitos autorais.
echo.
echo Pressione qualquer tecla para finalizar...
pause >nul

REM ========= LIMPEZA E SAIDA SEGURA =========
echo.
echo [LIMPEZA] Finalizando processos de forma segura...
taskkill /f /im python.exe >nul 2>&1
echo [SAIDA] Instalador finalizado.