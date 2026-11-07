# Decisões metodológicas e regras de negócio

Registro vivo: toda regra que muda um número entra aqui, com data e motivo.

## Definições

| Conceito | Regra adotada | Fonte |
| --- | --- | --- |
| Pagante ativo | Assinatura com status ativo em plano mensal ou anual; **exclui 60 cortesias** | Enunciado (14.753 no corte) |
| Churn mensal | Perdas entre os ativos no início do mês ÷ ativos no início do mês; entradas e saídas dentro do mesmo mês ficam fora do numerador | Enunciado |
| Corte | 30/09/2026; nenhuma variável pode usar informação posterior | Enunciado |
| Fuso | Análises em America/Sao_Paulo; lojas enviam UTC ("Z"), site grava em Brasília | Dicionário |
| Renovação desligada | NÃO é churn — a pessoa segue com acesso até o fim do período pago | Dicionário |

## Qualidade de dados — tratamentos

| Problema | Volume | Tratamento |
| --- | --- | --- |
| `pagamentos.valor` em 3 formatos ("34.90", 39.9, "R$ 34,90") | 19.750 com "R$" | Normalização para float antes de somar |
| **Duplicidade funcional em pagamentos** (ids distintos, mesma combinação user+data_hora+valor+método+status+tentativa) | 1.941 aprovados / R$ 118.295,90 (jul/24–set/26); 93 / R$ 6.830,70 só em set/26 | Manter 1 ocorrência por combinação. NÃO excluir toda tentativa > 1 (removeria pagamentos legítimos) |
| Treinos com duração ≤ 0 | 3.649 | Fora dos agregados de engajamento |
| Datas de nascimento implausíveis | 194 futuras + outras regras | Sinalizadas, não corrigidas |
| Cadastros posteriores ao corte | 119 contas | Segregados do painel histórico |
| Timestamps mistos (UTC × Brasília) | eventos e pagamentos | Conversão para Brasília; muda fronteiras de mês |

## Lições registradas

1. **Conciliar somas não valida regra de negócio.** Fonte bruta e TIDY "batiam" porque carregavam a mesma duplicidade. Teste de regra ≠ teste de total.
2. **Paradoxo de Simpson no uso:** no agregado, zero treinos no mês anterior parece churnar menos que 1–3 treinos; separando por plano, inverte (96,7% das observações com zero treinos são de anuais). Nunca interpretar média geral sem olhar composição.
3. **Associação ≠ causa.** Recusa de cobrança (26,6% vs 5,9%) e queda ≥50% de uso (12,1% vs 4,0%) são sinais diagnósticos, não efeitos causais.
4. **Heatmaps:** ganho preditivo ~nulo neste desenho (AUC 0,82558 → 0,82617). A tinta correlaciona com volume de treino já presente nas tabelas.
5. **Horizonte muda conclusão da campanha:** em 30 dias, nada conclusivo; até o corte, cupom −1,92 p.p. vs controle (IC95% 0,60–3,24) — exploratório.

## Base analítica do corte — artefato intermediário (28/10/2026)

`src/base_analitica.py`: uma linha por assinante pagante ativo em 30/09/2026
(**14.753 × 61**), integrando os 12 arquivos do data room pelo `user_id`.
Reaproveita a normalização e a deduplicação de `src/reconciliacao_pagamentos.py`,
exclui as 60 cortesias e não usa nenhuma informação posterior ao corte
(anti-vazamento para a modelagem). É o insumo dos objetivos 3 a 8.

Regra de churn que a validação flagrou: pelo dicionário (§11), **perda é
assinatura ativa no início do mês cujo fim cai no mês** — quem entrou e saiu
no mesmo mês fica fora do numerador. Sem essa regra, set/26 daria 717 perdas
em vez de 714 (e abr/26, 1.158 em vez de 1.154), e a série não bateria com o
enunciado. Âncoras reconciliadas e travadas em `tests/test_base_analitica.py`:
14.753 pagantes; MRR R$ 457.281,85 (última cobrança aprovada > 0; anual ÷ 12);
churn set/26 = 714/14.319 (4,99%) e abr/26 = 1.154/14.237 (8,11%); médias
5,62% (2025) e 6,62% (jan–set/26); mix anual/mensal = 8.478/6.275; mix de
canal = 5.395/4.964/2.994/1.400 (lojas 70,2%).

Convenção de ausentes: contagens viram 0; campos de estado ficam vazios
quando o fato não existe (ex.: `dias_desde_ultimo_treino` vazio = nunca
treinou em 2026 — vazio ≠ zero).

## Versões

| Data | Mudança |
| --- | --- |
| 22/10/2026 | Deduplicação funcional de pagamentos definida e validada (set/26: bruto R$ 492.571,70; líquido R$ 436.442,35). TIDY v1 marcado como desatualizado nos agregados financeiros. |
| 28/10/2026 | Base analítica do corte (artefato intermediário) adicionada: `src/base_analitica.py` + `tests/test_base_analitica.py` com as âncoras do enunciado; regra oficial de churn (§11) implementada e documentada. |
