# Dinheiro público: mapa ano a ano

Mapa de quanto o governo federal (e, onde há dado, estados e municípios) destinou a educação, saúde, segurança, assistência social, juros da dívida, INSS, servidores, militares e isenções fiscais, cruzado com o número de pessoas e empresas de cada grupo.

## Conteúdo
- `site/`: site estático (HTML/JS/CSS). Abra `site/index.html` ou hospede a pasta.
- `planilhas/`: listas e planilhas geradas (altos salários, gestoras e donos).
- `arrecadacao_despesas_2019_2026.xlsx`: planilha principal.
- `scripts/`: pipeline de coleta e agregação (Python/Bash).
- `FONTES_E_ARQUIVOS.csv`: índice das fontes com links oficiais.

## Dados brutos
Os arquivos originais (dezenas de GB do Portal da Transparência, CVM, Tesouro, BCB etc.) não estão no repositório. Use `FONTES_E_ARQUIVOS.csv` e os scripts `baixar_portal_v2.py` e `scripts/` para baixá-los de novo.

## Limites
Veja `site/metodologia.html`. Várias séries são estimadas ou aproximadas e estão marcadas como tal.

## Correções
Abra uma *issue* informando ano, grupo, valor encontrado e fonte.
