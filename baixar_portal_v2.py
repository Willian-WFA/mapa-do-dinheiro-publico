#!/usr/bin/env python3
"""Baixador gentil de dados abertos (Portal da Transparencia, Tesouro, Camara, Senado).

  python3 baixar_portal_v2.py listar                      # conjuntos do portal e quantidade de arquivos
  python3 baixar_portal_v2.py portal --conjuntos servidores,renuncias --de 2016-01 --ate 2026-12
  python3 baixar_portal_v2.py portal --conjuntos servidores --origens Militares,Reserva_Reforma_Militares,Pensionistas_DEFESA
  python3 baixar_portal_v2.py portal --conjuntos todos                 # tudo, exceto os PESADOS
  python3 baixar_portal_v2.py portal --conjuntos todos --incluir-pesados
  python3 baixar_portal_v2.py externos --fontes tesouro,camara,senado --de 2016 --ate 2026
  python3 baixar_portal_v2.py externos --fontes judiciario,cvm,rmd --de 2016 --ate 2026
      judiciario = remuneracoes de tribunais/conselhos (DadosJusBr); cvm = carteiras de fundos (titulos publicos
      por gestora/administradora); rmd = Relatorio Mensal da Divida (PDF, detentores por categoria)
  python3 baixar_portal_v2.py atualizar-catalogo                      # re-le o portal e regrava o catalogo

Regras: 1 arquivo por vez, pausa aleatoria, retoma de onde parou (pula o que existe).
Se o portal devolver pagina de verificacao humana (WAF), espera e tenta de novo
algumas vezes e PARA. Nao tenta contornar a verificacao.
"""
import argparse, json, os, random, re, sys, time, zipfile, datetime, urllib.request, urllib.error

AQUI = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
PORTAL = "https://portaldatransparencia.gov.br/download-de-dados"
CATALOGO = os.path.join(AQUI, "catalogo_portal.json")
# conjuntos com muitos GB (centenas ou milhares de arquivos grandes): so com --incluir-pesados
PESADOS = {"despesas", "despesas-favorecidos", "despesas-execucao", "notas-fiscais", "compras",
           "favorecidos-pj", "transferencias", "cpgf", "cpdc", "licitacoes", "bolsa-familia-pagamentos",
           "bolsa-familia-saques", "auxilio-emergencial", "novo-bolsa-familia", "garantia-safra",
           "seguro-defeso", "peti", "bpc"}
TESOURO_DATASETS = ["resultado-do-tesouro-nacional", "investidores-do-tesouro-direto", "vendas-do-tesouro-direto",
                    "resgates-do-tesouro-direto", "operacoes-do-tesouro-direto", "estoque-do-tesouro-direto",
                    "taxas-dos-titulos-ofertados-pelo-tesouro-direto", "estoque-da-divida-publica-federal",
                    "fatores-de-variacao-da-divida-publica-federal", "ds013",
                    "emissoes-e-resgates-divida-publica-federal", "despesas-e-transferencias-totais"]
CAMARA = ["https://www.camara.leg.br/cotas/Ano-{y}.csv.zip"]
SENADO = ["https://www.senado.leg.br/transparencia/LAI/verba/despesa_ceaps_{y}.csv"]


def http(url, timeout=300, ref=None):
    h = {"User-Agent": UA}
    if ref: h["Referer"] = ref
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout)


def baixar(url, dest, tipo="zip"):
    """'ok' | 'bloqueado' | 'inexistente'"""
    tmp = dest + ".part"
    try:
        with http(url, ref=PORTAL) as r, open(tmp, "wb") as f:
            while c := r.read(1 << 20):
                f.write(c)
    except urllib.error.HTTPError as e:
        rm(tmp)
        return "inexistente" if e.code in (403, 404) else "bloqueado"
    except Exception:
        rm(tmp)
        return "bloqueado"
    with open(tmp, "rb") as f:
        ini = f.read(512).lstrip().lower()
    html = ini.startswith(b"<!doctype html") or ini.startswith(b"<html")
    if (tipo == "zip" and not zipfile.is_zipfile(tmp)) or html:
        rm(tmp)
        return "bloqueado" if tipo == "zip" or html else "inexistente"
    os.replace(tmp, dest)
    return "ok"


def rm(p):
    try: os.remove(p)
    except OSError: pass


def executar(fila, pausa, max_bloq):
    """fila: lista de (url, destino, tipo)."""
    pend = [x for x in fila if not os.path.exists(x[1])]
    print(f"{len(fila)} na lista, {len(pend)} pendentes", flush=True)
    lo, hi = pausa
    bloq = 0
    for i, (url, dest, tipo) in enumerate(pend, 1):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        while True:
            r = baixar(url, dest, tipo)
            nome = os.path.relpath(dest)
            if r == "ok":
                bloq = 0; print(f"[{i}/{len(pend)}] ok  {nome}", flush=True); break
            if r == "inexistente":
                print(f"[{i}/{len(pend)}] nao existe  {nome}", flush=True); break
            bloq += 1
            if bloq > max_bloq:
                print("Bloqueado/verificacao humana repetida. Parando; rode de novo mais tarde (retoma).")
                sys.exit(2)
            esp = 300 * bloq
            print(f"[{i}/{len(pend)}] bloqueado; aguardando {esp}s ({bloq}/{max_bloq})", flush=True)
            time.sleep(esp)
        time.sleep(random.uniform(lo, hi))
    print("Concluido.")


# ---------- Portal da Transparencia ----------
def descobrir():
    idx = http(PORTAL, 60).read().decode("utf8", "ignore")
    slugs = sorted(set(re.findall(r'href="/download-de-dados/([a-z0-9-]+)"', idx)))
    cat = {}
    for s in slugs:
        h = http(f"{PORTAL}/{s}", 60).read().decode("utf8", "ignore")
        if "Human Verification" in h[:2000]:
            print(s, "WAF - pare e tente depois"); break
        ents = re.findall(r'arquivos\.push\(\{"ano" : "(\d+)", "mes" : "(\d*)", "dia" : "(\d*)", "origem" :\s+"([^"]*)"', h)
        ctor = re.search(r'new DownloadPlanilhas\("[^"]+", arquivos, "([A-Z_]+)"', h)
        cat[s] = {"ctor": f'"{s}", arquivos, "{ctor.group(1) if ctor else "ANO"}", url', "arquivos": ents}
        print(s, len(ents), flush=True)
        time.sleep(3)
    json.dump(cat, open(CATALOGO, "w"), ensure_ascii=False)


def modo(c):
    return re.search(r'arquivos, "([A-Z_]+)"', c["ctor"]).group(1)


def ym(s):
    s = str(s); y = int(s[:4]); m = int(s[5:7]) if len(s) >= 7 else None
    return y, m


def fila_portal(cat, slug, de, ate, origens, meses=None):
    c = cat[slug]; md = modo(c); out = set()
    if md == "UNICO":
        return [(f"{PORTAL}/{slug}/UNICO", "UNICO")]
    for ano, mes, dia, origem in c["arquivos"]:
        if int(ano) < 2000: continue
        y = int(ano); m = int(mes) if mes else None
        if not (de[0] <= y <= ate[0]): continue
        if m is not None and (y, m) < (de[0], de[1] or 1): continue
        if m is not None and (y, m) > (ate[0], ate[1] or 12): continue
        if origens and origem not in origens: continue
        if meses and m is not None and m not in meses: continue
        if md == "ANO": nome = f"{ano}"
        elif md == "ANO_MES": nome = f"{ano}{mes}"
        elif md in ("DIA", "ANO_MES_DIA"): nome = f"{ano}{mes}{dia}"
        elif md == "ANO_MES_ORIGEM": nome = f"{ano}{mes}_{origem}"
        elif md == "ORIGEM_ANO_MES_DIA": nome = f"{ano}{mes}{dia}_{origem}"
        elif md == "UNICO": nome = "UNICO"
        else: nome = f"{ano}{mes}{dia}"
        out.add(nome)
    return [(f"{PORTAL}/{slug}/{n}", n) for n in sorted(out)]


# ---------- externos ----------
def fila_externos(fontes, de, ate, saida):
    f = []
    for fonte in fontes:
        if fonte == "tesouro":
            for ds in TESOURO_DATASETS:
                try:
                    j = json.load(http(f"https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id={ds}", 60))
                except Exception as e:
                    print("tesouro", ds, "erro", e); continue
                for r in j["result"]["resources"]:
                    u = r.get("url") or ""
                    if u.startswith("http") and u.rsplit(".", 1)[-1].lower() in ("csv", "xlsx", "xls", "zip", "pdf"):
                        f.append((u, os.path.join(saida, "tesouro", ds, os.path.basename(u)), "livre"))
        elif fonte == "camara":
            for y in range(de, ate + 1):
                for t in CAMARA: f.append((t.format(y=y), os.path.join(saida, "camara", f"cota_parlamentar_{y}.csv.zip"), "zip"))
        elif fonte == "senado":
            for y in range(de, ate + 1):
                for t in SENADO: f.append((t.format(y=y), os.path.join(saida, "senado", f"ceaps_{y}.csv"), "livre"))
    return f


def fila_judiciario(de, ate, saida, incluir_mp):
    """DadosJusBr: pacote mensal de remuneracoes por orgao (tribunais e conselhos)."""
    orgaos = json.load(http("https://api.dadosjusbr.org/v2/orgaos", 60))
    f = []
    for o in orgaos:
        if o.get("entidade") == "Ministério" and not incluir_mp: continue
        oid = o["id_orgao"]
        for y in range(de, ate + 1):
            try:
                meses = json.load(http(f"https://api.dadosjusbr.org/v2/dados/{oid}/{y}", 60))
            except Exception:
                continue
            for m in meses or []:
                u = (m.get("pacote_de_dados") or {}).get("url")
                if u: f.append((u, os.path.join(saida, "judiciario", oid, os.path.basename(u)), "zip"))
            time.sleep(0.3)
    return f


def fila_cvm(de, ate, saida):
    b = "https://dados.cvm.gov.br/dados/FI"
    f = [(f"{b}/CAD/DADOS/cad_fi.csv", os.path.join(saida, "cvm", "cad_fi.csv"), "livre")]
    for y in range(de, ate + 1):
        if y <= 2022:
            f.append((f"{b}/DOC/CDA/DADOS/HIST/cda_fi_{y}.zip", os.path.join(saida, "cvm", f"cda_fi_{y}.zip"), "zip"))
        else:
            for m in range(1, 13):
                if (y, m) <= (datetime.date.today().year, datetime.date.today().month):
                    f.append((f"{b}/DOC/CDA/DADOS/cda_fi_{y}{m:02d}.zip", os.path.join(saida, "cvm", f"cda_fi_{y}{m:02d}.zip"), "zip"))
    return f


def fila_rmd(de, ate, saida):
    """Relatorio Mensal da Divida (PDF) - traz a tabela de detentores por categoria."""
    f = []; hoje = datetime.date.today()
    for y in range(de, ate + 1):
        for m in range(1, 13):
            if (y, m) > (hoje.year, hoje.month): continue
            dest = os.path.join(saida, "rmd", f"RMD_{y}{m:02d}.pdf")
            if os.path.exists(dest): continue
            try:
                h = http(f"https://www.tesourotransparente.gov.br/publicacoes/relatorio-mensal-da-divida-rmd/{y}/{m}", 60).read().decode("utf8", "ignore")
                pid = re.search(r"thot-arquivos\.tesouro\.gov\.br/publicacao/(\d+)", h)
                if not pid: continue
                v = http(f"https://thot-arquivos.tesouro.gov.br/publicacao/{pid.group(1)}", 60).read().decode("utf8", "ignore")
                src = re.search(r"iframe src='([^']+)'", v)
                if src: f.append((src.group(1), dest, "livre"))
            except Exception:
                continue
            time.sleep(1)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["listar", "portal", "externos", "atualizar-catalogo"])
    ap.add_argument("--conjuntos", default="")
    ap.add_argument("--origens", default="")
    ap.add_argument("--fontes", default="tesouro,camara,senado")
    ap.add_argument("--de", default="2016-01")
    ap.add_argument("--ate", default=datetime.date.today().strftime("%Y-%m"))
    ap.add_argument("--saida", default=os.path.join(AQUI, "dados_portal"))
    ap.add_argument("--pausa", default="25-60")
    ap.add_argument("--max-bloqueios", type=int, default=4)
    ap.add_argument("--incluir-pesados", action="store_true")
    ap.add_argument("--meses", default="", help="portal: so estes meses, ex 12 ou 6,12")
    ap.add_argument("--incluir-mp", action="store_true", help="judiciario: inclui Ministerios Publicos")
    a = ap.parse_args()
    pausa = tuple(float(x) for x in a.pausa.split("-"))
    if a.cmd == "atualizar-catalogo": return descobrir()
    cat = json.load(open(CATALOGO))
    if a.cmd == "listar":
        for s, c in sorted(cat.items()):
            anos = sorted({x[0] for x in c["arquivos"] if int(x[0]) >= 2000})
            print(f"{s:42} {modo(c):20} {len(c['arquivos']):5} arq  {anos[0] if anos else '-'}-{anos[-1] if anos else '-'}  {'PESADO' if s in PESADOS else ''}")
        return
    if a.cmd == "externos":
        de, ate = int(a.de[:4]), int(a.ate[:4])
        for fonte in a.fontes.split(","):
            print(f"=== {fonte} ===", flush=True)
            if fonte == "judiciario": fila, p = fila_judiciario(de, ate, a.saida, a.incluir_mp), (0.5, 1.5)
            elif fonte == "cvm": fila, p = fila_cvm(de, ate, a.saida), (2, 6)
            elif fonte == "rmd": fila, p = fila_rmd(de, ate, a.saida), (3, 8)
            else: fila, p = fila_externos([fonte], de, ate, a.saida), pausa
            executar(fila, p, a.max_bloqueios)
        return
    de, ate = ym(a.de), ym(a.ate)
    if a.conjuntos in ("", "todos"):
        slugs = [s for s in sorted(cat) if a.incluir_pesados or s not in PESADOS]
    else:
        slugs = a.conjuntos.split(",")
    origens = set(filter(None, a.origens.split(",")))
    fila = []
    for s in slugs:
        if s not in cat: print("conjunto desconhecido:", s); continue
        for url, nome in fila_portal(cat, s, de, ate, origens, set(int(x) for x in a.meses.split(',') if x)):
            fila.append((url, os.path.join(a.saida, s, nome + ".zip"), "zip"))
    executar(fila, pausa, a.max_bloqueios)


if __name__ == "__main__":
    main()
