# -*- coding: utf-8 -*-
"""Testes da base analítica do corte (artefato intermediário).

Números de referência validados em 28/10/2026 por recálculo independente
direto dos CSVs brutos, reconciliados com o enunciado e os slides do
professor. (A reconciliação financeira tem testes próprios em
tests/test_pagamentos.py.)

Uso:
    python tests/test_base_analitica.py [data/raw]
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.base_analitica import ARQUIVOS, CORTE_FIM, construir_base

# ---- Números de referência (validados) -------------------------------------
REF = {
    "pagantes_ativos_corte": 14_753,       # enunciado §01
    "colunas": 61,
    "mrr_corte": 457_281.85,               # última cobrança >0; anual /12
    "churn_set26_perdas": 714,             # dicionário §11
    "churn_set26_ativos": 14_319,          # => 4,99%
    "churn_abr26_perdas": 1_154,           # pior mês => 8,11%
    "churn_abr26_ativos": 14_237,
    "churn_medio_2025": 5.62,              # enunciado: 5,6%
    "churn_medio_2026": 6.62,              # enunciado: 6,6%
    "mix_plano": {"anual": 8_478, "mensal": 6_275},          # 57,5% / 42,5%
    "mix_canal": {"app_store": 5_395, "google_play": 4_964,  # lojas 70,2%
                  "web_cartao": 2_994, "web_pix": 1_400},
}
TOL = 0.01


def main() -> None:
    raw = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
    faltam = [a for a in ARQUIVOS if not (raw / a).exists()]
    if faltam:
        sys.exit(f"Arquivos ausentes em {raw}: {faltam} (ver data/README.md)")

    base, serie = construir_base(raw)
    falhas = []

    def check(nome, obtido, esperado, exato=True):
        ok = (obtido == esperado) if exato else abs(obtido - esperado) <= TOL
        print(f"[{'OK ' if ok else 'FALHA'}] {nome}: obtido={obtido} esperado={esperado}")
        if not ok:
            falhas.append(nome)

    # Grão e cobertura
    check("pagantes ativos no corte", len(base), REF["pagantes_ativos_corte"])
    check("user_id único", base.user_id.is_unique, True)
    check("sem cortesia na base", (base.plano == "cortesia").sum(), 0)
    check("nº de variáveis", base.shape[1], REF["colunas"])

    # MRR
    check("MRR no corte (R$)", round(base.mrr.sum(), 2), REF["mrr_corte"], exato=False)

    # Churn oficial (dicionário §11)
    s9 = serie[serie.mes == "2026-09"].iloc[0]
    check("set/26 perdas", int(s9.perdas), REF["churn_set26_perdas"])
    check("set/26 ativos no início", int(s9.ativos_inicio), REF["churn_set26_ativos"])
    s4 = serie[serie.mes == "2026-04"].iloc[0]
    check("abr/26 perdas", int(s4.perdas), REF["churn_abr26_perdas"])
    check("abr/26 ativos no início", int(s4.ativos_inicio), REF["churn_abr26_ativos"])
    m25 = round(serie[serie.mes.str.startswith("2025")].churn_pct.mean(), 2)
    m26 = round(serie[serie.mes.str.startswith("2026")].churn_pct.mean(), 2)
    check("churn médio 2025 (%)", m25, REF["churn_medio_2025"])
    check("churn médio jan–set/26 (%)", m26, REF["churn_medio_2026"])

    # Mix de plano e canal (contagens exatas)
    check("mix de plano", base.plano.value_counts().to_dict(), REF["mix_plano"])
    check("mix de canal", base.canal_cobranca.value_counts().to_dict(), REF["mix_canal"])

    # Anti-vazamento: nenhuma data de referência posterior ao corte
    for col in ["inicio_assinatura", "data_cadastro", "ultima_cobranca_data"]:
        ok = pd.to_datetime(base[col]).dropna().le(CORTE_FIM).all()
        check(f"sem data pós-corte em {col}", bool(ok), True)

    print()
    if falhas:
        print(f"{len(falhas)} teste(s) FALHARAM: {falhas}")
        sys.exit(1)
    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()
