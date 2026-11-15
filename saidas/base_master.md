# Base master por usuário (corte de 30/09/2026)

Gerado por `src/base_master.py`. Só leitura dos brutos (SHA-256 conjunto `e7623c2d992c8a73…`, inalterados). **64.948 linhas × 74 colunas**, uma por conta, tudo medido até 30/09/2026 23:59:59 (Brasília), sem rótulo de saída. Arquivo `dados/processados/base_master.parquet` (fora do Git).

## 1. Quem está na base

| situação no corte | contas |
|---|---|
| nunca_assinou | 32.305 |
| ex_assinante | 17.830 |
| ativo | 14.813 |
| ativos no corte (sem teste) | 14.753 |
| contas de teste (marcadas, mantidas) | 60 |

Segmentação: filtrar `ativo_no_corte` (14.753). `flag_conta_teste` e `flag_email_repetido` ficam como marcas, sem remover (decisão 22 e pendência dos e-mails).

## 2. Checagens

- Linhas = contas de `usuarios.csv` (64.948), um `user_id` por linha: ✔.
- Ativos no corte = 14.753 (série de churn): ✔.
- Soma dos treinos por conta = treinos usados (1.241.461): ✔; contas com treino diferente de `contas_treinos.treinos_sem_dup`: 0.
- Mesmos valores da `base_assinantes` de 30/09 para os 14.753 ativos (16 colunas comparadas): diferenças 0.
- Nenhuma fonte passa do corte: ✔ (máximos: eventos 2026-09-30 22:59; treinos 2026-09-30 21:59; uso_mensal 2026-09; pagamentos 2026-09-30 22:54; amizades 2026-09-30 00:00; posts 2026-09-30 22:59; tickets 2026-09-30 21:46).
- Nulos que sobram nas numéricas: `idade` 3.907, `tempo_de_casa_dias` 32.305, `dias_desde_desligamento` 50.135, `dias_ate_fim_periodo` 50.135, `dias_desde_fim` 47.118, `dias_semana_declarado` 8.304 (idade com marca; colunas de assinatura só se aplicam a quem tem assinatura ou está ativo).

## 3. Linhas antes e depois de cada passo

| passo | linhas antes | linhas depois | observação |
|---|---|---|---|
| espinha: usuarios.csv | 64.948 | 64.948 | 60 contas de teste marcadas |
| junção: assinatura e eventos | 64.948 | 64.948 | 32.643 contas com assinatura |
| junção: onboarding | 64.948 | 64.948 |  |
| junção: treinos até o corte | 64.948 | 64.948 | 36.538 contas com treino, 1.241.461 treinos |
| junção: uso mensal | 64.948 | 64.948 |  |
| junção: pagamentos | 64.948 | 64.948 | 31.782 contas com cobrança |
| junção: social | 64.948 | 64.948 |  |
| junção: suporte | 64.948 | 64.948 |  |
| junção: campanha de 10/08 | 64.948 | 64.948 | 14.120 sorteados |

## 4. Dicionário e marca de uso para a segmentação

`agrupamento` = pode formar os grupos (comportamento e perfil); `descritiva` = serve para descrever os grupos depois, não para formá-los; `proibida` = saída/rótulo, nunca no agrupamento. Os sinais de intenção de saída (renovação desligada, cancelamento no site, carência, prazo até o fim do período) ficam como descritivos para os grupos não virarem um preditor de churn disfarçado.

| coluna | bloco | uso |
|---|---|---|
| user_id | Identificação | descritiva |
| idade | Perfil | agrupamento |
| sexo | Perfil | agrupamento |
| uf | Perfil | agrupamento |
| canal_aquisicao | Perfil | agrupamento |
| sistema | Perfil | agrupamento |
| relogio_conectado | Perfil | agrupamento |
| dias_desde_cadastro | Perfil | agrupamento |
| flag_nascimento_invalido | Perfil | descritiva |
| flag_cadastro_apos_corte | Perfil | descritiva |
| flag_email_repetido | Perfil | descritiva |
| flag_conta_teste | Perfil | descritiva |
| situacao_no_corte | Assinatura | descritiva |
| ativo_no_corte | Assinatura | descritiva |
| plano_atual | Assinatura | descritiva |
| canal_cobranca | Assinatura | descritiva |
| tempo_de_casa_dias | Assinatura | descritiva |
| renovacao_desligada | Assinatura (sinais de saída) | descritiva |
| dias_desde_desligamento | Assinatura (sinais de saída) | descritiva |
| tem_cancelamento_web | Assinatura (sinais de saída) | descritiva |
| dias_ate_fim_periodo | Assinatura (sinais de saída) | descritiva |
| n_carencia | Assinatura (sinais de saída) | descritiva |
| n_renovacoes | Assinatura | agrupamento |
| dias_desde_fim | Assinatura (saída já ocorrida) | proibida |
| data_fim_assinatura | Assinatura (saída já ocorrida) | proibida |
| motivo_fim | Assinatura (saída já ocorrida) | proibida |
| nivel_declarado | Onboarding | agrupamento |
| dias_semana_declarado | Onboarding | agrupamento |
| sem_questionario | Onboarding | descritiva |
| nivel_nao_informado | Onboarding | descritiva |
| dias_por_semana_nao_informado | Onboarding | descritiva |
| objetivo_sem_resposta | Onboarding | descritiva |
| treinos_30d | Treinos | agrupamento |
| treinos_60d | Treinos | agrupamento |
| treinos_90d | Treinos | agrupamento |
| minutos_30d | Treinos | agrupamento |
| minutos_90d | Treinos | agrupamento |
| km_90d | Treinos | agrupamento |
| n_modalidades_90d | Treinos | agrupamento |
| pct_relogio_90d | Treinos | agrupamento |
| recencia_dias | Treinos | agrupamento |
| treinos_total | Treinos | agrupamento |
| minutos_total | Treinos | agrupamento |
| km_total | Treinos | agrupamento |
| n_modalidades_total | Treinos | agrupamento |
| tipo_principal | Treinos | agrupamento |
| pct_ar_livre | Treinos | agrupamento |
| pct_video | Treinos | agrupamento |
| tendencia | Treinos | agrupamento |
| sem_treino_90d | Treinos | descritiva |
| tem_treino | Treinos | descritiva |
| sessoes_app_mes | App | agrupamento |
| dias_ativos_mes | App | agrupamento |
| minutos_mes | App | agrupamento |
| sessoes_app_3m | App | agrupamento |
| minutos_3m | App | agrupamento |
| pg_aprovados | Pagamentos | agrupamento |
| pg_recusas | Pagamentos | agrupamento |
| pg_recusas_90d | Pagamentos | agrupamento |
| pg_estornos | Pagamentos | agrupamento |
| pg_pct_recusa | Pagamentos | agrupamento |
| pg_valor_medio | Pagamentos | agrupamento |
| pg_metodo_principal | Pagamentos | agrupamento |
| n_seguindo | Social | agrupamento |
| n_seguidores | Social | agrupamento |
| n_posts | Social | agrupamento |
| n_posts_90d | Social | agrupamento |
| n_tickets | Suporte | agrupamento |
| n_tickets_90d | Suporte | agrupamento |
| ticket_categoria_principal | Suporte | agrupamento |
| grupo_campanha | Campanha | descritiva |
| camp_abriu_push | Campanha | descritiva |
| camp_abriu_email | Campanha | descritiva |
| camp_clicou | Campanha | descritiva |

Colunas por uso: agrupamento 46, descritiva 25, proibida 3.

## 5. Regras e armadilhas

- Treinos de `atividades_limpa_v2` (decisões 10, 11, 23 a 25; só 2026); pagamentos sem duplicatas aprovadas (decisão 16); fuso em Brasília (decisão 13).
- Vazios: contagens = 0; recência de quem não treinou = 90 (teto) com `sem_treino_90d`; tendência sem base = 1,0; categóricas = `nao_informado`; `tipo_principal` = `sem_treino`; idade NA com marca.
- Quem nunca assinou (freemium) tem plano e canal `nao_informado` e nulos nas colunas de assinatura; o comportamento dele é bem diferente do de um assinante, e a segmentação do case é sobre os ativos.
- `ex_assinante` e as colunas de fim são saída já ocorrida: por isso `proibida` para o agrupamento.
- `grupo_campanha` descreve a campanha de 10/08; não deve formar grupos, porque o sorteio é aleatório.

## 6. Decisões propostas (formato do `decisoes.md`, não gravadas)

| # | Data | Arquivo | Problema | Decisão (corrigir/remover/marcar) | Motivo | Efeito na contagem (antes → depois) |
|---|------|---------|----------|-----------------------------------|--------|-------------------------------------|
| 37 | 09/11/2026 | usuarios.csv + demais fontes | base única por usuário para a segmentação | base master de uma linha por conta no corte de 30/09 (64.948 contas; 14.753 ativos), com a marca `ativo_no_corte` e sem rótulo de saída; teste e e-mail repetido só marcados | segmentar sem usar a variável de saída (objetivo 3); manter todas as contas deixa olhar também quem nunca pagou | 64.948 → 64.948 linhas; 74 colunas |
| 38 | 09/11/2026 | base_master | colunas ligadas à saída podem contaminar o agrupamento | cada coluna ganha a marca `agrupamento`, `descritiva` ou `proibida`; sinais de intenção de saída e a campanha só descrevem | evita um agrupamento que seja um preditor de churn disfarçado | 46 para agrupamento, 25 descritivas, 3 proibidas |

---
Conferência: brutos inalterados.