#!/usr/bin/env python3
"""Baixa arquivos em lote do Portal da Transparencia, devagar e com retomada.

Uso:
  python3 baixar_portal.py militares            # 2016-01..hoje (Militares, Reserva_Reforma, Pensionistas_DEFESA)
  python3 baixar_portal.py militares --de 2020-01 --ate 2025-12
  python3 baixar_portal.py renuncias            # renuncias fiscais 2016..2024

Comportamento:
  - 1 arquivo por vez, com pausa aleatoria entre downloads (--pausa, padrao 25-60 s)
  - pula o que ja foi baixado (pode interromper e rodar de novo)
  - valida que o arquivo e um ZIP; se vier pagina HTML (verificacao humana / 405),
    NAO tenta contornar: espera um tempo crescente e tenta de novo; apos
    --max-bloqueios seguidos, para e avisa para retomar depois.
"""
import argparse, os, random, sys, time, zipfile, datetime, urllib.request, urllib.error

BASE = "https://portaldatransparencia.gov.br/download-de-dados"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"
ORIGENS_MIL = {  # origem -> primeiro mes disponivel
    "Militares": (2013, 1),
    "Reserva_Reforma_Militares": (2020, 1),
    "Pensionistas_DEFESA": (2020, 1),
}


def meses(de, ate):
    y, m = de
    while (y, m) <= ate:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def parse_ym(s):
    y, m = s.split("-")
    return int(y), int(m)


def baixar(url, destino):
    """Retorna 'ok', 'bloqueado' ou 'inexistente'."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": BASE})
    tmp = destino + ".part"
    try:
        with urllib.request.urlopen(req, timeout=300) as r, open(tmp, "wb") as f:
            while chunk := r.read(1 << 20):
                f.write(chunk)
    except urllib.error.HTTPError as e:
        os.path.exists(tmp) and os.remove(tmp)
        return "inexistente" if e.code in (403, 404) else "bloqueado"
    except Exception:
        os.path.exists(tmp) and os.remove(tmp)
        return "bloqueado"
    if zipfile.is_zipfile(tmp):
        os.replace(tmp, destino)
        return "ok"
    os.remove(tmp)  # HTML de verificacao humana, etc.
    return "bloqueado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("conjunto", choices=["militares", "renuncias"])
    ap.add_argument("--de", default="2016-01")
    ap.add_argument("--ate", default=datetime.date.today().strftime("%Y-%m"))
    ap.add_argument("--saida", default="dados_portal")
    ap.add_argument("--pausa", default="25-60", help="intervalo em segundos, ex 25-60")
    ap.add_argument("--max-bloqueios", type=int, default=4)
    a = ap.parse_args()
    lo, hi = (float(x) for x in a.pausa.split("-"))

    fila = []
    if a.conjunto == "militares":
        for y, m in meses(parse_ym(a.de), parse_ym(a.ate)):
            for origem, ini in ORIGENS_MIL.items():
                if (y, m) >= ini:
                    nome = f"{y}{m:02d}_{origem}"
                    fila.append((f"{BASE}/servidores/{nome}", f"{nome}.zip"))
    else:
        for y in range(parse_ym(a.de)[0], parse_ym(a.ate)[0] + 1):
            fila.append((f"{BASE}/renuncias/{y}", f"renuncias_{y}.zip"))

    pasta = os.path.join(a.saida, a.conjunto)
    os.makedirs(pasta, exist_ok=True)
    pend = [(u, os.path.join(pasta, n)) for u, n in fila if not os.path.exists(os.path.join(pasta, n))]
    print(f"{len(fila)} arquivos na lista, {len(pend)} pendentes -> {pasta}")

    bloqueios = 0
    for i, (url, dest) in enumerate(pend, 1):
        while True:
            r = baixar(url, dest)
            if r == "ok":
                bloqueios = 0
                print(f"[{i}/{len(pend)}] ok  {os.path.basename(dest)}", flush=True)
                break
            if r == "inexistente":
                print(f"[{i}/{len(pend)}] nao existe  {os.path.basename(dest)}", flush=True)
                break
            bloqueios += 1
            if bloqueios > a.max_bloqueios:
                print("Portal pediu verificacao humana/bloqueou repetidamente. "
                      "Parando; rode de novo mais tarde (retoma de onde parou).")
                sys.exit(2)
            espera = 300 * bloqueios
            print(f"[{i}/{len(pend)}] bloqueado; aguardando {espera}s (tentativa {bloqueios}/{a.max_bloqueios})", flush=True)
            time.sleep(espera)
        time.sleep(random.uniform(lo, hi))
    print("Concluido.")


if __name__ == "__main__":
    main()
