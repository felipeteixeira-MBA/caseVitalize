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

## Versões

| Data | Mudança |
| --- | --- |
| 22/10/2026 | Deduplicação funcional de pagamentos definida e validada (set/26: bruto R$ 492.571,70; líquido R$ 436.442,35). TIDY v1 marcado como desatualizado nos agregados financeiros. |
