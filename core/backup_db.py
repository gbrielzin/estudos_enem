"""
backup_db.py — copia enem.db pra backups/enem_<timestamp>.db.

reconstruir_base.py já chama fazer_backup() sozinho antes de atualizar
a base (ver o topo daquele arquivo), então isso cobre o caso automático.
Existe como módulo à parte pra também dar um jeito manual e rápido de
tirar uma cópia (botão "Fazer backup agora" na tela Admin) antes de
qualquer operação que você não tenha certeza total do resultado --
carregar um CSV colado errado, por exemplo.

IMPORTANTE: backups/ é local nesta máquina (e está no .gitignore) --
não protege contra HD/SSD morto. Baixe o arquivo de vez em quando pra
algum lugar fora daqui (Drive, e-mail, etc.) usando o botão de download
ao lado de cada backup na tela Admin.

Uso: python backup_db.py
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


def dias_desde_ultimo_backup() -> int | None:
    """Dias desde o backup mais recente, local nesta máquina. None se
    nunca houve nenhum. Alimenta o lembrete na tela Admin -- ter um
    backup local não é o mesmo que ele estar em outro lugar também."""
    backups = listar_backups()
    if not backups:
        return None
    idade_segundos = datetime.now().timestamp() - backups[0].stat().st_mtime
    return int(idade_segundos // 86400)


if __name__ == "__main__":
    caminho = fazer_backup()
    tamanho_mb = caminho.stat().st_size / 1_000_000
    print(f"Backup criado: {caminho} ({tamanho_mb:.2f} MB)")
    print(f"Total de backups em {PASTA_BACKUPS}: {len(listar_backups())}")
