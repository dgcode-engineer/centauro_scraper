# Centauro Scraper API

API assíncrona para raspagem de produtos do site [centauro.com.br](https://www.centauro.com.br), construída com FastAPI e Selenium (undetected-chromedriver). Os resultados são persistidos em SQLite e expostos via endpoints REST.

## Requisitos (execução local)

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Google Chrome instalado

## Instalação

```bash
git clone <repo>
cd centauro_scraper
uv sync
```

## Rodando o servidor

```bash
uv run uvicorn app.main:app --reload
```

A documentação interativa fica disponível em `http://localhost:8000/docs`.

---

## Docker ( EM TESTE )

### Build e execução rápida

```bash
docker build -t centauro-scraper .
docker run -p 8000:8000 centauro-scraper
```

### Com docker-compose (recomendado)

```bash
docker compose up --build
```

O volume `./data` é montado em `/app/data` para persistir o `scraper.db` entre reinicializações.

> **Nota:** dentro do container o Chrome roda no modo `--headless=new` via a variável de ambiente `HEADLESS=true`.
> A variável `CHROME_VERSION` pode ser ajustada se precisar de uma versão específica do ChromeDriver.

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Verifica se a API está no ar |
| `POST` | `/scrape` | Inicia um job de scraping |
| `GET` | `/scrape/{job_id}` | Consulta o status e resultado do job |

---

## Casos de uso

### 1. Buscar tênis Nike em 2 páginas

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"query": "tenis nike", "pages": 2}'
```

Resposta imediata (202 Accepted):

```json
{
  "job_id": "a3f1c2d4-...",
  "status": "pending"
}
```

### 2. Acompanhar o progresso do job

```bash
curl http://localhost:8000/scrape/a3f1c2d4-...
```

Enquanto o Chrome ainda está navegando:

```json
{
  "job_id": "a3f1c2d4-...",
  "status": "running",
  "result": null,
  "error": null
}
```

Quando concluído:

```json
{
  "job_id": "a3f1c2d4-...",
  "status": "done",
  "result": [
    {
      "nome": "Tênis Feminino Nike Revolution 8",
      "image": "https://imgcentauro-a.akamaihd.net/...",
      "link": "https://www.centauro.com.br/tenis-feminino-nike-...",
      "tags": "17 cores\n7 tamanhos",
      "preco_atual": 299.99,
      "preco_antigo": 399.99,
      "desconto_pct": 25,
      "no_pix": true,
      "parcelamento": "ou 4x de R$ 78,94"
    }
  ],
  "error": null
}
```

### 3. Buscar chuteiras em 1 página (padrão)

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{"query": "chuteira adidas"}'
```

### 4. Verificar saúde da API

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## Estrutura do projeto

```
centauro_scraper/
├── app/
│   ├── main.py            # entry point FastAPI
│   ├── api/
│   │   └── products.py    # rotas + background tasks
│   ├── scraper/
│   │   ├── driver.py      # cria instância do Chrome (suporta HEADLESS)
│   │   ├── parser.py      # extração e parsing de preços
│   │   └── centauro.py    # lógica de navegação e scraping
│   ├── models/
│   │   └── product.py     # schemas Pydantic
│   ├── db/
│   │   └── database.py    # SQLite (jobs + products)
│   └── core/
│       └── logger.py      # logger estruturado em JSON
├── xpath.py               # builder de XPath customizado
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## Observações

- Cada job abre e fecha sua própria instância do Chrome em background task.
- Os resultados são persistidos em `scraper.db` (SQLite) e sobrevivem a reinicializações do servidor.
- O `undetected-chromedriver` requer que a versão do Chrome instalado corresponda ao parâmetro `version_main` em `app/scraper/driver.py` (padrão: `147`). No Docker, use a variável `CHROME_VERSION` para ajustar.
- Em ambiente Docker, defina `HEADLESS=true` para rodar o Chrome sem interface gráfica (já configurado por padrão no `docker-compose.yml`).
