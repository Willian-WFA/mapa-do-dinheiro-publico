# Mapa do dinheiro público federal

Site estático (HTML + CSS + JavaScript), sem backend. Envie **todos** os arquivos desta pasta, inclusive `planilhas/`.

## Páginas
- `index.html` mapa e cards (pizza, séries ano a ano)
- `entenda.html` explicação simples para qualquer pessoa
- `vezes.html` quantas vezes mais cada grupo recebe por pessoa
- `gestoras.html` gestoras de fundos, donos e lucro dos bancos
- `salarios.html` pessoas acima de R$ 50 mil (Executivo, Senado, Judiciário, MP, militares)
- `dados.html` planilhas e fontes (informe a URL da sua cópia para gerar links)

## Dica de cache
Se o navegador mostrar uma versão antiga (links sem estilo, botão que não abre), force a atualização com Ctrl+Shift+R. Os arquivos têm `?v=` na referência para evitar isso.

## Hospedagem
Hostinger: enviar para `public_html/`. VPS (nginx): `root /var/www/mapa;` com `index index.html;`.
