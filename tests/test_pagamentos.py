# -*- coding: utf-8 -*-
"""Testes de regras de negócio — pagamentos.csv.

Números de referência validados em 22/10/2026 por duas vias independentes
(pipeline Julius e recálculo em Claude, direto do CSV bruto), batendo com o
slide do professor (R$ 492.571,70 bruto / R$ 436.442,35 líquido em set/26).

Uso:
    python tests/test_pagamentos.py [caminho/para/pagamentos.csv]
    (padrão: data/raw/pagamentos.csv)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.parametros import TAXAS
from src.reconciliacao_pagamentos import carregar_pagamentos, deduplicar_aprovados

# ---- Números de referência (validados) -------------------------------------
REF = {
    "set26_bruto_antes_dedup": 499_402.40,   # aprovadas em set/26, Brasília
    "set26_registros_antes_dedup": 7_176,
    "set26_duplicatas_qtd": 93,
    "set26_duplicatas_valor": 6_830.70,
    "set26_bruto_dedup": 492_571.70,         # = slide do professor
    "set26_liquido_taxas": 436_442.35,       # = slide do professor
    "jan_set26_bruto_dedup": 4_090_356.60,
    "jan_set26_liquido_taxas": 3_629_311.33,
    "base_toda_duplicatas_qtd": 1_941,       # jul/24–set/26, aprovados
    "base_toda_duplicatas_valor": 118_295.90,
}
TOL = 0.01  # tolerância de arredondamento em R$


def aproximado(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    caminho = sys.argv[1] if len(sys.argv) > 1 else "data/raw/pagamentos.csv"
    df = carregar_pagamentos(caminho)
    ap_dedup, dups = deduplicar_aprovados(df)

    falhas = []

    def check(nome, obtido, esperado, exato=False):
        ok = (obtido == esperado) if exato else aproximado(obtido, esperado)
        status = "OK " if ok else "FALHA"
        print(f"[{status}] {nome}: obtido={obtido:,} esperado={esperado:,}")
        if not ok:
            falhas.append(nome)

    # Chave única do arquivo
    check("pagamento_id único", df["pagamento_id"].nunique(), len(df), exato=True)

    # Setembro/2026
    ap = df[df["status"] == "aprovado"]
    set26 = ap[ap["mes"] == "2026-09"]
    check("set/26 registros aprovados (antes dedup)", len(set26),
          REF["set26_registros_antes_dedup"], exato=True)
    check("set/26 bruto antes dedup", round(set26["valor_num"].sum(), 2),
          REF["set26_bruto_antes_dedup"])

    dups_set = dups[dups["mes"] == "2026-09"]
    check("set/26 duplicatas (qtd)", len(dups_set),
          REF["set26_duplicatas_qtd"], exato=True)
    check("set/26 duplicatas (R$)", round(dups_set["valor_num"].sum(), 2),
          REF["set26_duplicatas_valor"])

    set26_d = ap_dedup[ap_dedup["mes"] == "2026-09"]
    bruto_d = round(set26_d["valor_num"].sum(), 2)
    check("set/26 bruto deduplicado", bruto_d, REF["set26_bruto_dedup"])

    liquido = round(
        (set26_d["valor_num"] * (1 - set26_d["metodo"].map(TAXAS))).sum(), 2
    )
    check("set/26 líquido de taxas", liquido, REF["set26_liquido_taxas"])

    # Jan–set/2026
    y26 = ap_dedup[ap_dedup["mes"].str.startswith("2026")]
    check("jan–set/26 bruto deduplicado", round(y26["valor_num"].sum(), 2),
          REF["jan_set26_bruto_dedup"])
    liq26 = round((y26["valor_num"] * (1 - y26["metodo"].map(TAXAS))).sum(), 2)
    check("jan–set/26 líquido de taxas", liq26, REF["jan_set26_liquido_taxas"])

    # Duplicidade estrutural na base inteira
    check("duplicatas aprovadas na base toda (qtd)", len(dups),
          REF["base_toda_duplicatas_qtd"], exato=True)
    check("duplicatas aprovadas na base toda (R$)",
          round(dups["valor_num"].sum(), 2), REF["base_toda_duplicatas_valor"])

    print()
    if falhas:
        print(f"{len(falhas)} teste(s) FALHARAM: {falhas}")
        sys.exit(1)
    print("Todos os testes passaram.")


if __name__ == "__main__":
    main()
