---
name: senado-federal
description: "Monitor and research the Brazilian Senate (Senado Federal) legislative activity. Use when: (1) searching for Senate bills/matérias by type, author, keyword or year, (2) checking today's or upcoming plenary/committee agenda, (3) looking up senators by name, party or state, (4) tracking voting results (votações) in plenary or committees, (5) checking committee (comissão) schedules and composition, (6) monitoring specific bill tramitação/status, (7) researching senator speeches (discursos/apartes), (8) checking senator mandates, affiliations, academic history, (9) any question about the Senado Federal, senators, or Senate legislative process. Base URL: https://legis.senado.leg.br/dadosabertos — no auth required, supports .json and .xml suffixes."
---

# Senado Federal — API de Dados Abertos

Base URL: `https://legis.senado.leg.br/dadosabertos`
Swagger: `https://legis.senado.leg.br/dadosabertos/api-docs/swagger-ui/index.html`
No authentication required.
**Format**: append `.json` or `.xml` to endpoint paths.

---

## Key Endpoints

### Senators (Senadores)
```
GET /senador/lista/atual.json           # all senators currently in office
GET /senador/afastados.json             # senators on leave
GET /senador/lista/legislatura/{leg}.json  # by legislature number (e.g. 57)
GET /senador/partidos.json              # party list

GET /senador/{codigo}.json              # full senator profile
GET /senador/{codigo}/mandatos.json     # mandate history
GET /senador/{codigo}/filiacoes.json    # party affiliations
GET /senador/{codigo}/cargos.json       # positions held
GET /senador/{codigo}/comissoes.json    # committee memberships
GET /senador/{codigo}/liderancas.json   # leadership roles
GET /senador/{codigo}/discursos.json    # speeches
  ?dataInicio=YYYYMMDD&dataFim=YYYYMMDD&tipoPronunciamento=
GET /senador/{codigo}/apartes.json      # interjections
GET /senador/{codigo}/autorias.json     # authored bills
GET /senador/{codigo}/relatorias.json   # reports authored
GET /senador/{codigo}/votacoes.json     # voting history
GET /senador/{codigo}/profissao.json    # professional background
GET /senador/{codigo}/historicoAcademico.json
GET /senador/{codigo}/licencas.json     # leave periods
```

### Bills / Matérias (API v2 — recommended)
```
GET /materia/pesquisa/lista.json
  ?sigla=PL          # type: PL, PEC, PLS, MSF, INC, etc.
  ?numero=123
  ?ano=2026
  ?autor=            # author name
  ?assunto=          # subject/keyword
  ?tramitando=S      # S=currently in progress
  ?codigoSituacao=

GET /materia/{codigo}.json              # by internal code
GET /materia/{sigla}/{numero}/{ano}.json  # e.g. /materia/PL/1234/2026.json
GET /materia/situacaoatual/{codigo}.json  # current status
GET /materia/votacoes/{codigo}.json     # votes on this bill
GET /materia/textos/{codigo}.json       # bill texts
GET /materia/emendas/{codigo}.json      # amendments
GET /materia/relatorias/{codigo}.json   # rapporteurs
GET /materia/autoria/{codigo}.json      # authorship
GET /materia/movimentacoes/{codigo}.json # full tramitação history
GET /materia/tramitando.json            # all currently in progress
GET /materia/legislaturaatual.json      # current legislature bills
GET /materia/atualizadas.json           # recently updated
  ?numdias=7         # last N days
```

### Plenary Agenda & Results (Plenário)
```
GET /plenario/agenda/dia/{data}.json     # e.g. /plenario/agenda/dia/20260304.json
GET /plenario/agenda/mes/{data}.json     # e.g. /plenario/agenda/mes/202603.json
GET /plenario/agenda/cn/{data}.json      # Congresso Nacional joint session agenda

GET /plenario/resultado/{data}.json      # plenary results for a date (YYYYMMDD)
GET /plenario/resultado/mes/{data}.json  # monthly results (YYYYMM)

GET /plenario/lista/votacao/{dataInicio}/{dataFim}.json  # votes in date range (YYYYMMDD)
GET /plenario/votacao/nominal/{ano}.json  # all nominal votes in a year

GET /plenario/lista/discursos/{dataInicio}/{dataFim}.json  # speeches
GET /plenario/lista/legislaturas.json
GET /plenario/legislatura/{data}.json

GET /plenario/encontro/{codigo}.json       # session detail
GET /plenario/encontro/{codigo}/pauta.json # session agenda
GET /plenario/encontro/{codigo}/resultado.json
GET /plenario/encontro/{codigo}/resumo.json
```

### Committees (Comissões)
```
GET /comissao/lista/colegiados.json      # all standing committees
GET /comissao/lista/mistas.json          # joint CN/Congresso committees
GET /comissao/lista/{tipo}.json          # by type

GET /comissao/{codigo}.json              # committee detail
GET /comissao/agenda/{dataReferencia}.json   # YYYYMMDD
GET /comissao/agenda/{dataInicio}/{dataFim}.json
GET /comissao/agenda/mes/{mesReferencia}.json  # YYYYMM
GET /comissao/agenda/atual/iCal          # iCal feed

GET /comissao/reuniao/{codigoReuniao}.json
GET /comissao/reuniao/notas/{codigoReuniao}.json

GET /composicao/comissao/{codigo}.json   # membership
GET /composicao/comissao/resumida/mista/{codigo}/{dataInicio}/{dataFim}.json
```

### Voting in Committees (VotaçãoComissão)
```
GET /votacaoComissao/comissao/{siglaComissao}.json
GET /votacaoComissao/materia/{sigla}/{numero}/{ano}.json
GET /votacaoComissao/parlamentar/{codigo}.json
```

### Voting (Geral)
```
GET /votacao.json
  ?dataInicio=YYYYMMDD&dataFim=YYYYMMDD
  ?codigoSessao=
```

### Leadership & Composition
```
GET /composicao/mesaSF.json           # Senate presiding board
GET /composicao/mesaCN.json           # CN presiding board
GET /composicao/lideranca.json        # leadership
GET /composicao/lista/liderancaSF.json
GET /composicao/lista/liderancaCN.json
GET /composicao/lista/partidos.json
GET /composicao/lista/blocos.json
GET /composicao/bloco/{codigo}.json
```

### Authors / Autores
```
GET /autor/lista/atual.json
GET /autor/tiposAutor.json
```

### Legislation / Normas
```
GET /legislacao/lista.json
  ?tipo=&ano=&numero=
GET /legislacao/{codigo}.json
GET /legislacao/urn.json?urn={urn}
```

### Taquigrafia (Transcripts)
```
GET /taquigrafia/notas/sessao/{idSessao}.json
GET /taquigrafia/notas/reuniao/{idReuniao}.json
GET /taquigrafia/videos/sessao/{idSessao}.json
GET /taquigrafia/videos/reuniao/{idReuniao}.json
```

### Speeches / Discursos
```
GET /discurso/texto-integral/{codigoPronunciamento}.json
GET /discurso/texto-binario/{codigoPronunciamento}.json
```

---

## Common Tasks

### Today's plenary agenda
```bash
DATE=$(date +%Y%m%d)
curl "https://legis.senado.leg.br/dadosabertos/plenario/agenda/dia/$DATE.json"
```

### Find a senator (search in lista/atual)
```bash
curl "https://legis.senado.leg.br/dadosabertos/senador/lista/atual.json" | \
  python3 -c "
import json,sys
data = json.load(sys.stdin)
senators = data['ListaParlamentarEmExercicio']['Parlamentares']['Parlamentar']
for s in senators:
    name = s['IdentificacaoParlamentar']['NomeParlamentar']
    if 'Pontes' in name:
        print(json.dumps(s, ensure_ascii=False, indent=2))
"
```

### Search bills
```bash
curl "https://legis.senado.leg.br/dadosabertos/materia/pesquisa/lista.json?sigla=PL&ano=2026&tramitando=S&assunto=transporte"
```

### Recent plenary votes
```bash
START=$(date -d '7 days ago' +%Y%m%d)
END=$(date +%Y%m%d)
curl "https://legis.senado.leg.br/dadosabertos/plenario/lista/votacao/$START/$END.json"
```

### Committee agenda (current month)
```bash
MONTH=$(date +%Y%m)
curl "https://legis.senado.leg.br/dadosabertos/comissao/agenda/mes/$MONTH.json"
```

### Bill tramitação
```bash
# By sigla/number/year:
curl "https://legis.senado.leg.br/dadosabertos/materia/movimentacoes/{codigo}.json"
```

---

## Notes
- Date formats vary: plenary agenda uses `YYYYMMDD`; senator speeches use `YYYYMMDD`; materia pesquisa uses `YYYY`
- Current legislature: 57 (started Feb 2023)
- Senator codes (CodigoParlamentar) found in `/senador/lista/atual.json`
- Materia codes (codigo) found in `/materia/pesquisa/lista.json` results
- API v1 `/materia/{sigla}/{numero}/{ano}` is deprecated since 2025; prefer `/processo` or `/materia/pesquisa/lista`
- iCal feed available for committee agenda: `/comissao/agenda/atual/iCal`
- Full endpoint list: see `references/api-endpoints.md`
