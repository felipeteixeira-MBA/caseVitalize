# -*- coding: utf-8 -*-
"""Base analítica do corte (artefato intermediário) — Vitaliza.

Uma linha por assinante pagante ativo em 30/09/2026 (14.753 × 61), integrando
os 12 arquivos do data room pelo ``user_id``. É o insumo dos objetivos 3 a 8
do case (segmentação, previsão, decisão, ROI, mensagem).

Regras (validadas em 28/10/2026 contra 15 números de referência do enunciado
e dos slides do professor — ver tests/test_base_analitica.py):
    1. Cortesias (60 contas) fora da base pagante.
    2. Ativo no corte: inicio <= 30/09/2026 e (data_fim vazia ou > 30/09).
    3. Pagamentos: normalização de valor, fuso Brasília e deduplicação
       funcional REAPROVEITADAS de src/reconciliacao_pagamentos.py.
    4. Churn mensal (dicionário §11): perda = assinatura ativa no INÍCIO do
       mês cujo fim cai no mês; quem entrou e saiu no mesmo mês fica fora do
       numerador. (Sem essa regra, set/26 daria 717 perdas em vez de 714.)
    5. Nenhuma variável usa informação posterior ao corte (anti-vazamento).

Uso:
    python src/base_analitica.py [data/raw]
Saídas (locais, fora do Git): reports/base_analitica_corte.csv,
reports/serie_churn_mensal.csv e um resumo impresso no terminal.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config.parametros import DATA_CORTE, FUSO, TAXAS
from src.reconciliacao_pagamentos import carregar_pagamentos, deduplicar_aprovados

CORTE = pd.Timestamp(DATA_CORTE)
CORTE_FIM = CORTE + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
J12_INI = (CORTE + pd.Timedelta(days=1) - pd.DateOffset(months=12)).normalize()
J90_INI = CORTE - pd.Timedelta(days=89)

ARQUIVOS = [
    "usuarios.csv", "assinaturas.csv", "eventos_assinatura.csv",
    "pagamentos.csv", "uso_mensal.csv", "atividades.parquet",
    "onboarding.csv", "amizades.csv", "feed_posts.csv",
    "tickets_suporte.csv", "campanha_ago26.csv", "pesquisa_saida.csv",
]


def to_brt(s: pd.Series) -> pd.Series:
    """Mesma regra de carregar_pagamentos: 'Z'/offset = UTC; sem fuso = Brasília."""
    s = s.astype(str)
    com_tz = s.str.contains(r"Z|\+", regex=True, na=False)
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    if com_tz.any():
        out.loc[com_tz] = (pd.to_datetime(s[com_tz], utc=True)
                           .dt.tz_convert(FUSO).dt.tz_localize(None))
    if (~com_tz).any():
        out.loc[~com_tz] = pd.to_datetime(s[~com_tz])
    return out


def serie_churn_mensal(ass_pag: pd.DataFrame) -> pd.DataFrame:
    """Churn oficial (dicionário §11), jan/2025 até o corte."""
    meses = pd.period_range("2025-01", CORTE, freq="M")
    linhas = []
    for m in meses:
        ini, fim = m.start_time, m.end_time.normalize()
        ativos = ((ass_pag.inicio < ini)
                  & (ass_pag.data_fim.isna() | (ass_pag.data_fim >= ini))).sum()
        perdas = ((ass_pag.inicio < ini) & ass_pag.data_fim.between(ini, fim)).sum()
        linhas.append({"mes": str(m), "ativos_inicio": int(ativos),
                       "perdas": int(perdas),
                       "churn_pct": round(100 * perdas / ativos, 2)})
    return pd.DataFrame(linhas)


def construir_base(raw: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (base 1-linha-por-assinante, série de churn mensal)."""
    # -------------------------------------------------- assinaturas
    ass = pd.read_csv(raw / "assinaturas.csv", parse_dates=["inicio", "data_fim"])
    ass_pag = ass[ass.plano_atual != "cortesia"].copy()
    ativos = ass_pag[(ass_pag.inicio <= CORTE)
                     & (ass_pag.data_fim.isna() | (ass_pag.data_fim > CORTE))].copy()
    assert ativos.user_id.is_unique, "usuário com 2 assinaturas ativas no corte"
    serie = serie_churn_mensal(ass_pag)

    # -------------------------------------------------- pagamentos (pipeline validado)
    pag = carregar_pagamentos(str(raw / "pagamentos.csv"))
    ap_dedup, dups = deduplicar_aprovados(pag)
    ap_dedup["liquido"] = ap_dedup.valor_num * (1 - ap_dedup.metodo.map(TAXAS))
    ap_corte = ap_dedup[ap_dedup.dt_brt <= CORTE_FIM]

    ult = (ap_corte[ap_corte.valor_num > 0]
           .sort_values(["dt_brt", "pagamento_id"])
           .groupby("user_id").tail(1).set_index("user_id"))
    rec_12m = (ap_corte[ap_corte.dt_brt >= J12_INI]
               .groupby("user_id").liquido.sum().round(2))
    n_aprov = ap_corte.groupby("user_id").size()
    rec_mask = (pag.status == "recusado") & pag.dt_brt.between(J12_INI, CORTE_FIM)
    n_recusas_12m = pag[rec_mask].groupby("user_id").size()
    teve_dup = set(dups.user_id)

    # -------------------------------------------------- eventos de assinatura
    ev = pd.read_csv(raw / "eventos_assinatura.csv")
    ev["dt"] = to_brt(ev.data_hora)
    ev = ev[ev.dt <= CORTE_FIM]
    n_renov = ev[ev.evento == "renovacao"].groupby("user_id").size()
    carencia = set(ev[(ev.evento == "periodo_carencia") & (ev.dt >= J12_INI)].user_id)
    sw = ev[ev.evento.isin(["renovacao_automatica_desligada",
                            "renovacao_automatica_religada"])]
    renov_off = (sw.sort_values("dt").groupby("user_id").evento.last()
                 == "renovacao_automatica_desligada")

    # -------------------------------------------------- cadastro e onboarding
    usu = pd.read_csv(raw / "usuarios.csv",
                      parse_dates=["data_cadastro", "data_nascimento"]).set_index("user_id")
    usu["idade"] = ((CORTE - usu.data_nascimento).dt.days / 365.25).round(0)
    usu["relogio"] = usu.relogio_conectado.fillna("nenhum").ne("nenhum")
    onb = (pd.read_csv(raw / "onboarding.csv").sort_values("respondido_em")
           .groupby("user_id").tail(1).set_index("user_id"))
    onb["tem_objetivo"] = (onb.objetivo_texto.notna()
                           & onb.objetivo_texto.astype(str).str.strip().ne(""))

    # -------------------------------------------------- uso mensal (jul–set/26)
    uso = pd.read_csv(raw / "uso_mensal.csv")
    u3 = uso[uso.mes.between("2026-07", "2026-09")]
    agg3 = u3.groupby("user_id").agg(
        atividades_ult3m=("atividades", "sum"),
        ar_livre_ult3m=("atividades_ar_livre", "sum"),
        video_ult3m=("atividades_video", "sum"),
        minutos_ult3m=("minutos", "sum"),
        dias_ativos_ult3m=("dias_ativos", "sum"),
        sessoes_ult3m=("sessoes_app", "sum"))
    piv = u3.pivot_table(index="user_id", columns="mes", values="atividades", aggfunc="sum")
    agg3["tendencia_atividades_jul_set"] = piv.get("2026-09", 0) - piv.get("2026-07", 0)
    u_prev = uso[uso.mes.between("2026-04", "2026-06")].groupby("user_id").atividades.mean()
    agg3["queda50_set_vs_t2"] = (piv.get("2026-09").reindex(agg3.index).fillna(0)
                                 < 0.5 * u_prev.reindex(agg3.index).fillna(0))

    # -------------------------------------------------- atividades (janela 90d)
    atv = pd.read_parquet(raw / "atividades.parquet")
    atv["dt"] = pd.to_datetime(atv.inicio)
    a90 = atv[atv.dt.between(J90_INI, CORTE_FIM)]
    f90 = a90.groupby("user_id").agg(n_treinos_90d=("atividade_id", "size"),
                                     minutos_90d=("duracao_min", "sum"),
                                     n_outdoor_90d=("gps_ok", "sum"))
    f90["n_treinos_companhia_90d"] = (a90[a90.treino_com.fillna("") != ""]
                                      .groupby("user_id").size())
    dias_ult_treino = (CORTE_FIM - atv[atv.dt <= CORTE_FIM]
                       .groupby("user_id").dt.max()).dt.days

    # -------------------------------------------------- rede, posts, suporte
    ami = pd.read_csv(raw / "amizades.csv", parse_dates=["desde"])
    ami = ami[ami.desde <= CORTE]
    posts = pd.read_csv(raw / "feed_posts.csv", parse_dates=["data_hora"])
    p90 = posts[posts.data_hora.between(J90_INI, CORTE_FIM)]
    tic = pd.read_csv(raw / "tickets_suporte.csv", parse_dates=["aberto_em"])
    t12 = tic[tic.aberto_em.between(J12_INI, CORTE_FIM)]

    # -------------------------------------------------- campanha e pesquisa
    camp = pd.read_csv(raw / "campanha_ago26.csv").set_index("user_id")
    camp["abriu_campanha"] = camp.abriu_push.fillna(False) | camp.abriu_email.fillna(False)
    pes = (pd.read_csv(raw / "pesquisa_saida.csv").sort_values("respondido_em")
           .groupby("user_id").tail(1).set_index("user_id"))

    # -------------------------------------------------- montagem
    b = ativos.set_index("user_id").rename(columns={
        "plano_atual": "plano", "inicio": "inicio_assinatura",
        "renovacao_automatica": "renov_auto_snapshot"})
    b["meses_de_casa"] = ((CORTE - b.inicio_assinatura).dt.days / 30.44).round(1)
    b["meses_ate_renovacao"] = np.where(
        b.plano.eq("anual"),
        (12 - (((CORTE - b.inicio_assinatura).dt.days / 30.44) % 12)).round(1), 1.0)
    b = b.join(usu[["data_cadastro", "idade", "sexo", "uf", "canal_aquisicao",
                    "sistema", "relogio"]])
    b["dias_desde_cadastro"] = (CORTE - b.data_cadastro.dt.normalize()).dt.days
    b["dias_cadastro_ate_assinar"] = (b.inicio_assinatura
                                      - b.data_cadastro.dt.normalize()).dt.days
    b = b.join(onb[["nivel", "dias_por_semana", "tem_objetivo"]])
    b = b.join(ult[["valor_num", "metodo", "dt_brt"]].rename(columns={
        "valor_num": "ultima_cobranca_valor", "metodo": "ultimo_metodo",
        "dt_brt": "ultima_cobranca_data"}))
    b["mrr"] = np.where(b.plano.eq("anual"),
                        b.ultima_cobranca_valor / 12, b.ultima_cobranca_valor)
    b["receita_liq_12m"] = rec_12m
    b["n_cobrancas_aprovadas_total"] = n_aprov
    b["n_recusas_12m"] = n_recusas_12m
    b["teve_duplicidade_pagto"] = b.index.isin(teve_dup)
    b["n_renovacoes"] = n_renov
    b["teve_carencia_12m"] = b.index.isin(carencia)
    b["renov_auto_off_eventos"] = renov_off.reindex(b.index).fillna(False)
    b = b.join(agg3)
    b["share_ar_livre_ult3m"] = (b.ar_livre_ult3m
                                 / b.atividades_ult3m.replace(0, np.nan)).round(3)
    b["share_video_ult3m"] = (b.video_ult3m
                              / b.atividades_ult3m.replace(0, np.nan)).round(3)
    b = b.join(f90)
    b["dias_desde_ultimo_treino"] = dias_ult_treino
    b["seguidores"] = ami.groupby("seguido_id").size()
    b["seguindo"] = ami.groupby("seguidor_id").size()
    b["n_posts_90d"] = p90.groupby("user_id").size()
    b["curtidas_90d"] = p90.groupby("user_id").curtidas.sum()
    b["n_tickets_12m"] = t12.groupby("user_id").size()
    b["ticket_cobranca_12m"] = b.index.isin(
        set(t12[t12.categoria_atendente.eq("cobranca")].user_id))
    b["ticket_cancelamento_12m"] = b.index.isin(
        set(t12[t12.categoria_atendente.str.contains("cancel", na=False)].user_id))
    b = b.join(camp[["grupo", "abriu_campanha", "clicou"]].rename(columns={
        "grupo": "grupo_campanha_ago26", "clicou": "clicou_campanha"}))
    b["respondeu_pesquisa_saida"] = b.index.isin(pes.index)
    b = b.join(pes[["motivo_principal"]].rename(
        columns={"motivo_principal": "motivo_pesquisa_saida"}))

    # Contagens ausentes = 0; campos de estado continuam vazios quando o fato
    # não existe (ex.: dias_desde_ultimo_treino vazio = nunca treinou em 2026).
    zeros = ["atividades_ult3m", "ar_livre_ult3m", "video_ult3m", "minutos_ult3m",
             "dias_ativos_ult3m", "sessoes_ult3m", "tendencia_atividades_jul_set",
             "n_treinos_90d", "minutos_90d", "n_outdoor_90d",
             "n_treinos_companhia_90d", "seguidores", "seguindo", "n_posts_90d",
             "curtidas_90d", "n_tickets_12m", "n_recusas_12m", "n_renovacoes",
             "n_cobrancas_aprovadas_total", "receita_liq_12m"]
    b[zeros] = b[zeros].fillna(0)
    b["queda50_set_vs_t2"] = b.queda50_set_vs_t2.fillna(False).astype(bool)
    return b.reset_index(), serie


def main() -> None:
    raw = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
    faltam = [a for a in ARQUIVOS if not (raw / a).exists()]
    if faltam:
        sys.exit(f"Arquivos ausentes em {raw}: {faltam} (ver data/README.md)")
    base, serie = construir_base(raw)

    saida = Path("reports")
    saida.mkdir(exist_ok=True)
    base.to_csv(saida / "base_analitica_corte.csv", index=False)
    serie.to_csv(saida / "serie_churn_mensal.csv", index=False)

    print(f"Base analítica: {len(base):,} assinantes × {base.shape[1]} variáveis")
    print(f"MRR no corte: R$ {base.mrr.sum():,.2f}")
    s = serie[serie.mes == "2026-09"].iloc[0]
    print(f"Churn set/26: {s.churn_pct}% ({s.perdas}/{s.ativos_inicio:,})")
    print(f"Mix de plano: {base.plano.value_counts().to_dict()}")
    print(f"Salvo em {saida}/base_analitica_corte.csv e {saida}/serie_churn_mensal.csv")


if __name__ == "__main__":
    main()
