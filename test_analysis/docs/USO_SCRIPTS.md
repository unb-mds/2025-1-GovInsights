# 🛠️ Guia de Uso dos Scripts

## 🎯 **Referência Rápida**

### **✅ Scripts de Validação** (`scripts/validation/`)

#### **🔍 Validação de Estrutura**
```bash
python scripts/validation/validate_integration_tests.py
```
**Propósito:** Valida sintaxe, importações e estrutura básica de todos os arquivos de teste
**Saída:** Relatório no console + resultados de validação
**Quando usar:** Antes de fazer alterações, após atualizações

#### **📊 Análise de Cobertura**  
```bash
python scripts/validation/analyze_test_coverage.py
```
**Propósito:** Analisa cobertura de código em todos os módulos
**Saída:** Relatório detalhado de cobertura + recomendações
**Quando usar:** Para verificar completude dos testes

#### **⚡ Análise Rápida**
```bash
python scripts/validation/quick_test_analysis.py
```
**Propósito:** Visão geral rápida da estrutura e status dos testes
**Saída:** Relatório JSON + métricas rápidas
**Quando usar:** Para verificações rápidas de saúde

#### **🚀 Execução Completa de Testes**
```bash
python scripts/validation/run_final_integration_tests.py
```
**Propósito:** Executa todos os testes de integração com relatório detalhado
**Saída:** Relatório completo de execução + resultados
**Quando usar:** Para validação abrangente

---

## 🏗️ **Scripts de Infraestrutura** (`scripts/infrastructure/`)

#### **🔧 Verificação de Saúde**
```bash
python scripts/infrastructure/test_integration_health.py
```
**Propósito:** Verifica saúde do ambiente de testes
**Quando usar:** Antes de executar testes, solução de problemas

#### **📦 Validação de Importações**
```bash
python scripts/infrastructure/test_imports_integration.py
```
**Propósito:** Valida todas as importações e dependências
**Quando usar:** Após mudanças de dependências

#### **🏠 Infraestrutura Básica**
```bash
python scripts/infrastructure/test_basic_infrastructure.py
```
**Propósito:** Testa infraestrutura básica do projeto
**Quando usar:** Validação de configuração do projeto

---

## 🛠️ **Scripts de Correção** (`scripts/fixes/`) - Apenas Referência

> **Nota:** Estes scripts foram usados historicamente para corrigir problemas. Eles são mantidos para referência e compreensão do que foi corrigido.

#### **🔤 Correção de Codificação**
```bash
# Histórico - já aplicado
python scripts/fixes/fix_encoding.py
```
**Propósito:** Corrigiu problemas de codificação UTF-8 nos arquivos de teste
**Status:** ✅ Aplicado

#### **🔗 Correção de Teste End-to-End**
```bash
# Histórico - já aplicado  
python scripts/fixes/fix_end_to_end_tests.py
```
**Propósito:** Corrigiu estrutura de teste end-to-end e mocks
**Status:** ✅ Aplicado

#### **🔍 Correção de Existência de Método**
```bash
# Histórico - já aplicado
python scripts/fixes/fix_buscar_indicadores.py
```
**Propósito:** Corrigiu referências de métodos inexistentes
**Status:** ✅ Aplicado

---

## 📋 **Detalhes dos Scripts**

### **🔍 validate_integration_tests.py**

**O que faz:**
- Verifica sintaxe Python em todos os arquivos de teste
- Valida declarações de importação
- Conta métodos e classes de teste
- Identifica problemas estruturais

**Saída:**
```
✅ Resultados de validação de arquivo
📊 Resumo de estatísticas  
⚠️ Problemas encontrados (se houver)
📝 Recomendações
```

**Códigos de retorno:**
- `0` - Todos os testes válidos
- `1` - Problemas encontrados

### **📊 analyze_test_coverage.py**

**O que faz:**
- Executa análise de cobertura em todos os módulos
- Gera relatório detalhado de cobertura
- Identifica áreas de código não testadas
- Fornece recomendações de melhoria

**Saída:**
```
📈 Percentual de cobertura por módulo
📋 Análise detalhada linha por linha
🎯 Áreas que precisam de atenção
💡 Sugestões de melhoria
```

**Requisitos:**
- Pacote `coverage` instalado
- Arquivos de teste devem ser executáveis

### **⚡ quick_test_analysis.py**

**O que faz:**
- Análise rápida de estrutura
- Coleta de métricas básicas  
- Geração de relatório JSON
- Visão geral do status de saúde

**Saída:**
```json
{
  "total_files": 8,
  "valid_files": 8,
  "test_methods": 95,
  "coverage": "95%",
  "status": "excellent"
}
```

### **🚀 run_final_integration_tests.py**

**O que faz:**
- Executa todos os testes de integração
- Coleta resultados de execução
- Gera relatório abrangente
- Fornece análise de sucesso/falha

**Saída:**
```
🧪 Resultados de execução de teste
📊 Estatísticas de aprovação/reprovação
⏱️ Tempos de execução
📝 Relatórios detalhados de erro (se houver)
```

---

## 🎯 **Padrões de Uso Comuns**

### **🔍 Desenvolvimento Diário**
```bash
# Verificação rápida de saúde
python scripts/validation/quick_test_analysis.py

# Se problemas encontrados, validar estrutura
python scripts/validation/validate_integration_tests.py
```

### **📊 Antes do Release**
```bash
# Análise completa de cobertura
python scripts/validation/analyze_test_coverage.py

# Execução completa de testes
python scripts/validation/run_final_integration_tests.py
```

### **🐛 Solução de Problemas**
```bash
# Verificar ambiente
python scripts/infrastructure/test_integration_health.py

# Validar importações
python scripts/infrastructure/test_imports_integration.py

# Infraestrutura básica
python scripts/infrastructure/test_basic_infrastructure.py
```

### **📈 Melhoria de Cobertura**
```bash
# Analisar cobertura atual
python scripts/validation/analyze_test_coverage.py

# Verificar estrutura após mudanças
python scripts/validation/validate_integration_tests.py

# Verificar melhorias
python scripts/validation/run_final_integration_tests.py
```

---

## ⚙️ **Requisitos dos Scripts**

### **🐍 Ambiente Python**
```bash
# Garantir que Python 3.7+ esteja disponível
python --version

# Instalar requisitos
pip install -r requirements.txt
```

### **📦 Pacotes Necessários**
- `coverage` - Para análise de cobertura
- `pytest` - Para execução de testes  
- `json` - Para saída estruturada
- Módulos da biblioteca padrão

### **📁 Diretório de Trabalho**
Todos os scripts devem ser executados da raiz do projeto:
```bash
cd /path/to/2025-1-GovInsights/
python test_analysis/scripts/validation/script_name.py
```

---

## 🚨 **Solução de Problemas**

### **❌ Problemas Comuns**

#### **ImportError: No module named 'src'**
```bash
# Solução: Executar da raiz do projeto
cd /path/to/2025-1-GovInsights/
python test_analysis/scripts/validation/script_name.py
```

#### **Coverage não encontrado**
```bash
# Solução: Instalar coverage
pip install coverage
```

#### **Testes falham ao executar**
```bash
# Solução: Verificar ambiente
python test_analysis/scripts/infrastructure/test_integration_health.py
```

#### **Permissão negada**
```bash
# Solução: Verificar permissões de arquivo
chmod +x test_analysis/scripts/validation/*.py
```

---

## 📊 **Formatos de Saída**

### **Saída no Console**
- Indicadores de progresso em tempo real
- Resultados com código de cores (quando suportado)
- Estatísticas resumidas
- Feedback imediato

### **Relatórios JSON**
- Dados estruturados em `data/json_reports/`
- Resultados legíveis por máquina
- Perfeito para automação
- Formato consistente

### **Relatórios de Texto**
- Legível por humanos em `data/coverage/`
- Explicações detalhadas
- Amigável para copiar/colar
- Adequado para arquivo

---

*Use estes scripts eficientemente para manter excelente qualidade de teste! 🎯*
