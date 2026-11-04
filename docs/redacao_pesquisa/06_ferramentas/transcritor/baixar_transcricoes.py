"""Baixa transcrições do YouTube em lote (canal, busca por palavra-chave ou links).

Uso (da pasta do projeto):
  python docs/redacao_pesquisa/06_ferramentas/transcritor/baixar_transcricoes.py canal https://www.youtube.com/@metodoquestiona --top 15
  python docs/redacao_pesquisa/06_ferramentas/transcritor/baixar_transcricoes.py busca "redação enem 2026 modelo" --top 20
  python docs/redacao_pesquisa/06_ferramentas/transcritor/baixar_transcricoes.py links https://youtu.be/VRQtqA3Fbeo https://youtu.be/xxxx

Opções: --top N (quantos vídeos), --ordem populares|recentes (só canal), --pool N (quantos
vídeos do canal olhar antes de ordenar, padrão 200), --min-min M (ignora vídeo curto, em minutos).
Saída: docs/redacao_pesquisa/06_ferramentas/transcritor/saida/<canal>/<data>_<id>.txt (fora do git).
Depende de: yt-dlp e youtube-transcript-api.
"""
import argparse
import re
import sys
import time
from pathlib import Path

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

SAIDA = Path(__file__).parent / "saida"
IDIOMAS = ["pt", "pt-BR", "pt-PT"]


def listar(fonte, valor, pool):
    """Devolve lista de dicts (id, titulo, canal, views, duracao) sem baixar vídeo."""
    opts = {"quiet": True, "extract_flat": True, "skip_download": True, "ignoreerrors": True}
    if fonte == "canal":
        alvo = valor.rstrip("/")
        if not re.search(r"/(videos|shorts|streams)$", alvo):
            alvo += "/videos"
        opts["playlistend"] = pool
    elif fonte == "busca":
        alvo = f"ytsearch{pool}:{valor}"
    else:
        alvo = valor
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(alvo, download=False)
    entradas = info.get("entries") or [info]
    saida = []
    for e in entradas:
        if not e or not e.get("id"):
            continue
        saida.append({
            "id": e["id"],
            "titulo": e.get("title") or e["id"],
            "canal": e.get("channel") or e.get("uploader") or info.get("channel") or info.get("uploader") or "sem_canal",
            "views": e.get("view_count") or 0,
            "duracao": e.get("duration") or 0,
        })
    return saida


def nome_seguro(texto):
    return re.sub(r"[^\w\-]+", "_", texto, flags=re.UNICODE).strip("_")[:60]


def baixar_transcricao(video_id):
    api = YouTubeTranscriptApi()
    trechos = api.fetch(video_id, languages=IDIOMAS)
    return " ".join(t.text.replace("\n", " ") for t in trechos)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # console do Windows quebra com emoji
    ap =argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fonte", choices=["canal", "busca", "links"])
    ap.add_argument("valor", nargs="+")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--ordem", choices=["populares", "recentes"], default="populares")
    ap.add_argument("--pool", type=int, default=200)
    ap.add_argument("--min-min", type=float, default=0, dest="min_min")
    ap.add_argument("--pausa", type=float, default=2.0, help="segundos entre vídeos (evita bloqueio)")
    args = ap.parse_args()

    videos = []
    if args.fonte == "links":
        for link in args.valor:
            videos += listar("links", link, 1)
    else:
        videos = listar(args.fonte, " ".join(args.valor), args.pool)
        if args.fonte == "canal" and args.ordem == "populares":
            videos.sort(key=lambda v: v["views"], reverse=True)
        if args.min_min:
            videos = [v for v in videos if v["duracao"] >= args.min_min * 60]
        videos = videos[: args.top]

    print(f"{len(videos)} vídeos na fila")
    ok = falha = pulado = 0
    for i, v in enumerate(videos, 1):
        pasta = SAIDA / nome_seguro(v["canal"])
        pasta.mkdir(parents=True, exist_ok=True)
        arquivo = pasta / f"{v['id']}.txt"
        if arquivo.exists():
            pulado += 1
            continue
        try:
            texto = baixar_transcricao(v["id"])
        except Exception as erro:  # sem legenda, bloqueio de IP, vídeo privado...
            falha += 1
            print(f"[{i}/{len(videos)}] FALHA {v['id']} {v['titulo'][:50]}: {type(erro).__name__}")
            continue
        cabecalho = (f"Título: {v['titulo']}\nCanal: {v['canal']}\nViews: {v['views']}\n"
                     f"Duração: {v['duracao']//60} min\nLink: https://youtu.be/{v['id']}\n\n")
        arquivo.write_text(cabecalho + texto, encoding="utf-8")
        ok += 1
        print(f"[{i}/{len(videos)}] ok {v['titulo'][:60]} ({v['views']} views)")
        time.sleep(args.pausa)
    print(f"Feito: {ok} baixados, {pulado} já existiam, {falha} falharam. Pasta: {SAIDA}")


if __name__ == "__main__":
    sys.exit(main())
