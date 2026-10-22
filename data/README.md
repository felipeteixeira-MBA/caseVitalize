# data/ — dados locais (NÃO versionados)

Esta pasta fica fora do Git (`.gitignore`). Para reproduzir as análises, coloque aqui os arquivos do data room da Vitaliza, exportados em 01/10/2026 com corte em 30/09/2026:

```
data/
└── raw/
    ├── usuarios.csv            (64.948 linhas)
    ├── assinaturas.csv         (32.643)
    ├── amizades.csv            (113.480)
    ├── campanha_ago26.csv      (14.120)
    ├── eventos_assinatura.csv  (275.565)
    ├── pagamentos.csv          (165.548)
    ├── uso_mensal.csv          (591.662)
    ├── atividades.parquet      (1.254.475)
    ├── onboarding.csv          (63.929)
    ├── pesquisa_saida.csv      (643)
    ├── tickets_suporte.csv     (4.422)
    └── heatmaps_90d/
        ├── 2026-07-31/   (12.426 PNGs)
        └── 2026-09-30/   (13.047 PNGs)
```

Motivos para não versionar: tamanho (o painel TIDY tem ~216 MB; o GitHub bloqueia arquivos >100 MB), e-mails/dados cadastrais fictícios mas em formato real, e materiais do curso.
