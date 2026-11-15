# Granularidade: uma linha por conta, com treinos e minutos

Gerado por `src/contas_treinos.py`. Só leitura dos brutos (SHA-256 conjunto `51c9a8cea7d384b3…` conferido antes e depois). Base: `dados/processados/contas_treinos.parquet` (fora do Git).

## 1. Grão e contagens

| arquivo | uma linha por | linhas | user_id únicos |
|---|---|---|---|
| usuarios.csv | conta (`user_id`) | 64.948 | 64.948 |
| atividades.parquet | treino (`atividade_id`) | 1.254.475 | 36.551 |
| contas_treinos.parquet (saída) | conta (`user_id`) | = contas de usuarios.csv |  |

- `user_id` repetido em usuarios.csv: 0; `atividade_id` repetido em atividades.parquet: 0.
- `user_id` de atividades que não existe em usuarios.csv: **0** (0 treinos). Contas sem nenhum treino no bruto: 28.397.

## 2. Etapas de filtro dos treinos (linhas antes e depois)

| etapa | treinos | removidos |
|---|---|---|
| 0. bruto | 1.254.475 |  |
| 1. remove duração ≤ 0 (decisão 23) | 1.250.826 | −3.649 |
| 2. remove início depois de 30/09/2026, horário de Brasília | 1.250.826 | −0 |

- Fuso: o `inicio` do garmin é UTC (+3 h medido na análise 5); Brasília = garmin − 3 h. Depois do corte: **34** treinos com o horário bruto, **0** com o fuso corrigido (os garmin das primeiras horas de 01/10 voltam para dentro).
- Distância anulada (decisões 24 e 25): 949 acima de 200 km e 7.435 com `gps_ok` falso; as linhas não mudam.
- Treinos de contas de teste no bruto: 0 (as contas ficam marcadas, decisão 22).

## 3. Duplicatas app × relógio (só marcadas, nada removido)

- Pares (mesma conta, tipo canônico, duração, início ≤ 5 min com fuso corrigido, um por treino): **9.365** = 5.190 app com garmin + 4.175 app com apple_health ✔. Candidatos antes do desempate: 9.365.
- `duplicata_app_relogio` marca a ponta app (9.365 treinos), a que a decisão 11 removeria; a ponta do relógio fica sem marca. `tipo_canonico` é uma coluna nova; o `tipo` original não mudou.

## 4. Resumo por conta e junção

- Resumo por `user_id` antes de juntar: 36.538 contas com treino (todos os treinos) e 36.538 (sem as duplicatas).
- Junção esquerda: usuarios.csv 64.948 → 64.948 linhas ✔; `user_id` repetido: 0 ✔.
- Soma dos treinos por conta: **1.250.826** = treinos usados 1.250.826 ✔ (sem duplicatas: 1.241.461 = 1.241.461 ✔).
- Treinos de `user_id` ausentes em usuarios.csv: 0.
- Contas sem treino ficam com `treinos = 0`, `minutos = 0`, `distancia_km = 0` e `tem_treino = False` (`distancia_km` 0 também vale para quem treinou sem GPS: a soma é só dos treinos com valor).

## 5. Contas e treinos em cada cenário (item 8)

| cenário | contas | com treino | sem treino | treinos |
|---|---|---|---|---|
| tudo (bruto) | 64.948 | 36.551 | 28.397 | 1.254.475 |
| sem contas de teste | 64.888 | 36.551 | 28.337 | 1.254.475 |
| sem treinos após o corte | 64.948 | 36.551 | 28.397 | 1.254.475 |
| sem os dois | 64.888 | 36.551 | 28.337 | 1.254.475 |
| base final (+ decisão 23) | 64.888 | 36.538 | 28.350 | 1.250.826 |

Cenários com treinos sobre o bruto (sem decisão 23) mostram só o efeito de contas de teste e do corte; a última linha é a base final.

## 6. Tamanho do efeito das duplicatas (todos × sem duplicatas)

| medida | todos os treinos | sem duplicatas | diferença |
|---|---|---|---|
| treinos | 1.250.826 | 1.241.461 | −9.365 (0.75%) |
| minutos | 58.269.441 | 57.835.103 | −434.337 (0.75%) |
| distância (km) | 6.562.355 | 6.513.122 | −49.232 |
| contas com treino | 36.538 | 36.538 | −0 |
| contas com número de treinos diferente |  |  | 4.940 |

## 7. Decisões novas propostas (formato do `decisoes.md`, não gravadas)

| # | Data | Arquivo | Problema | Decisão (corrigir/remover/marcar) | Motivo | Efeito na contagem (antes → depois) |
|---|------|---------|----------|-----------------------------------|--------|-------------------------------------|
| 28 | 09/11/2026 | usuarios.csv + atividades.parquet | granularidade: contas (1 linha por conta) × treinos (1 linha por treino) | resumir os treinos por `user_id` e juntar pela esquerda em `contas_treinos.parquet`; contas sem treino ficam com 0 e `tem_treino = False` | juntar direto multiplicaria contas por treino; quem não treinou é informação, não ausência | 64.948 → 64.948 linhas; 36.538 contas com treino e 28.410 sem |
| 29 | 09/11/2026 | atividades.parquet | 0 treinos depois de 30/09/2026 em Brasília (34 com o horário bruto do garmin) | remover da base de contas (corte), com o garmin convertido (−3 h) antes de comparar | nenhuma análise usa informação posterior ao corte; sem o fuso, treinos garmin das primeiras horas de 01/10 ficariam de fora do corte por engano | 1.250.826 → 1.250.826 (−0) |
| 30 | 09/11/2026 | atividades.parquet | 9.365 treinos em dobro (app × relógio) | marcar `duplicata_app_relogio` na ponta app em `contas_treinos.parquet`; duas versões de treinos e minutos (`treinos`/`treinos_sem_dup`), sem remover linha | pedido do usuário de ver o tamanho do efeito antes de aplicar a decisão 11 nesta base; as colunas principais usam todos os treinos | 1.250.826 → 1.250.826; efeito −9.365 treinos (0.75%) |

---
Conferência: brutos inalterados.