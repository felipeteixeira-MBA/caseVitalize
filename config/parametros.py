# -*- coding: utf-8 -*-
"""Parâmetros do case Vitaliza — fonte única para todos os scripts.

Origem: enunciado do case (Inteli, Módulo 2) e dicionário de dados.
Qualquer mudança aqui deve ser registrada em docs/decisoes.md.
"""

# Corte temporal da base
DATA_CORTE = "2026-09-30"          # último dia com dados
FUSO = "America/Sao_Paulo"          # fuso de referência das análises

# Preços (R$)
PRECO_MENSAL_ATE_FEV26 = 34.90
PRECO_MENSAL_DESDE_MAR26 = 39.90    # reajuste em 01/03/2026
PRECO_ANUAL = 299.90
PRECO_ANUAL_CUPOM_INFLUENCER = 239.90  # 1º ano

# Taxas por método de cobrança (fração da cobrança retida pelo intermediário)
TAXAS = {
    "app_store": 0.15,
    "google_play": 0.15,
    "cartao": 0.035,
    "pix_automatico": 0.0099,
}

# Custos (R$)
CUSTO_SERVIR_MES = 4.20
CAC_2026 = 118.00

# Canais de contato: custo unitário e teto mensal (nov/dez 2026)
CANAIS = {
    "push":     {"custo": 0.00, "teto": None, "obs": "máx. 1 por assinante/semana"},
    "email":    {"custo": 0.01, "teto": None},
    "whatsapp": {"custo": 0.40, "teto": 1500},
    "cs":       {"custo": 18.00, "teto": 300},
}

ORCAMENTO_CRM_MES = 40_000.00  # inclui descontos concedidos e custo de IA generativa

# Chave de duplicidade funcional em pagamentos.csv
# (registros com pagamento_id distintos mas idênticos nesta combinação = duplicata)
CHAVE_DEDUP_PAGAMENTOS = [
    "user_id", "dt_brt", "valor_num", "metodo", "status", "tentativa",
]
