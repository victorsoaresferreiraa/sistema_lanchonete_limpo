# 🧪 PLANO DE TESTE COMPLETO DO SISTEMA

**Data:** 28/08/2025  
**Objetivo:** Testar todas as funcionalidades sistematicamente  

---

## 📋 **ESCOPO DOS TESTES**

### **1. Sistema de Proteção**
- [ ] Ativação inicial em hardware novo
- [ ] Senha de desenvolvedor (Victor@1307)
- [ ] Bypass de 30 dias
- [ ] Renovação automática

### **2. Cadastro de Produtos**
- [ ] Cadastro rápido (F4)
- [ ] Validação de campos obrigatórios
- [ ] Produtos com nomes especiais ("hamburguer", "batata frita")
- [ ] Preços com vírgula e ponto
- [ ] Quantidades inteiras e decimais
- [ ] Categorias diferentes

### **3. Sistema de Vendas (Caixa)**
- [ ] Seleção de produtos no combo
- [ ] Preenchimento automático de preço
- [ ] Adição ao carrinho
- [ ] Exibição correta no TreeView
- [ ] Cálculo de totais
- [ ] Múltiplos produtos no carrinho
- [ ] Remoção de itens

### **4. Interface Gráfica**
- [ ] Abertura das janelas
- [ ] Navegação por teclado (F1-F10)
- [ ] Atalhos funcionando
- [ ] Responsividade da interface
- [ ] Atualização em tempo real

### **5. Banco de Dados**
- [ ] Conexão com SQLite
- [ ] Inserção de produtos
- [ ] Consulta de estoque
- [ ] Histórico de vendas
- [ ] Integridade dos dados

---

## 🎯 **CASOS DE TESTE ESPECÍFICOS**

### **Teste 1: Cadastro de Produto Simples**
```
Input: Nome="Refrigerante", Categoria="Bebidas", Qty=10, Preço=3.50
Expected: Produto salvo com sucesso
```

### **Teste 2: Produto com Nome Problemático**
```
Input: Nome="hamburguer", Categoria="Lanches", Qty=5, Preço=15.00
Expected: Produto aceito sem erro de validação
```

### **Teste 3: Venda Simples**
```
1. Selecionar produto no caixa
2. Verificar preço preenchido automaticamente
3. Definir quantidade = 2
4. Adicionar ao carrinho
Expected: Item aparece no carrinho com valores corretos
```

### **Teste 4: Múltiplos Produtos**
```
1. Adicionar Refrigerante (2x R$3.50 = R$7.00)
2. Adicionar Hamburguer (1x R$15.00 = R$15.00)
Expected: Total = R$22.00, 3 itens no carrinho
```

### **Teste 5: Senha de Desenvolvedor**
```
1. Simular hardware diferente
2. Sistema pede ativação
3. Clicar "NÃO" → "SIM" → Digite "Victor@1307"
Expected: Sistema libera por 30 dias
```

---

## 🔧 **METODOLOGIA DE TESTE**

### **Ambiente Controlado:**
1. Sistema limpo
2. Base de dados conhecida
3. Debug ativo para rastreamento
4. Logs detalhados

### **Verificações em Cada Teste:**
1. **Console Debug** - Verificar logs de processamento
2. **Interface Visual** - Confirmar exibição correta
3. **Banco de Dados** - Validar persistência
4. **Estado do Sistema** - Verificar consistência

### **Critérios de Sucesso:**
- ✅ Funcionalidade executa sem erro
- ✅ Interface atualiza corretamente
- ✅ Dados são persistidos
- ✅ Cálculos estão corretos
- ✅ Debug confirma funcionamento

---

## 📊 **REGISTRO DE RESULTADOS**

### **Template por Teste:**
```
Teste: [Nome do teste]
Data/Hora: [timestamp]
Input: [dados de entrada]
Expected: [resultado esperado]
Actual: [resultado obtido]
Debug Log: [logs relevantes]
Status: [PASS/FAIL]
Observações: [notas adicionais]
```

---

## 🚀 **EXECUÇÃO DOS TESTES**

### **Fase 1: Testes Básicos**
- Inicialização do sistema
- Cadastro simples de produto
- Venda básica

### **Fase 2: Testes de Validação**
- Produtos com nomes problemáticos
- Validações de campos
- Tratamento de erros

### **Fase 3: Testes de Interface**
- Atualização do carrinho
- Múltiplos produtos
- Navegação completa

### **Fase 4: Testes de Sistema**
- Proteção e segurança
- Persistência de dados
- Performance geral

---

**📝 Nota:** Cada teste será executado metodicamente com registro completo dos resultados para identificar e corrigir qualquer problema restante.