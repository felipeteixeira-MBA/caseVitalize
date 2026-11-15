# Base de assinantes por corte (rótulo: sair em até 60 dias)

Gerado por `src/base_assinantes.py`. Só leitura dos brutos (SHA-256 conjunto `eabbedb0de1a00c3…`, inalterados). Uma linha por assinante ativo no corte, sem contas de teste/cortesia; tudo medido até o corte (Brasília). Bases em `dados/processados/base_assinantes_<corte>.parquet` (fora do Git).

## 1. Resumo por corte

| corte | papel | ativos (base) | ativos (série de churn) | janela do rótulo | saiu em 60 dias | taxa | colunas |
|---|---|---|---|---|---|---|---|
| 2026-04-30 | treino | 14.119 | 14.119 | até 2026-06-29 | 1.783 | 12,63% | 60 |
| 2026-05-31 | treino | 14.102 | 14.102 | até 2026-07-30 | 1.703 | 12,08% | 60 |
| 2026-06-30 | validação | 14.059 | 14.059 | até 2026-08-29 | 1.675 | 11,91% | 60 |
| 2026-09-30 | aplicação | 14.753 | 14.753 | até 2026-11-29 | — | — | 62 |

Painel rotulado (30/04, 31/05 e 30/06): **42.280** linhas em `base_assinantes_painel_rotulado.parquet`.

## 2. Checagens

- Ativos de cada corte iguais à série de churn (`churn_mensal.csv`): ✔.
- Rótulo igual à contagem direta em `assinaturas.csv` (outro caminho de cálculo): ✔.
- Data máxima usada por fonte e corte (nenhuma passa do corte): ✔.

| corte | eventos | treinos | pagamentos | amizades | posts | tickets | uso_mensal (mês) |
|---|---|---|---|---|---|---|---|
| 2026-04-30 | 2026-04-30 22:56 | 2026-04-30 21:59 | 2026-04-30 22:59 | 2026-04-30 00:00 | 2026-04-30 22:49 | 2026-04-30 19:57 | 2026-04 |
| 2026-05-31 | 2026-05-31 22:53 | 2026-05-31 09:59 | 2026-05-31 22:59 | 2026-05-31 00:00 | 2026-05-31 22:52 | 2026-05-31 21:49 | 2026-05 |
| 2026-06-30 | 2026-06-30 22:57 | 2026-06-30 21:59 | 2026-06-30 22:56 | 2026-06-30 00:00 | 2026-06-30 22:49 | 2026-06-30 18:23 | 2026-06 |
| 2026-09-30 | 2026-09-30 22:59 | 2026-09-30 21:59 | 2026-09-30 22:54 | 2026-09-30 00:00 | 2026-09-30 22:46 | 2026-09-30 21:46 | 2026-09 |

- Fim do período pago calculado (mensal: `inicio` + 30·k dias; anual: aniversário): bate com a `data_fim` real (no mensal, no primeiro ou no segundo fim de período) em 2026-04-30: 1.611 de 1.783; 2026-05-31: 1.539 de 1.703; 2026-06-30: 1.509 de 1.675 dos que saíram.
- Nulos que sobram nas colunas numéricas: 2026-04-30: idade 839, dias_semana_declarado 1.663 (com marca), outras 0; 2026-05-31: idade 849, dias_semana_declarado 1.667 (com marca), outras 0; 2026-06-30: idade 847, dias_semana_declarado 1.656 (com marca), outras 0; 2026-09-30: idade 897, dias_semana_declarado 1.747 (com marca), outras 0.

## 3. Passos e junções (linhas antes e depois)


### Corte 30/04/2026 (treino)

| passo | linhas antes | linhas depois | observação |
|---|---|---|---|
| assinaturas sem cortesia/teste | 32.643 | 32.583 | decisão 1 |
| ativas no corte | 32.583 | 14.119 | série de churn: 14.119 |
| junção: situação pelos eventos | 14.119 | 14.119 | 2.038 com renovação desligada |
| junção: perfil (usuarios) | 14.119 | 14.119 |  |
| junção: onboarding | 14.119 | 14.119 |  |
| junção: treinos até o corte | 14.119 | 14.119 | 13.647 contas com treino |
| junção: uso mensal | 14.119 | 14.119 |  |
| junção: pagamentos | 14.119 | 14.119 | 14.119 contas com cobrança |
| junção: social | 14.119 | 14.119 |  |
| junção: suporte | 14.119 | 14.119 |  |

### Corte 31/05/2026 (treino)

| passo | linhas antes | linhas depois | observação |
|---|---|---|---|
| assinaturas sem cortesia/teste | 32.643 | 32.583 | decisão 1 |
| ativas no corte | 32.583 | 14.102 | série de churn: 14.102 |
| junção: situação pelos eventos | 14.102 | 14.102 | 2.139 com renovação desligada |
| junção: perfil (usuarios) | 14.102 | 14.102 |  |
| junção: onboarding | 14.102 | 14.102 |  |
| junção: treinos até o corte | 14.102 | 14.102 | 13.713 contas com treino |
| junção: uso mensal | 14.102 | 14.102 |  |
| junção: pagamentos | 14.102 | 14.102 | 14.102 contas com cobrança |
| junção: social | 14.102 | 14.102 |  |
| junção: suporte | 14.102 | 14.102 |  |

### Corte 30/06/2026 (validação)

| passo | linhas antes | linhas depois | observação |
|---|---|---|---|
| assinaturas sem cortesia/teste | 32.643 | 32.583 | decisão 1 |
| ativas no corte | 32.583 | 14.059 | série de churn: 14.059 |
| junção: situação pelos eventos | 14.059 | 14.059 | 2.336 com renovação desligada |
| junção: perfil (usuarios) | 14.059 | 14.059 |  |
| junção: onboarding | 14.059 | 14.059 |  |
| junção: treinos até o corte | 14.059 | 14.059 | 13.722 contas com treino |
| junção: uso mensal | 14.059 | 14.059 |  |
| junção: pagamentos | 14.059 | 14.059 | 14.059 contas com cobrança |
| junção: social | 14.059 | 14.059 |  |
| junção: suporte | 14.059 | 14.059 |  |

### Corte 30/09/2026 (aplicação)

| passo | linhas antes | linhas depois | observação |
|---|---|---|---|
| assinaturas sem cortesia/teste | 32.643 | 32.583 | decisão 1 |
| ativas no corte | 32.583 | 14.753 | série de churn: 14.753 |
| junção: situação pelos eventos | 14.753 | 14.753 | 2.255 com renovação desligada |
| junção: perfil (usuarios) | 14.753 | 14.753 |  |
| junção: onboarding | 14.753 | 14.753 |  |
| junção: treinos até o corte | 14.753 | 14.753 | 14.576 contas com treino |
| junção: uso mensal | 14.753 | 14.753 |  |
| junção: pagamentos | 14.753 | 14.753 | 14.753 contas com cobrança |
| junção: social | 14.753 | 14.753 |  |
| junção: suporte | 14.753 | 14.753 |  |
| junção: campanha de 10/08 | 14.753 | 14.753 | 12.862 sorteados entre os ativos |

## 4. Dicionário de variáveis

| bloco | variáveis |
|---|---|
| Identificação | `user_id`, `assinatura_id`, `corte`, `inicio`, `tenure_dias`, `plano_atual`, `canal_cobranca` |
| Rótulo (não é variável) | `saiu_60d`, `rotulo_motivo_fim` (só nos cortes passados) |
| Situação pelos eventos | `renovacao_desligada`, `dias_desde_desligamento`, `n_renovacoes`, `n_carencia`, `tem_cancelamento_web`, `dias_ate_fim_periodo` |
| Perfil | `idade`, `flag_nascimento_invalido`, `sexo`, `uf`, `canal_aquisicao`, `sistema`, `relogio_conectado`, `flag_email_repetido` |
| Onboarding | `nivel_declarado`, `dias_semana_declarado`, `sem_questionario`, `nivel_nao_informado`, `dias_por_semana_nao_informado`, `objetivo_sem_resposta` |
| Treinos | `treinos_30d/60d/90d`, `minutos_30d/90d`, `km_90d`, `n_modalidades_90d`, `pct_relogio_90d`, `recencia_dias` (teto 90), `treinos_total`, `sem_treino_90d`, `tendencia` |
| App | `sessoes_app_mes`, `dias_ativos_mes`, `minutos_mes`, `sessoes_app_3m`, `minutos_3m` |
| Pagamentos | `pg_aprovados`, `pg_recusas`, `pg_recusas_90d`, `pg_estornos`, `pg_pct_recusa`, `pg_valor_medio`, `pg_metodo_principal` |
| Social | `n_seguindo`, `n_seguidores`, `n_posts`, `n_posts_90d` |
| Suporte | `n_tickets`, `n_tickets_90d`, `ticket_categoria_principal` |
| Campanha (só 30/09) | `grupo_campanha`, `camp_abriu_push`, `camp_abriu_email`, `camp_clicou` |

Regras de vazio: contagens ausentes = 0; recência de quem não treinou = 90 (teto) com `sem_treino_90d`; tendência sem base = 1,0; categóricas vazias = `nao_informado`; idade NA quando o nascimento é inválido (com marca). Treinos já com as decisões 10, 11 (duplicata app removida), 23, 24 e 25 (`atividades_limpa_v2`); pagamentos sem duplicatas aprovadas (decisão 16).

## 5. Armadilhas

- **Campanha de 10/08:** foi sorteada entre os pagantes ativos naquele dia. A janela do corte de 30/06 vai até 2026-08-29 e passa de 10/08; quem saiu antes de 10/08 não podia ser sorteado, e o efeito da campanha entra no rótulo sem estar nas variáveis. Por isso o corte de 30/06 é só de validação e `grupo_campanha` existe apenas na base de 30/09.
- **Treinos só de 2026:** a janela de 90 dias só existe para cortes a partir de 31/03/2026 (por isso o primeiro corte é 30/04).
- **Plano e canal** vêm de `assinaturas.csv`; nos eventos nunca mudam por conta, então não há vazamento. A **renovação** vem só dos eventos até o corte (o retrato de 01/10 erra a situação de 36,6% das contas com renovação desligada).
- **Taxa de saída diferente por corte:** as janelas de 60 dias têm sazonalidade diferente; comparar taxas entre cortes exige cuidado.

## 6. Decisões propostas (formato do `decisoes.md`, não gravadas)

| # | Data | Arquivo | Problema | Decisão (corrigir/remover/marcar) | Motivo | Efeito na contagem (antes → depois) |
|---|------|---------|----------|-----------------------------------|--------|-------------------------------------|
| 33 | 09/11/2026 | assinaturas.csv + eventos_assinatura.csv | base para prever a saída em 60 dias, sem vazamento | uma linha por assinante ativo no corte (sem cortesia/teste), com cortes de 30/04 e 31/05 (treino), 30/06 (validação) e 30/09 (aplicação); rótulo `saiu_60d` só nos cortes passados | o futuro de 30/09 ainda não aconteceu; janelas de treino antes da campanha de 10/08 | ativos: 2026-04-30 14.119; 2026-05-31 14.102; 2026-06-30 14.059; 2026-09-30 14.753 |
| 34 | 09/11/2026 | eventos_assinatura.csv | o retrato de 01/10 erra a renovação nos cortes passados | situação da renovação pelo último evento de liga/desliga até o corte; plano e canal do retrato (não mudam nos eventos) | evita vazamento (análise 11: retrato erra 36,6%) | 0 linhas removidas |
| 35 | 09/11/2026 | atividades.parquet | treinos duplicados e outliers nas variáveis de engajamento | variáveis de treino a partir de `atividades_limpa_v2` (decisões 10, 11, 23 a 25); `recencia_dias` com teto 90 e marca `sem_treino_90d` | mesma limpeza das demais análises; janela de 90 dias é o que cabe em todos os cortes | linhas inalteradas |
| 36 | 09/11/2026 | campanha_ago26.csv | campanha só pode ser variável depois de 10/08 | `grupo_campanha` apenas na base de 30/09 (1.891 ativos fora da campanha); corte de 30/06 só para validação | janela de 30/06 passa de 10/08 e o sorteio exclui quem já tinha saído | 0 linhas removidas |

---
Conferência: brutos inalterados.