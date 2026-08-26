"""
backup_db.py — copia enem.db pra backups/enem_<timestamp>.db.

Existe porque reconstruir_base.py apaga enem.db antes de reconstruir, e
ele NÃO consegue reproduzir sozinho: resoluções em vídeo ligadas depois
do último snapshot de questoes_enem.csv, tentativas de anos fora do
backfill hardcoded de 2019, e classificações de matéria conseguidas via
título de vídeo (coletar_videos.py) em vez do CSV de gabarito. Rodar
este script ANTES de qualquer reconstrução é a rede de segurança real
-- ver o aviso no topo de reconstruir_base.py.

Uso: python backup_db.py
Também é chamado direto da tela Admin do cartão-resposta (botão
"Fazer backup agora").
"""
from datetime import datetime
from pathlib import Path
import shutil

import db

PASTA_BACKUPS = Path(__file__).parent / "backups"


def fazer_backup() -> Path:
    """Copia o enem.db atual pra backups/enem_<AAAAMMDD_HHMMSS>.db e
    devolve o caminho do arquivo criado. Não apaga backups antigos --
    quem decide o que limpar é a pessoa, olhando listar_backups()."""
    if not db.DB_PATH.exists():
        raise FileNotFoundError(f"{db.DB_PATH} não existe ainda -- nada pra fazer backup.")

    PASTA_BACKUPS.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = PASTA_BACKUPS / f"enem_{timestamp}.db"
    shutil.copy2(db.DB_PATH, destino)
    return destino


def listar_backups() -> list[Path]:
    """Backups existentes, do mais recente pro mais antigo."""
    if not PASTA_BACKUPS.exists():
        return []
    return sorted(PASTA_BACKUPS.glob("enem_*.db"), reverse=True)


if __name__ == "__main__":
    caminho = fazer_backup()
    tamanho_mb = caminho.stat().st_size / 1_000_000
    print(f"Backup criado: {caminho} ({tamanho_mb:.2f} MB)")
    print(f"Total de backups em {PASTA_BACKUPS}: {len(listar_backups())}")
