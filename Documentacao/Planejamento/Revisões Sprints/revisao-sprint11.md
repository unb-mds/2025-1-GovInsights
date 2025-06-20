# 🌀 Sprint Review – Sprint 11

*📅 Data:* 16 de junho de 2025  
*🕒 Hora:* 21h30  

## 👥 Participantes
- *FrontEnd:* Eduarda, Mayra, Gabriel  
- *BackEnd:* Marjorie, Guilherme  
- *Gestão de Projetos:* Eric, Brenda, Maria Eduarda

---

## ✅ Revisão da Sprint 11

### 🧠 Progresso Individual e de Equipe

### 👨‍💻 Gabriel (FrontEnd)
- Finalizou as filtragens necessárias para os relatórios e dashboards, garantindo maior precisão na geração dos dados.

### 👨‍🎨 Eduarda (FrontEnd)
- Trabalhou no roteamento da dashboard.py.
- Realizou ajustes na header para melhorar a localização dos componentes.
- Apesar dos avanços, a dashboard segue apresentando problemas de quebra na navegação.

### 🎨 Mayra (FrontEnd)
- Atuou na página de alertas, porém enfrentou um problema que resultou na perda do CSS anteriormente desenvolvido, impactando diretamente o layout.

### 👨‍💻 Guilherme (BackEnd)
- Desenvolveu o algoritmo que realiza a atualização das séries diretamente do IPEA.
- Implementou um sistema de alertas baseado em variações detectadas nas séries.
- Criou o algoritmo de agendamento (*cronjob*), que ainda não foi integrado ao ambiente de produção.

### 👩‍💻 Marjorie (BackEnd)
- Trabalhou em conjunto com Eric no processo de *deploy da aplicação*, focando na estabilidade do ambiente.

### 🔍 Maria Eduarda (QA / Testes)
- Iniciou a implementação dos *testes unitários*, visando garantir mais segurança e qualidade ao desenvolvimento.

### 🔧 Brenda (QA / Testes)
- Começou o desenvolvimento da *automação dos testes*, passo essencial para validação contínua das funcionalidades.

### 🧩 Integração e Organização Técnica
- A integração dos módulos de *relatórios* e *alertas* foi finalizada com sucesso.  
- O *banco de dados* passou por atualizações e ajustes para suportar as novas funcionalidades, incluindo o algoritmo de atualização e geração de alertas.

---

## 🔍 Pontos de Aprendizado

- A necessidade de criar uma estratégia mais robusta para lidar com séries do IPEA de atualização anual, que apresentam dados inconsistentes.
- A importância de um controle de versionamento mais rígido, especialmente para evitar perdas como a do CSS na página de alertas.
- Reforço na importância de realizar testes contínuos e de implementar a automação dos mesmos para evitar retrabalho.

---

## ✅ Conclusão

A Sprint 11 foi essencial para consolidar as integrações dos módulos principais, como relatórios e alertas.  
Apesar dos desafios técnicos — como problemas nas séries do IPEA e na perda de arquivos de estilo —, a equipe avançou significativamente na construção da pipeline, na automação de testes e na preparação para a etapa final de deploy.

A Sprint 12 terá como foco:  
- Finalização da pipeline de dados.  
- Implementação e validação do cronjob.  
- Correção dos problemas de roteamento e de layout.  
- Conclusão dos testes unitários e de integração.  
- Refinamento do deploy e resolução das pendências técnicas.  

*✍ Ata elaborada por:* @mariadenis  
*📆 Data:* 16/06/2025