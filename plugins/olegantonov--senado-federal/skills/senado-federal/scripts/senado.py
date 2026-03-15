#!/usr/bin/env python3
"""
senado.py - CLI para a API de Dados Abertos do Senado Federal
Uso: python3 senado.py <comando> [opções]

Comandos:
  senadores               Lista todos os senadores em exercício
  senador <nome>          Busca senador por nome
  senador-id <codigo>     Perfil completo de um senador
  agenda [data]           Agenda plenária (default: hoje). Data: YYYYMMDD ou YYYY-MM-DD
  agenda-comissoes [mes]  Agenda das comissões. Mês: YYYYMM (default: mês atual)
  votacoes <inicio> <fim> Votações no plenário. Datas: YYYYMMDD
  buscar-pl <assunto>     Busca matérias/proposições
  materia <sigla> <num> <ano>   Detalhes de uma matéria (ex: PL 1234 2026)
  materia-id <codigo>     Matéria pelo código interno
  tramitacao <codigo>     Histórico de tramitação de uma matéria
  comissoes               Lista comissões permanentes
"""

import sys
import json
import urllib.request
import urllib.parse
from datetime import date, datetime

BASE = "https://legis.senado.leg.br/dadosabertos"

def get(path, params=None):
    path = path if path.endswith(".json") else path + ".json"
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def norm_date(d):
    """Accept YYYY-MM-DD or YYYYMMDD, return YYYYMMDD."""
    return d.replace("-", "")

def senadores():
    r = get("/senador/lista/atual")
    sens = r["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    print(f"\n🏛️  Senadores em exercício ({len(sens)})\n{'='*60}")
    for s in sorted(sens, key=lambda x: x["IdentificacaoParlamentar"]["NomeParlamentar"]):
        i = s["IdentificacaoParlamentar"]
        print(f"  {i['CodigoParlamentar']:5} | {i['NomeParlamentar']:40} | {i['SiglaPartidoParlamentar']:12} | {i['UfParlamentar']}")
    print()

def buscar_senador(nome):
    r = get("/senador/lista/atual")
    sens = r["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    nome_lower = nome.lower()
    encontrados = [s for s in sens if nome_lower in s["IdentificacaoParlamentar"]["NomeParlamentar"].lower()]
    if not encontrados:
        print(f"Nenhum senador encontrado para '{nome}'.")
        return
    print(f"\n👤 Senadores — '{nome}'\n{'='*60}")
    for s in encontrados:
        i = s["IdentificacaoParlamentar"]
        print(f"  Código: {i['CodigoParlamentar']} | {i['NomeParlamentar']} | {i['SiglaPartidoParlamentar']}/{i['UfParlamentar']}")
        print(f"  Email: {i.get('EmailParlamentar','')} | {i.get('UrlPaginaParlamentar','')}")
    print()

def senador_id(codigo):
    r = get(f"/senador/{codigo}")
    d = r.get("DetalheParlamentar", {}).get("Parlamentar", {})
    i = d.get("IdentificacaoParlamentar", {})
    m = d.get("DadosBasicosParlamentar", {})
    print(f"\n👤 {i.get('NomeCompletoParlamentar')}")
    print(f"  Partido: {i.get('SiglaPartidoParlamentar')} | UF: {i.get('UfParlamentar')}")
    print(f"  Tratamento: {i.get('FormaTratamento')}")
    print(f"  Email: {i.get('EmailParlamentar')}")
    print(f"  Nascimento: {m.get('DataNascimento','')} | Naturalidade: {m.get('Naturalidade','')}")
    print(f"  Página: {i.get('UrlPaginaParlamentar')}")
    # mandatos
    try:
        mr = get(f"/senador/{codigo}/mandatos")
        mands = mr.get("MandatosParlamentar", {}).get("Parlamentar", {}).get("Mandatos", {}).get("Mandato", [])
        if isinstance(mands, dict):
            mands = [mands]
        print(f"\n  Mandatos: {len(mands)}")
        for m in mands[-2:]:
            print(f"    UF: {m.get('UfParlamentar')} | {m.get('PrimeiraLegislaturaDoMandato',{}).get('DataInicio','')} - {m.get('SegundaLegislaturaDoMandato',{}).get('DataFim','')}")
    except Exception:
        pass
    print()

def agenda(data=None):
    d = norm_date(data) if data else date.today().strftime("%Y%m%d")
    try:
        r = get(f"/plenario/agenda/dia/{d}")
        ag = r.get("AgendaDia", {})
        sessoes = ag.get("Sessoes", {}).get("Sessao", [])
        if isinstance(sessoes, dict):
            sessoes = [sessoes]
        print(f"\n📅 Agenda Plenário Senado — {d[:4]}-{d[4:6]}-{d[6:]}\n{'='*60}")
        if not sessoes:
            print("  Sem sessões plenárias neste dia.")
        for s in sessoes:
            print(f"  {s.get('HoraInicioSessao','?')[:5]} | {s.get('SiglasSessao',''):10} | {s.get('NomeSessao','')}")
    except Exception as e:
        print(f"  Sem dados de agenda para {d}: {e}")
    print()

def agenda_comissoes(mes=None):
    m = mes or date.today().strftime("%Y%m")
    try:
        r = get(f"/comissao/agenda/mes/{m}")
        ag = r.get("AgendaReunioesComissoes", {})
        reunioes = ag.get("Reunioes", {}).get("Reuniao", [])
        if isinstance(reunioes, dict):
            reunioes = [reunioes]
        print(f"\n🏛️  Agenda Comissões — {m}\n{'='*60}")
        for re in reunioes:
            dt = re.get("DataReuniao","")
            hr = re.get("HoraReuniao","")
            sigla = re.get("SiglaComissao","")
            desc = re.get("DescricaoReuniao","")[:60]
            print(f"  {dt} {hr[:5]} | {sigla:8} | {desc}")
    except Exception as e:
        print(f"  Erro ao buscar agenda de comissões: {e}")
    print()

def votacoes(inicio, fim):
    r = get(f"/plenario/lista/votacao/{norm_date(inicio)}/{norm_date(fim)}")
    vots = r.get("ListaVotacoes", {}).get("Votacoes", {}).get("Votacao", [])
    if isinstance(vots, dict):
        vots = [vots]
    if not vots:
        print(f"Sem votações entre {inicio} e {fim}.")
        return
    print(f"\n🗳️  Votações — Senado — {inicio} a {fim}\n{'='*60}")
    for v in vots:
        resultado = v.get("DescricaoResultado","")
        materia = v.get("IdentificacaoMateria","")
        sessao = v.get("SessaoPlenaria","")
        print(f"  {sessao[:10]} | {materia:20} | {resultado}")
    print()

def buscar_materia(assunto, sigla=None, tramitando="S"):
    params = {"assunto": assunto, "tramitando": tramitando}
    if sigla:
        params["sigla"] = sigla
    r = get("/materia/pesquisa/lista", params)
    mats = r.get("PesquisaBasicaMateria", {}).get("Materias", {}).get("Materia", [])
    if isinstance(mats, dict):
        mats = [mats]
    if not mats:
        print(f"Nenhuma matéria encontrada para '{assunto}'.")
        return
    print(f"\n📑 Matérias — '{assunto}'\n{'='*60}")
    for m in mats[:20]:
        # Nova estrutura da API pesquisa/lista
        codigo = m.get("Codigo", m.get("CodigoMateria", ""))
        desc = m.get("DescricaoIdentificacao", f"{m.get('Sigla','')} {m.get('Numero','')}/{m.get('Ano','')}")
        ementa = m.get("Ementa", m.get("EmentaMateria", ""))[:70]
        autor = m.get("Autor", "")
        data = m.get("Data", "")
        print(f"  {codigo:7} | {desc:20} | {data[:10]} | {ementa}")
        if autor:
            print(f"          Autor: {autor}")
    print()

def materia(sigla, numero, ano):
    r = get(f"/materia/pesquisa/lista", {"sigla": sigla, "numero": numero, "ano": ano})
    mats = r.get("PesquisaBasicaMateria", {}).get("Materias", {}).get("Materia", [])
    if isinstance(mats, dict):
        mats = [mats]
    if not mats:
        print(f"Matéria {sigla} {numero}/{ano} não encontrada.")
        return
    m = mats[0]
    i = m.get("IdentificacaoMateria", {})
    s = m.get("SituacaoAtual", {})
    codigo = i.get("CodigoMateria", "")
    print(f"\n📄 {sigla} {numero}/{ano} (código: {codigo})")
    print(f"  Ementa: {i.get('EmentaMateria','')}")
    print(f"  Situação: {s.get('DescricaoSituacao','')}")
    print(f"  Local atual: {s.get('Local','')}")
    if codigo:
        tramitacao(codigo)

def materia_id(codigo):
    r = get(f"/materia/situacaoatual/{codigo}")
    sit = r.get("SituacaoAtualMateria", {})
    i = sit.get("IdentificacaoMateria", {})
    s = sit.get("Autuacao", {})
    print(f"\n📄 Matéria {codigo}")
    print(f"  {i.get('SiglaSubtipoMateria','')} {i.get('NumeroMateria','')}/{i.get('AnoMateria','')}")
    print(f"  Ementa: {i.get('EmentaMateria','')}")
    print(f"  Situação: {s.get('DescricaoSituacao','')}")
    tramitacao(codigo)

def tramitacao(codigo):
    try:
        r = get(f"/materia/movimentacoes/{codigo}")
        movs = r.get("MovimentacaoMateria", {}).get("Materia", {}).get("Movimentacoes", {}).get("Movimentacao", [])
        if isinstance(movs, dict):
            movs = [movs]
        print(f"\n  📋 Tramitação (últimas 8):")
        for m in movs[-8:]:
            dt = m.get("DataMovimentacao","")
            desc = m.get("DescricaoMovimentacao","")[:60]
            local = m.get("DescricaoLocal","")
            print(f"    {dt} | {local:20} | {desc}")
    except Exception as e:
        print(f"  Tramitação não disponível: {e}")

def comissoes():
    r = get("/comissao/lista/colegiados")
    cols = r.get("ListaColegiados", {}).get("Colegiados", {}).get("Colegiado", [])
    if isinstance(cols, dict):
        cols = [cols]
    print(f"\n🏛️  Comissões Permanentes do Senado ({len(cols)})\n{'='*60}")
    for c in sorted(cols, key=lambda x: x.get("SiglaColegiado","")):
        print(f"  {c.get('CodigoColegiado',''):5} | {c.get('SiglaColegiado',''):10} | {c.get('NomeColegiado','')}")
    print()

COMMANDS = {
    "senadores": lambda args: senadores(),
    "senador": lambda args: buscar_senador(" ".join(args)),
    "senador-id": lambda args: senador_id(args[0]),
    "agenda": lambda args: agenda(args[0] if args else None),
    "agenda-comissoes": lambda args: agenda_comissoes(args[0] if args else None),
    "votacoes": lambda args: votacoes(args[0], args[1]),
    "buscar-pl": lambda args: buscar_materia(" ".join(args[3:]) if len(args) > 3 else args[0], sigla=args[0] if len(args) > 1 else None),
    "buscar": lambda args: buscar_materia(" ".join(args)),
    "materia": lambda args: materia(args[0], args[1], args[2]),
    "materia-id": lambda args: materia_id(args[0]),
    "tramitacao": lambda args: tramitacao(args[0]),
    "comissoes": lambda args: comissoes(),
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
        import traceback; traceback.print_exc()
        sys.exit(1)
