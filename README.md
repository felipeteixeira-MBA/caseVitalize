# caseVitalize — MBA em IA e Dados para Negócios (Inteli, Módulo 2)

Ambiente de trabalho do business case **Vitaliza** (app fictício de treino por assinatura): retenção e churn, do diagnóstico à decisão de contato, seguindo **CRISP-DM**.

> Este repositório versiona **código, regras, testes e documentação** — nunca os dados brutos do data room nem materiais do curso com direitos autorais. Veja `data/README.md`.

## Estrutura

```
caseVitalize/
├── src/        # Scripts de tratamento e análise (Python)
├── tests/      # Validações automáticas (números de referência conferidos)
├── config/     # Parâmetros do case: corte, preços, taxas, definições
├── docs/       # Decisões metodológicas, regras de negócio, limitações
├── reports/    # Relatórios aprovados (com versão e estado)
└── data/       # Dados locais — FORA do Git (ver data/README.md)
```

## Como reproduzir

1. Coloque os arquivos do data room em `data/raw/` (lista em `data/README.md`).
2. Instale as dependências: `pip install pandas numpy pyarrow`
3. Rode a reconciliação financeira: `python src/reconciliacao_pagamentos.py`
4. Rode a base analítica do corte (artefato intermediário): `python src/base_analitica.py`
5. Rode os testes: `python tests/test_pagamentos.py` e `python tests/test_base_analitica.py`

Os testes comparam o resultado com os números de referência já validados de forma independente (duas fontes: pipeline Julius e recálculo em Claude, a partir do CSV bruto).

### Base analítica do corte (artefato intermediário)

`src/base_analitica.py` integra os **12 arquivos** do data room pelo `user_id` e produz **uma linha por assinante pagante ativo em 30/09/2026 (14.753 × 61 variáveis)** — o insumo dos objetivos 3 a 8 (segmentação, previsão, decisão de contato, ROI, mensagem). Reaproveita a normalização/deduplicação de `src/reconciliacao_pagamentos.py`, aplica a regra oficial de churn (dicionário §11) e não usa nenhuma informação posterior ao corte (anti-vazamento). `tests/test_base_analitica.py` trava as âncoras: 14.753 pagantes, MRR R$ 457.281,85, churn set/26 = 714/14.319 (4,99%) e abr/26 = 1.154/14.237 (8,11%), médias 5,62%/6,62%, mix de plano e de canal em contagens exatas.

## Estado das entregas

| Entrega | Estado |
| --- | --- |
| Reconciliação de pagantes e série de churn (7 pontos do enunciado) | Validada |
| Diagnóstico V1 (hipóteses, segmentação, personas) | Validado por amostra |
| Diagnóstico V2 (heatmaps; ganho preditivo ~nulo) | Validado — reprodução exata |
| Reconciliação financeira com deduplicação (set/26 e jan–set/26) | **Validada — números de referência em `tests/`** |
| Base analítica do corte, 14.753 × 61 (artefato intermediário) | **Validada — âncoras travadas em `tests/test_base_analitica.py`** |
| Painel TIDY v1 | **Desatualizado** — agregados financeiros anteriores à deduplicação |
| Modelagem preditiva final, uplift da campanha, política de contato | Pendente |

## Regra de ouro aprendida no case

Conciliar somas entre fonte bruta e base tratada **não valida a regra de negócio**: ambas podem carregar o mesmo erro (foi o caso das duplicidades funcionais de pagamento). Por isso os testes deste repo verificam regras (chave única, deduplicação, fuso), não só totais.
