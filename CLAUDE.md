# Projeto Vitaliza · grupo 06

## O case
A Vitaliza é um app de assinatura para quem treina. O grupo estuda a saída de assinantes: quem sai, por quê e em quem vale a pena agir. Enunciado e dicionário de dados estão em docs/.
Resumo do case, premissas e dicionário: leia docs/contexto_case.md antes de qualquer análise.

## Os dados
- Os arquivos originais estão em dados/brutos/. Nunca altere, mova ou apague esses arquivos.
- Tabelas intermediárias ficam em dados/processados/; resultados e relatórios em saidas/.
- Data de corte: 30/09/2026. Nenhuma análise usa informação posterior ao corte.
- Horários nos arquivos podem estar em UTC (Z): converter para Brasília antes de comparar.
- Contas de teste (e-mail @vitaliza.com.br) não contam.

## Como trabalhar
- Antes de uma tarefa com mais de um passo, apresente o plano e espere a aprovação.
- Mostre a contagem de linhas depois de cada filtro e de cada junção.
- Resuma tabelas de muitos registros por user_id antes de juntar, para não multiplicar linhas.
- Código em src/ ou notebooks/; nunca edite os dados brutos, só gere cópias em dados/processados/.
- Registre cada decisão de limpeza (corrigir, remover ou marcar) em decisoes.md, com o motivo e o efeito na contagem.

## O que não fazer
- Não coloque chaves de API, senhas ou tokens em nenhum arquivo do projeto.
- Não processe o data room inteiro de uma vez: use só os arquivos que a pergunta da vez pede.
