"""Hook PostToolUse: quando o Claude edita um .py de core/, roda a suíte de testes.

Recebe no stdin o JSON do evento (tool_input.file_path). Se não for .py de
core/, sai sem fazer nada. Se os testes falharem, escreve o fim da saída no
stderr e sai com código 2 — o Claude Code devolve isso ao Claude, que vê a
falha na hora e corrige. Com testes passando, fica em silêncio.
"""
import json
import os
import subprocess
import sys

try:
    evento = json.load(sys.stdin)
except Exception:
    sys.exit(0)

caminho = (evento.get("tool_input") or {}).get("file_path") or (evento.get("tool_response") or {}).get("filePath") or ""
caminho = caminho.replace("\\", "/")
if not caminho.endswith(".py") or "/core/" not in caminho:
    sys.exit(0)

raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
resultado = subprocess.run(
    [sys.executable, "-m", "unittest", "discover", "-p", "test_*.py"],
    cwd=os.path.join(raiz, "core"),
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)
if resultado.returncode != 0:
    saida = (resultado.stdout + resultado.stderr).strip().splitlines()
    sys.stderr.write("Testes do core falharam depois da edição em " + os.path.basename(caminho) + ":\n")
    sys.stderr.write("\n".join(saida[-40:]) + "\n")
    sys.exit(2)
sys.exit(0)
