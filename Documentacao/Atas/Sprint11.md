# 📄 Ata da Reunião – Sprint 11

📅 **Data:** 10 de junho de 2025  
🕒 **Horário:** 21h30  
📍 **Local:** Discord  
**✍️ Responsável pela ata:** @mariadenis

---

## 👥 Participantes

- **FrontEnd:** Eduarda, Mayra, Gabriel  
- **BackEnd:** Marjorie, Guilherme  
- **Gestão de Projetos:** Eric, Maria Eduarda, Brenda  

---

## 📌 Pauta da Reunião

1. Acompanhamento das entregas da Sprint 10  
2. Validação das integrações realizadas  
3. Levantamento dos problemas encontrados  
4. Definição das próximas ações para finalização da pipeline e testes

---

## ✅ Andamentos da Sprint 11

- **Marjorie:** Trabalhou no processo de deploy em conjunto com Eric.  
- **Eduarda:** Tentou realizar o roteamento da `dashboard.py`, realizou ajustes na `header` para melhorar a localização dos componentes, embora a dashboard ainda esteja com algumas quebras.  
- **Gabriel:** Finalizou as filtragens necessárias para os relatórios e dashboards.  
- **Guilherme:** Desenvolveu o algoritmo que atualiza as séries diretamente do IPEA e dispara alertas com base nas variações. O algoritmo de agendamento (cronjob) está implementado, mas ainda não foi integrado ao ambiente de produção.  
- **Mayra:** Trabalhou na página de alertas, porém enfrentou um problema que resultou na perda do CSS anteriormente desenvolvido.  
- **Maria Eduarda:** Iniciou a implementação dos testes unitários.  
- **Brenda:** Começou o desenvolvimento da automação dos testes.  

---

## 🔧 Integrações Realizadas

- Integração dos módulos de **relatórios** e **alertas** finalizada com sucesso.  
- Atualização e ajustes no **banco de dados** para suportar as novas funcionalidades.

---

## ⚠️ Dificuldades Encontradas

- **Guilherme:** Desafio com as séries do IPEA, principalmente as de atualização anual, que possuem atualizações inconsistentes. Isso causava envios repetidos de alertas. Apesar disso, o algoritmo foi simplificado ao máximo para cumprir os requisitos, ainda que sem alta robustez.  
- **Mayra:** Perda do CSS da página de alertas durante os ajustes.  
- **Eduarda:** Dificuldades no roteamento da dashboard, que apresenta falhas na navegação.

---

## 🎯 Próximos Passos (Preview para a Sprint 12)

- **Finalizar a pipeline de dados.**  
- **Concluir os testes unitários e de integração.**  
- Implementar e validar o **cronjob** para execução automática das atualizações e alertas.  
- Recuperar o CSS perdido na página de alertas.  
- Corrigir problemas no roteamento da dashboard.  
- Refinar o deploy e resolver pendências técnicas.  

---

✍️ **Ata validada por:** @mariadenis
