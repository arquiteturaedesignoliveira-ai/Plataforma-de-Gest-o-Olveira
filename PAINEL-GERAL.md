# Painel Geral — Escritório Oliveira

> Documento único de referência: tudo que já foi desenvolvido, onde está e o que falta.
> Regra fixa: toda vez que algo for criado/alterado em qualquer frente, este arquivo é atualizado no mesmo momento (aqui) ou na próxima sessão em que essa frente for tocada (fora daqui). Se um item está desatualizado, é porque ainda não foi reportado — atualize avisando "atualiza o painel" nessa frente.

Última atualização: 2026-07-29

---

## Índice de frentes

| Frente | Status | Onde vive | Última atualização | Próximo passo |
|---|---|---|---|---|
| Sistema Oliveira (gestão do escritório) | 🟢 Em produção, uso ativo | Este repositório (`index.html`, SPA) | 2026-07-21 (merge apresentação de orçamento) | Ver pendências abaixo |
| Método de projeto | ⚪ Não mapeado aqui | Provavelmente ChatGPT / documento avulso | — | Exportar do ChatGPT ou descrever aqui |
| Template de apresentação/orçamento (16:9) | 🟢 Feito | Este repositório, dentro do `index.html` (gerador de slides) | 2026-07-21 | Confirmar se é o item que você chamou de "template de arcade" |
| Nova marca / identidade visual | ⚪ Não mapeado aqui | Provavelmente ChatGPT, Canva ou Drive | — | Exportar do ChatGPT ou apontar onde está |
| Oficina Estilos (gestão da oficina) | ⚪ Não mapeado aqui | Provavelmente ChatGPT ou outro repositório | — | Exportar do ChatGPT ou apontar onde está |

Legenda: 🟢 feito/ativo · 🟡 em andamento · 🔴 parado/bloqueado · ⚪ não mapeado ainda (sem visibilidade a partir daqui)

---

## 1. Sistema Oliveira (gestão do escritório)

**O que é:** aplicativo único (`index.html`, single-page app) que roda no navegador, com sincronização própria (Google Drive via token) e armazenamento local. Não depende de servidor.

**Módulos identificados no código atual:**
- Clientes (cadastro, contato, origem)
- Projetos (status, prazos, responsável, contrato)
- Propostas comerciais (parâmetros, geração de proposta, apresentação de orçamento em slides 16:9)
- Contratos (template de contrato, variáveis, geração de documento)
- Orçamento (parâmetros, cálculo, margem, custo estimado)
- Especificações técnicas (pacotes, classificação, fluxo, BIM)
- RDO — Relatório Diário de Obra (clima, efetivo, atividades, fotos)
- Terceiros/fornecedores (itens, template)
- Financeiro (senha de acesso separada, parcelas)
- Backup/sincronização com nuvem (import/export, merge, undo)

**Pendências conhecidas:** nenhuma reportada nesta sessão. Ao trabalhar em algo específico deste sistema, essa seção é atualizada com o que mudou.

---

## 2. Método de projeto

*Sem visibilidade a partir deste repositório.* Prováveis fontes: conversas no ChatGPT, documento à parte.

**Ação pendente:** você escolheu exportar o histórico completo do ChatGPT (Configurações → Dados no controle → Exportar dados). Quando o arquivo chegar por e-mail, envie o `conversations.json` (ou o `.zip`) aqui que eu extraio o que for método/framework de projeto e preencho esta seção.

---

## 3. Template de apresentação/orçamento

**O que é:** gerador de apresentação de orçamento em slides, formato 16:9, embutido no próprio Sistema Oliveira (mesmo `index.html`, commit `466732c` / PR #1, mesclado em 21/07/2026).

Se "template de arcade" que você mencionou for outra coisa (não a de orçamento), me diga o nome certo ou onde está para eu corrigir esta linha.

---

## 4. Nova marca / identidade visual

*Sem visibilidade a partir deste repositório.* Prováveis fontes: ChatGPT, Canva, Google Drive.

**Ação pendente:** mesma exportação do ChatGPT acima. Se a marca foi desenvolvida no Canva, me diga e eu busco lá diretamente (tenho acesso a essa ferramenta).

---

## 5. Oficina Estilos (gestão da oficina)

*Sem visibilidade a partir deste repositório.* Pode ser uma frente inteiramente separada (outro repositório, outra ferramenta, ou só conversas).

**Ação pendente:** mesma exportação do ChatGPT acima, ou me diga se existe um repositório/planilha/sistema próprio para ela.

---

## Como manter isto vivo

1. **Aqui no Sistema Oliveira / repositório:** sempre que uma sessão de desenvolvimento terminar, esta tabela e a seção correspondente são atualizadas antes do commit final.
2. **Fora daqui (ChatGPT, Canva, Drive):** como não há acesso automático, a atualização depende de você trazer a informação — por exportação, print, ou resumo rápido — e eu incorporo aqui.
3. **Quando ficar em dúvida "isso está em algum lugar?"**, abra este arquivo primeiro. Se não estiver aqui, ainda não foi trazido para o hub — não significa que não existe.
