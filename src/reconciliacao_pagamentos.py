# -*- coding: utf-8 -*-
"""Reconciliação financeira de pagamentos.csv — Vitaliza.

Pipeline validado de forma independente (Julius + recálculo Claude, 22/10/2026):
    1. Normaliza `valor` (3 formatos no mesmo campo: "34.90", 39.9, "R$ 34,90").
    2. Converte timestamps para America/Sao_Paulo (lojas enviam UTC com "Z";
       o site grava em horário de Brasília, sem fuso).
    3. Filtra status == "aprovado" e agrupa pelo mês em Brasília.
    4. Remove DUPLICIDADES FUNCIONAIS: registros com pagamento_id distintos,
       mas idênticos em (user_id, data_hora normalizada, valor, método,
       status, tentativa). Mantém 1 ocorrência.
    5. Aplica as taxas por método para obter o líquido de taxas.

"Líquido" aqui = após taxas de pagamento. Não é receita contábil reconhecida,
não desconta impostos nem custos.

Uso:
    python src/reconciliacao_pagamentos.py [caminho/para/pagamentos.csv]
    (padrão: data/raw/pagamentos.csv)
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.parametros import TAXAS, FUSO, CHAVE_DEDUP_PAGAMENTOS


def normalizar_valor(v: str) -> float:
    """'R$ 34,90' -> 34.90 ; '34.90'/'39.9' -> float direto."""
    v = str(v).strip()
    if v.startswith("R$"):
        v = v.replace("R$", "").strip().replace(".", "").replace(",", ".")
    return float(v)


def carregar_pagamentos(caminho: str) -> pd.DataFrame:
    df = pd.read_csv(caminho, dtype=str)
    df["valor_num"] = df["valor"].map(normalizar_valor)

    # Timestamps mistos: com fuso (UTC, "Z") e sem fuso (já Brasília)
    com_tz = df["data_hora"].str.contains(r"Z|\+", regex=True, na=False)
    dt_utc = (
        pd.to_datetime(df.loc[com_tz, "data_hora"], utc=True)
        .dt.tz_convert(FUSO)
        .dt.tz_localize(None)
    )
    dt_local = pd.to_datetime(df.loc[~com_tz, "data_hora"])
    df["dt_brt"] = pd.concat([dt_utc, dt_local]).sort_index()
    df["mes"] = df["dt_brt"].dt.to_period("M").astype(str)
    return df


def deduplicar_aprovados(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (aprovados deduplicados, duplicatas removidas)."""
    ap = df[df["status"] == "aprovado"].copy()
    mask_dup = ap.duplicated(subset=CHAVE_DEDUP_PAGAMENTOS, keep="first")
    return ap[~mask_dup], ap[mask_dup]


def resumo_mensal(ap_dedup: pd.DataFrame) -> pd.DataFrame:
    ap = ap_dedup.copy()
    ap["liquido"] = ap["valor_num"] * (1 - ap["metodo"].map(TAXAS))
    out = (
        ap.groupby("mes")
        .agg(
            bruto_dedup=("valor_num", "sum"),
            liquido_taxas=("liquido", "sum"),
            registros=("valor_num", "size"),
        )
        .round(2)
    )
    return out


def main() -> None:
    caminho = sys.argv[1] if len(sys.argv) > 1 else "data/raw/pagamentos.csv"
    df = carregar_pagamentos(caminho)
    ap_dedup, dups = deduplicar_aprovados(df)

    print(f"Registros totais: {len(df):,}")
    print(f"Aprovados: {(df['status'] == 'aprovado').sum():,}")
    print(
        f"Duplicidades funcionais removidas (aprovados): {len(dups):,} "
        f"| R$ {dups['valor_num'].sum():,.2f}"
    )

    tab = resumo_mensal(ap_dedup)
    print("\nMês a mês (aprovado, deduplicado, Brasília):")
    print(tab.to_string())

    saida = Path("reports/reconciliacao_pagamentos_mensal.csv")
    saida.parent.mkdir(exist_ok=True)
    tab.to_csv(saida)
    print(f"\nSalvo em {saida}")


if __name__ == "__main__":
    main()
