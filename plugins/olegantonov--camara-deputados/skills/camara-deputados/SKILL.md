---
name: camara-deputados
description: "Monitor and research the Brazilian Chamber of Deputies (Câmara dos Deputados) legislative activity. Use when: (1) searching for bills/proposições by author, keyword, type or year, (2) checking today's or upcoming agenda/events, (3) looking up deputies (deputados) by name, party or state, (4) tracking voting results (votações) in plenary or committees, (5) checking committee (comissão) schedules and membership, (6) monitoring specific bills' tramitação/status, (7) retrieving deputy expenses (CEAP/cota parlamentar), (8) searching for frentes parlamentares, grupos de trabalho, (9) any question about the Câmara dos Deputados, deputies, or federal bills. Base URL: https://dadosabertos.camara.leg.br/api/v2 — no auth required, returns JSON."
---

# Câmara dos Deputados — API de Dados Abertos

Base URL: `https://dadosabertos.camara.leg.br/api/v2`
Docs/Swagger: `https://dadosabertos.camara.leg.br/swagger/api.html`
No authentication required. All endpoints return JSON.

## Common query params
- `itens` — page size (default 15, max 100)
- `pagina` — page number
- `ordem` — `ASC` or `DESC`
- `ordenarPor` — field name for sorting

---

## Key Endpoints

### Deputies (Deputados)
```
GET /deputados
  ?nome=         # name search
  ?siglaPartido= # party (e.g. PT, PL, MDB)
  ?siglaUf=      # state (e.g. SP, RJ, AM)
  ?idLegislatura=57  # current legislature
  ?ordem=ASC&ordenarPor=nome

GET /deputados/{id}           # full profile
GET /deputados/{id}/discursos # speeches
  ?dataInicio=YYYY-MM-DD&dataFim=YYYY-MM-DD
GET /deputados/{id}/despesas  # CEAP expenses
  ?ano=YYYY&mes=MM
GET /deputados/{id}/frentes   # parliamentary fronts
GET /deputados/{id}/ocupacoes # professional history
GET /deputados/{id}/orgaos    # committee memberships
```

### Bills / Proposições
```
GET /proposicoes
  ?siglaTipo=PL      # type: PL, PEC, MPV, PDC, PLP, etc.
  ?numero=123
  ?ano=2026
  ?autor=Nome        # author name (partial match)
  ?tema=             # topic id (see /referencias/temas)
  ?keywords=         # keywords
  ?dataApresentacaoInicio=YYYY-MM-DD
  ?dataApresentacaoFim=YYYY-MM-DD
  ?codSituacao=      # status code
  ?tramitacaoSenado=true  # bills currently in Senate
  ?ordem=DESC&ordenarPor=id

GET /proposicoes/{id}             # full detail
GET /proposicoes/{id}/autores     # authorship
GET /proposicoes/{id}/relacionadas# related bills
GET /proposicoes/{id}/temas       # topics
GET /proposicoes/{id}/tramitacoes # full history/status
GET /proposicoes/{id}/votacoes    # votes on this bill
```

### Votações (Voting)
```
GET /votacoes
  ?dataInicio=YYYY-MM-DD&dataFim=YYYY-MM-DD
  ?idOrgao=180       # 180 = Plenário
  ?siglaPartido=
  ?ordem=DESC&ordenarPor=dataHoraRegistro

GET /votacoes/{id}             # vote detail
GET /votacoes/{id}/votos       # individual votes per deputy
GET /votacoes/{id}/orientacoes # party orientations
```

### Events / Agenda (Eventos)
```
GET /eventos
  ?dataInicio=YYYY-MM-DD
  ?dataFim=YYYY-MM-DD
  ?siglaOrgao=       # committee sigla or PLEN for plenary
  ?codTipoEvento=    # see /referencias/tiposEvento
  ?codSituacao=      # see /referencias/situacoesEvento
  ?ordem=ASC&ordenarPor=dataHoraInicio

GET /eventos/{id}          # event detail
GET /eventos/{id}/deputados # attending deputies
GET /eventos/{id}/orgaos    # organizing bodies
GET /eventos/{id}/pauta     # agenda items
GET /eventos/{id}/votacoes  # votes in this session
```

### Committees (Órgãos / Comissões)
```
GET /orgaos
  ?sigla=CCJC        # committee abbreviation
  ?codTipoOrgao=     # type (see /referencias/tiposOrgao)
  ?nome=

GET /orgaos/{id}            # detail
GET /orgaos/{id}/eventos    # committee agenda
GET /orgaos/{id}/membros    # current membership
GET /orgaos/{id}/votacoes   # votes by committee
```

### Parties & Blocs (Partidos / Blocos)
```
GET /partidos?ordem=ASC&ordenarPor=sigla
GET /partidos/{id}
GET /partidos/{id}/membros

GET /blocos
GET /blocos/{id}
```

### Parliamentary Fronts (Frentes)
```
GET /frentes
GET /frentes/{id}
GET /frentes/{id}/membros
```

### Working Groups (Grupos de Trabalho)
```
GET /gruposTrabalho
GET /gruposTrabalho/{id}
GET /gruposTrabalho/{id}/membros
```

### Legislative Sessions (Legislaturas)
```
GET /legislaturas
GET /legislaturas/{id}
GET /legislaturas/{id}/mesa  # presiding board
```

### Reference Data
```
GET /referencias/deputados/codSituacao
GET /referencias/proposicoes/codSituacaoProposicao
GET /referencias/proposicoes/siglaTipo
GET /referencias/proposicoes/tema
GET /referencias/tiposEvento
GET /referencias/tiposOrgao
GET /referencias/uf
```

---

## Common Tasks

### Today's agenda
```bash
DATE=$(date +%Y-%m-%d)
curl "https://dadosabertos.camara.leg.br/api/v2/eventos?dataInicio=$DATE&dataFim=$DATE&ordem=ASC&ordenarPor=dataHoraInicio"
```

### Search bills by keyword
```bash
curl "https://dadosabertos.camara.leg.br/api/v2/proposicoes?keywords=transporte+público&ano=2026&ordem=DESC&ordenarPor=id&itens=20"
```

### Find a deputy
```bash
curl "https://dadosabertos.camara.leg.br/api/v2/deputados?nome=Marcos+Pontes&idLegislatura=57"
```

### Recent plenary votes
```bash
curl "https://dadosabertos.camara.leg.br/api/v2/votacoes?idOrgao=180&dataInicio=2026-03-01&ordem=DESC&ordenarPor=dataHoraRegistro&itens=10"
```

### Bill status / tramitação
```bash
curl "https://dadosabertos.camara.leg.br/api/v2/proposicoes/{id}/tramitacoes"
```

---

## Notes
- Legislature 57 = current (started Feb 2023)
- Plenário orgão id = 180
- CEAP data also available as bulk download: `https://www.camara.leg.br/cotas/Ano-{ano}.json.zip`
- Full API reference: see `references/api-endpoints.md` for parameter details
- Swagger UI: `https://dadosabertos.camara.leg.br/swagger/api.html`
