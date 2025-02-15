# Conversor de Insights para CSV

Este projeto é uma aplicação Flask que consome dados de uma API de insights de plataformas de anúncios e os converte para arquivos CSV, permitindo análises mais acessíveis e organizadas.

## Tecnologias Utilizadas
- Python 3
- Flask
- urllib.request
- JSON
- CSV

## Instalação e Execução

1. Clone o repositório:
```bash
git clone https://github.com/zPedroLuis/stract-ad-reporting.git
cd stract-ad-reporting
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install Flask
```

4. Execute a aplicação:
```bash
python src/app.py
```

A aplicação estará disponível em `http://127.0.0.1:5000/`.

## Endpoints Disponíveis

### `/` - Informações do Desenvolvedor
Retorna um arquivo CSV com informações do autor.

### `/<platform>` - Relatório Completo por Plataforma
Gera um relatório CSV com os insights de uma plataforma específica.

Exemplo: `http://127.0.0.1:5000/meta_ads`

### `/<platform>/resumo` - Resumo por Plataforma
Gera um CSV com a soma dos principais campos numéricos (cliques, impressões, etc.) para uma determinada plataforma.

Exemplo: `http://127.0.0.1:5000/meta_ads/resumo`

### `/geral` - Relatório Geral
Gera um CSV com dados de todas as plataformas disponíveis.

### `/geral/resumo` - Resumo Geral
Gera um CSV com a soma dos principais campos numéricos para todas as plataformas.

## Estrutura dos Arquivos CSV
Os arquivos gerados possuem os seguintes campos principais:
- Platform
- Account Name
- ad_name
- clicks
- impressions
- spend
- cpc
- ctr
- ctr_unique

## Observações
- O formato CSV é gerado com suporte a BOM para melhor compatibilidade com editores como o Excel.

