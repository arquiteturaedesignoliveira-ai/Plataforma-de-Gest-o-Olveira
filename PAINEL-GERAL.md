# Painel Geral — Escritório Oliveira

> Documento único de referência: tudo que já foi desenvolvido, onde está e o que falta.
> Regra fixa: toda vez que algo for criado/alterado em qualquer frente, este arquivo é atualizado no mesmo momento (aqui) ou na próxima sessão em que essa frente for tocada (fora daqui). Se um item está desatualizado, é porque ainda não foi reportado — atualize avisando "atualiza o painel" nessa frente.

Última atualização: 2026-07-29

---

## Índice de frentes

| Frente | Status | Onde vive | Última atualização | Próximo passo |
|---|---|---|---|---|
| Sistema Oliveira (gestão do escritório) | 🟢 Em produção, uso ativo | Este repositório (`index.html`, SPA) | 2026-07-21 (merge apresentação de orçamento) | Ver pendências abaixo |
| Método de projeto | 🟡 Localizado, conteúdo não revisado | Claude.ai Projeto "GESTÃO ARQ" (tem pasta local também) | 2026-06-13 | Abrir o projeto e trazer o conteúdo pra cá |
| Template de apresentação/orçamento (16:9) | 🟢 Feito | Este repositório, dentro do `index.html` (gerador de slides) | 2026-07-21 | Confirmar se é o item que você chamou de "template de arcade" |
| Nova marca / identidade visual | ⚪ Não mapeado aqui | Ainda não localizado num Projeto Claude específico | — | Apontar onde está (Projeto Claude, Canva, Drive) |
| Oficina Estilos (gestão da oficina) | 🟡 Localizado, conteúdo não revisado | Claude.ai Projeto "GESTÃO STYLOS" | 2026-06-18 | Abrir o projeto e trazer o conteúdo pra cá |
| Classificação Oliveira (De-Para + Ramificação) | 🟢 Feito | Artifacts Claude (fora deste repo) | 2026-07-22 | Ver seção 6 |
| MAARA — Passeio Virtual 360° | 🟢 Feito | Artifact Claude (fora deste repo) | 2026-07-24 | Ver seção 7 |
| Arc — Expanding Cards | 🟡 Não identificado | Artifact Claude (fora deste repo) | 2026-07-23 | Confirmar se é do escritório ou exploração avulsa |
| MÉTODO_Render IA | 🟡 Localizado, conteúdo não revisado | Claude.ai Projeto "MÉTODO_Render IA" | 2026-06-13 | Ver seção 9 |
| Sistema Operacional Profissional (hub de métodos) | 🟡 Localizado — possível hub já existente | Claude.ai Projeto "Sistema Operacional Profi..." | 2026-06-06 | Ver seção 10 — checar sobreposição com este painel |

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

**Localizado:** Projeto Claude.ai "GESTÃO ARQ" (última atualização 13/06/2026), que também tem uma pasta local associada. Ainda não abri o conteúdo — você vai dar uma olhada primeiro.

**Ação pendente:** abrir o projeto e trazer aqui o que for método/framework de projeto (ou colar o resumo, ou linkar o projeto se for compartilhável).

---

## 3. Template de apresentação/orçamento

**O que é:** gerador de apresentação de orçamento em slides, formato 16:9, embutido no próprio Sistema Oliveira (mesmo `index.html`, commit `466732c` / PR #1, mesclado em 21/07/2026).

Se "template de arcade" que você mencionou for outra coisa (não a de orçamento), me diga o nome certo ou onde está para eu corrigir esta linha.

---

## 4. Nova marca / identidade visual

Ainda não identifiquei um Projeto Claude.ai específico com esse nome. Pode estar dentro de um dos projetos já localizados (GESTÃO ARQ ou Sistema Operacional Profissional) ou em outro lugar (Canva, Drive).

**Ação pendente:** confirmar em qual projeto/pasta está, ou apontar direto (Canva, Drive, etc).

---

## 5. Oficina Estilos (gestão da oficina)

**Localizado:** Projeto Claude.ai "GESTÃO STYLOS" (última atualização 18/06/2026).

**Ação pendente:** abrir o projeto e trazer aqui o essencial (o que já foi decidido/estruturado para a gestão da oficina).

---

## 6. Classificação Oliveira (De-Para + Ramificação)

**O que é:** sistema de classificação/taxonomia do escritório, com dois artifacts Claude que compartilham a mesma identidade visual (paleta terracota, fonte Sora):
- **De-Para completo** — tabela de correspondência entre sistemas de classificação, com busca e estatísticas. https://claude.ai/code/artifact/bb58bbd9-3f0d-4d36-a3ed-d211b45784cd
- **Ramificação completa** — árvore/hierarquia completa da classificação. https://claude.ai/code/artifact/6747b772-6b58-4688-a03a-1bb1ef07331a

Última atualização: 2026-07-22. Provável ligação com as especificações técnicas do Sistema Oliveira (módulo de classificação/pacotes já existente no `index.html`) — a confirmar.

## 7. MAARA — Passeio Virtual 360°

**O que é:** visualizador de passeio virtual 360° com a marca "Arquitetura & Design Oliveira", para apresentar um projeto (MAARA) a clientes — hotspots, cenas navegáveis, giroscópio no celular.
https://claude.ai/code/artifact/91e5a77c-32cf-4d15-afe3-db610641f218
Última atualização: 2026-07-24.

## 8. Arc — Expanding Cards *(não identificado)*

Componente de UI com cards que expandem no hover ("Well-being, by design"). Não tem referência clara ao escritório Oliveira — pode ser uma exploração/estudo avulso, ou parte de um projeto ainda não descrito aqui.
https://claude.ai/code/artifact/44b67172-7164-4850-8eee-31589c27ff4d
**Pendente:** confirmar se isso pertence a alguma frente do escritório ou se é descartável do painel.

## 9. MÉTODO_Render IA

**O que é:** Projeto Claude.ai — "Estudo e testes para fluxo de Renderização com Inteligência Artificial". Última atualização 13/06/2026. Conteúdo ainda não revisado.

**Ação pendente:** abrir e trazer o que já foi validado do fluxo de renderização com IA.

## 10. Sistema Operacional Profissional (possível hub já existente)

**Atenção:** este Projeto Claude.ai se descreve como "Central estratégica para desenvolvimento, documentação e evolução dos métodos..." (última atualização 06/06/2026) — ou seja, **pode já ser um hub equivalente ao que este painel está tentando ser.**

**Ação pendente:** antes de continuar expandindo este painel, vale abrir esse projeto e decidir: unificar os dois (este painel absorve aquele, ou vice-versa), ou manter os dois com papéis diferentes e deixar claro qual é a fonte de verdade.

## Como manter isto vivo

1. **Aqui no Sistema Oliveira / repositório:** sempre que uma sessão de desenvolvimento terminar, esta tabela e a seção correspondente são atualizadas antes do commit final.
2. **Fora daqui (ChatGPT, Canva, Drive):** como não há acesso automático, a atualização depende de você trazer a informação — por exportação, print, ou resumo rápido — e eu incorporo aqui.
3. **Quando ficar em dúvida "isso está em algum lugar?"**, abra este arquivo primeiro. Se não estiver aqui, ainda não foi trazido para o hub — não significa que não existe.
