#!/usr/bin/env python3
"""
camara.py - CLI para a API de Dados Abertos da Câmara dos Deputados
Uso: python3 camara.py <comando> [opções]

Comandos:
  agenda [data]           Agenda do dia (default: hoje). Data: YYYY-MM-DD
  deputado <nome>         Busca deputado por nome
  deputado-id <id>        Perfil completo de um deputado
  proposicao <id>         Detalhes de uma proposição
  buscar-pl <keywords>    Busca proposições por palavras-chave
  votacoes [data]         Votações no plenário (default: hoje)
  votos <votacao_id>      Votos individuais de uma votação
  comissao <sigla>        Busca comissão por sigla
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import date

BASE = "https://dadosabertos.camara.leg.br/api/v2"

def get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())

def fmt(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))

def agenda(data=None):
    d = data or date.today().isoformat()
    r = get("/eventos", {"dataInicio": d, "dataFim": d, "ordem": "ASC", "ordenarPor": "dataHoraInicio", "itens": 50})
    eventos = r.get("dados", [])
    if not eventos:
        print(f"Sem eventos para {d}.")
        return
    print(f"\n📅 Agenda da Câmara — {d}\n{'='*50}")
    for e in eventos:
        hora = e.get("dataHoraInicio", "")[-5:] if e.get("dataHoraInicio") else "?"
        orgaos = ", ".join(o.get("sigla","") for o in e.get("orgaos",[]))
        local = e.get("localCamara", {}).get("nome") or e.get("localExterno") or ""
        print(f"  {hora} | {orgaos:10} | {e.get('descricaoTipo',''):30} | {e.get('descricao','')[:60]}")
        if local:
            print(f"         Local: {local}")
    print()

def buscar_deputado(nome):
    r = get("/deputados", {"nome": nome, "idLegislatura": 57, "ordem": "ASC", "ordenarPor": "nome"})
    deps = r.get("dados", [])
    if not deps:
        print(f"Nenhum deputado encontrado para '{nome}'.")
        return
    print(f"\n👤 Deputados — '{nome}'\n{'='*50}")
    for d in deps:
        print(f"  ID {d['id']} | {d['nome']:40} | {d['siglaPartido']:12} | {d['siglaUf']}")
    print()

def deputado_id(dep_id):
    r = get(f"/deputados/{dep_id}")
    d = r.get("dados", {})
    nome = d.get("nomeCivil", d.get("ultimoStatus", {}).get("nome", ""))
    status = d.get("ultimoStatus", {})
    print(f"\n👤 {nome}")
    print(f"  Partido: {status.get('siglaPartido')} | UF: {status.get('siglaUf')}")
    print(f"  Situação: {status.get('situacao')}")
    print(f"  Gabinete: {status.get('gabinete', {}).get('nome')} sala {status.get('gabinete', {}).get('sala')}")
    print(f"  Email: {status.get('email')}")
    print(f"  URL foto: {status.get('urlFoto')}")
    print()

def proposicao(prop_id):
    r = get(f"/proposicoes/{prop_id}")
    p = r.get("dados", {})
    print(f"\n📄 {p.get('siglaTipo')} {p.get('numero')}/{p.get('ano')}")
    print(f"  Ementa: {p.get('ementa')}")
    print(f"  Apresentação: {p.get('dataApresentacao')}")
    print(f"  Status: {p.get('statusProposicao', {}).get('descricaoSituacao')}")
    print(f"  Órgão atual: {p.get('statusProposicao', {}).get('siglaOrgao')}")
    print(f"  Relator: {p.get('statusProposicao', {}).get('uriRelator')}")
    # tramitação
    tr = get(f"/proposicoes/{prop_id}/tramitacoes")
    trams = tr.get("dados", [])[-5:]
    if trams:
        print(f"\n  📋 Últimas 5 tramitações:")
        for t in trams:
            print(f"    {t.get('dataHora','')[:10]} | {t.get('siglaOrgao',''):8} | {t.get('descricaoSituacao','')[:50]}")
    print()

def buscar_pl(keywords, tipo="PL", ano=None):
    params = {"keywords": keywords, "siglaTipo": tipo, "ordem": "DESC", "ordenarPor": "id", "itens": 15}
    if ano:
        params["ano"] = ano
    r = get("/proposicoes", params)
    pls = r.get("dados", [])
    if not pls:
        print(f"Nenhuma proposição encontrada para '{keywords}'.")
        return
    print(f"\n📑 Proposições — '{keywords}'\n{'='*50}")
    for p in pls:
        print(f"  ID {p['id']} | {p['siglaTipo']} {p['numero']}/{p['ano']} | {p.get('dataApresentacao','')[:10]} | {p['ementa'][:70]}")
    print()

def votacoes(data=None):
    d = data or date.today().isoformat()
    r = get("/votacoes", {"dataInicio": d, "dataFim": d, "idOrgao": 180, "ordem": "DESC", "ordenarPor": "dataHoraRegistro", "itens": 20})
    vots = r.get("dados", [])
    if not vots:
        print(f"Sem votações no plenário em {d}.")
        return
    print(f"\n🗳️  Votações — Plenário — {d}\n{'='*50}")
    for v in vots:
        ap = "✅ APROVADA" if v.get("aprovacao") == 1 else "❌ REJEITADA" if v.get("aprovacao") == 0 else "⏳"
        print(f"  {v['id']} | {ap} | {v.get('descricao','')[:70]}")
    print()

def votos(votacao_id):
    r = get(f"/votacoes/{votacao_id}/votos")
    votos_list = r.get("dados", [])
    print(f"\n🗳️  Votos na votação {votacao_id}\n{'='*50}")
    contagem = {}
    for v in votos_list:
        voto = v.get("tipoVoto", "?")
        contagem[voto] = contagem.get(voto, 0) + 1
    for tipo, qtd in sorted(contagem.items(), key=lambda x: -x[1]):
        print(f"  {tipo:10}: {qtd}")
    print(f"  Total: {len(votos_list)}")
    print()

def comissao(sigla):
    r = get("/orgaos", {"sigla": sigla})
    orgs = r.get("dados", [])
    if not orgs:
        print(f"Comissão '{sigla}' não encontrada.")
        return
    org = orgs[0]
    print(f"\n🏛️  {org.get('nome')} ({org.get('sigla')})")
    print(f"  ID: {org['id']} | Tipo: {org.get('tipoOrgao')}")
    # Membros
    try:
        mr = get(f"/orgaos/{org['id']}/membros")
        membros = mr.get("dados", [])
        print(f"  Membros: {len(membros)}")
        for m in membros[:5]:
            print(f"    {m.get('nome',''):40} | {m.get('siglaPartido',''):8} | {m.get('titulo','')}")
        if len(membros) > 5:
            print(f"    ... e mais {len(membros)-5}")
    except Exception:
        pass
    print()

COMMANDS = {
    "agenda": lambda args: agenda(args[0] if args else None),
    "deputado": lambda args: buscar_deputado(" ".join(args)),
    "deputado-id": lambda args: deputado_id(args[0]),
    "proposicao": lambda args: proposicao(args[0]),
    "buscar-pl": lambda args: buscar_pl(" ".join(args)),
    "votacoes": lambda args: votacoes(args[0] if args else None),
    "votos": lambda args: votos(args[0]),
    "comissao": lambda args: comissao(args[0]),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    args = sys.argv[2:]
    try:
        COMMANDS[cmd](args)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
