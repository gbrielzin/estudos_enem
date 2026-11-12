"""
seguranca.py — proteção básica contra abuso e robô na API (ver
docs/seguranca_api.md).

Três peças, todas sem dependência fora da biblioteca padrão:

- **Limite de requisições** (rate limit) por janela deslizante de 60 s,
  com número diferente por tipo de rota (leitura, escrita, admin,
  arquivos). A chave é a pessoa quando o código de acesso é válido e o IP
  quando não é: assim duas pessoas na mesma wifi da escola não dividem a
  cota, e quem não tem código fica preso no IP.
- **Trava de força bruta**: 401 conta como tentativa errada de chave. Com
  `FALHAS_AUTH_MAX` erros do mesmo IP em `FALHAS_AUTH_JANELA`, aquele IP
  recebe 429 em toda rota com trava, MESMO acertando a chave depois --
  senão o 200 vira o sinal de "achei" para o robô.
- **Log de segurança**: 429, chave errada e admin negado viram uma linha
  JSON no stdout (os logs da Railway guardam) e ficam nos últimos
  `TAMANHO_LOG` eventos em memória, que o painel /admin/ mostra. Nunca
  grava o header Authorization, query string nem corpo.

Tudo em memória do processo: com uma réplica só (hoje) funciona; com
várias, cada uma teria a própria conta e o limite real viraria
limite x réplicas -- aí o contador precisa ir para um Redis.
"""
from __future__ import annotations

import ipaddress
import json
import logging
import math
import os
import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Callable

# Requisições por minuto, por pessoa (ou por IP sem código válido).
JANELA_SEGUNDOS = 60
LIMITES_POR_MINUTO = {
    "leitura": 240,   # GET da API: a trilha abre várias telas por minuto
    "escrita": 60,    # POST: responder 1 questão por segundo já é robô
    "admin": 20,      # painel: uma pessoa olhando, não precisa de mais
    "arquivos": 600,  # app web + figuras: uma tela carrega dezenas de arquivos
}
# Força bruta na chave: 10 erros do mesmo IP em 15 min bloqueiam o IP
# pelo resto da janela.
FALHAS_AUTH_MAX = 10
FALHAS_AUTH_JANELA = 15 * 60
# Teto de chaves guardadas (IPs/pessoas) para um ataque com muitos IPs
# não encher a memória: passando disso, as chaves mais antigas saem.
MAX_CHAVES = 20_000
TAMANHO_LOG = 500
TAMANHO_USER_AGENT = 200

_logger = logging.getLogger("enem.seguranca")
if not _logger.handlers:
    _saida = logging.StreamHandler()
    _saida.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_saida)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False


class LimitadorJanela:
    """Janela deslizante: guarda o horário de cada requisição aceita por
    chave e recusa quando já há `limite` dentro dos últimos `janela`
    segundos. Exato (sem o "estouro na virada do minuto" da janela fixa)
    e a memória por chave é no máximo `limite` números."""

    def __init__(self, relogio: Callable[[], float] = time.monotonic):
        self._relogio = relogio
        self._registros: dict[str, deque] = {}
        self._trava = threading.Lock()

    def _fila(self, chave: str, janela: float, agora: float) -> deque:
        fila = self._registros.get(chave)
        if fila is None:
            if len(self._registros) >= MAX_CHAVES:
                self._liberar_espaco(agora, janela)
            fila = self._registros[chave] = deque()
        while fila and fila[0] <= agora - janela:
            fila.popleft()
        return fila

    def _liberar_espaco(self, agora: float, janela: float) -> None:
        vazias = [c for c, f in self._registros.items() if not f or f[-1] <= agora - janela]
        for chave in vazias:
            del self._registros[chave]
        # Ainda cheio: tira as mais antigas (dict guarda ordem de inserção).
        while len(self._registros) >= MAX_CHAVES:
            del self._registros[next(iter(self._registros))]

    def tentar(self, chave: str, limite: int, janela: float) -> int | None:
        """Conta a requisição se couber. Devolve None (passou) ou quantos
        segundos faltam para abrir vaga (vai no Retry-After)."""
        with self._trava:
            agora = self._relogio()
            fila = self._fila(chave, janela, agora)
            if len(fila) >= limite:
                return max(1, math.ceil(fila[0] + janela - agora))
            fila.append(agora)
            return None

    def bloqueado(self, chave: str, limite: int, janela: float) -> int | None:
        """Como tentar(), mas só olha: usado na trava de força bruta, que
        conta erro (registrar) e não acesso."""
        with self._trava:
            agora = self._relogio()
            fila = self._fila(chave, janela, agora)
            if len(fila) >= limite:
                return max(1, math.ceil(fila[0] + janela - agora))
            return None

    def registrar(self, chave: str, janela: float) -> int:
        """Conta um evento e devolve quantos há na janela."""
        with self._trava:
            agora = self._relogio()
            fila = self._fila(chave, janela, agora)
            fila.append(agora)
            return len(fila)

    def limpar(self) -> None:
        with self._trava:
            self._registros.clear()


limitador = LimitadorJanela()
falhas_auth = LimitadorJanela()
_eventos: deque = deque(maxlen=TAMANHO_LOG)
_ultimo_aviso_429: dict[str, float] = {}


def limpar_estado() -> None:
    """Zera contadores e log (usado pelos testes)."""
    limitador.limpar()
    falhas_auth.limpar()
    _eventos.clear()
    _ultimo_aviso_429.clear()


def rate_limit_ligado() -> bool:
    """Ligado por padrão. `API_RATE_LIMIT_DESLIGADO=1` só para a suíte de
    testes antiga e desenvolvimento local."""
    return os.environ.get("API_RATE_LIMIT_DESLIGADO") != "1"


def confiar_no_proxy() -> bool:
    """Se o X-Real-IP pode ser usado como IP do cliente.

    Só faz sentido atrás de um proxy que SOBRESCREVE esse header (a borda
    da Railway documenta que põe o IP do cliente nele). Fora desse caso,
    qualquer um mandaria `X-Real-IP: 1.2.3.4` e trocaria de IP a cada
    requisição, furando o limite. Por isso: `API_CONFIAR_PROXY=1/0`
    decide; sem a variável, liga só quando a Railway está presente (ela
    injeta RAILWAY_ENVIRONMENT_ID / RAILWAY_PROJECT_ID em todo deploy)."""
    valor = os.environ.get("API_CONFIAR_PROXY")
    if valor is not None:
        return valor == "1"
    return any(os.environ.get(v) for v in ("RAILWAY_ENVIRONMENT_ID", "RAILWAY_PROJECT_ID"))


def _ip_valido(texto: str | None) -> str | None:
    try:
        return str(ipaddress.ip_address((texto or "").strip()))
    except ValueError:
        return None


def ip_do_cliente(ip_conexao: str | None, x_real_ip: str | None, confiar: bool) -> str:
    """IP usado no limite e no log.

    - Sem proxy confiável: o IP de quem abriu a conexão TCP, ponto. Header
      nenhum é lido (X-Forwarded-For e X-Real-IP são texto que o cliente
      escreve).
    - Atrás da Railway: o X-Real-IP, que a borda preenche. Não uso o
      X-Forwarded-For: a Railway não documenta se ele é sobrescrito ou se
      ela só acrescenta no fim, e a 1ª posição dele é escolha do cliente.
      Header ausente ou que não é IP cai no IP da conexão."""
    if confiar:
        ip = _ip_valido(x_real_ip)
        if ip:
            return ip
    return ip_do_conexao(ip_conexao)


def ip_do_conexao(ip_conexao: str | None) -> str:
    return _ip_valido(ip_conexao) or (ip_conexao or "desconhecido")


def registrar_evento(tipo: str, ip: str, metodo: str, rota: str, user_agent: str | None, detalhe: str | None = None) -> dict:
    """Uma linha do log de segurança. `rota` é só o caminho (sem query
    string) e nada do header Authorization entra aqui."""
    evento = {
        "horario": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tipo": tipo,
        "ip": ip,
        "metodo": metodo,
        "rota": rota[:200],
        "user_agent": (user_agent or "")[:TAMANHO_USER_AGENT] or None,
        "detalhe": detalhe,
    }
    _eventos.append(evento)
    _logger.info(json.dumps({"seguranca": evento}, ensure_ascii=False))
    return evento


def eventos_recentes() -> list[dict]:
    """Mais novo primeiro."""
    return list(reversed(_eventos))


def _header(scope, nome: bytes, ultimo: bool = False) -> str | None:
    """Valor do header. `ultimo=True` pega a última ocorrência: se o
    cliente mandar o próprio X-Real-IP e o proxy acrescentar outro em vez
    de trocar, o do proxy é o que vem depois."""
    valores = [v.decode("latin-1") for k, v in scope.get("headers", []) if k == nome]
    if not valores:
        return None
    return valores[-1] if ultimo else valores[0]


# Headers que toda resposta leva. CSP mínima de propósito: o app web
# (export do Expo) e o painel usam script/estilo inline, e uma CSP que
# restringe script quebraria a tela; estas três diretivas não mexem em
# script e fecham clickjacking, <base> injetado e plugin.
HEADERS_SEGURANCA = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"content-security-policy", b"frame-ancestors 'none'; base-uri 'self'; object-src 'none'"),
]


class MiddlewareSeguranca:
    """ASGI puro (não BaseHTTPMiddleware) para não mexer no contexto da
    requisição que a trava de autenticação usa para escolher o banco.

    `classificar(metodo, caminho)` devolve o tipo de rota (chave de
    LIMITES_POR_MINUTO) ou None para rota sem limite (/health).
    `identificar(authorization)` devolve um identificador da pessoa se o
    código for válido, ou None."""

    def __init__(self, app, classificar: Callable[[str, str], str | None], identificar: Callable[[str | None], str | None]):
        self.app = app
        self.classificar = classificar
        self.identificar = identificar

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        metodo = scope.get("method", "GET")
        caminho = scope.get("path", "")
        cliente = scope.get("client")
        ip = ip_do_cliente(cliente[0] if cliente else None, _header(scope, b"x-real-ip", ultimo=True), confiar_no_proxy())
        user_agent = _header(scope, b"user-agent")
        tipo_rota = self.classificar(metodo, caminho)
        com_trava = tipo_rota in ("leitura", "escrita", "admin")

        async def enviar_com_headers(mensagem):
            if mensagem["type"] == "http.response.start":
                mensagem["headers"] = list(mensagem.get("headers", [])) + HEADERS_SEGURANCA
            await send(mensagem)

        if tipo_rota is None or not rate_limit_ligado():
            await self.app(scope, receive, enviar_com_headers)
            return

        # 1) IP em bloqueio por força bruta: recusa antes de olhar a chave.
        if com_trava:
            espera = falhas_auth.bloqueado(f"ip:{ip}", FALHAS_AUTH_MAX, FALHAS_AUTH_JANELA)
            if espera:
                self._avisar_429(f"forca:{ip}", ip, metodo, caminho, user_agent, "ip bloqueado por chave errada repetida")
                await self._responder_429(enviar_com_headers, espera, "Muitas tentativas com chave errada. Tente mais tarde.")
                return

        # 2) Limite por pessoa (código válido) ou por IP.
        pessoa = None
        if com_trava and tipo_rota != "admin":
            try:
                pessoa = self.identificar(_header(scope, b"authorization"))
            except Exception:  # config mal formada: a trava da rota responde
                pessoa = None
        chave = f"{tipo_rota}:" + (f"pessoa:{pessoa}" if pessoa else f"ip:{ip}")
        espera = limitador.tentar(chave, LIMITES_POR_MINUTO[tipo_rota], JANELA_SEGUNDOS)
        if espera:
            self._avisar_429(chave, ip, metodo, caminho, user_agent, f"limite {tipo_rota}")
            await self._responder_429(enviar_com_headers, espera, "Muitas requisições. Tente de novo em instantes.")
            return

        # 3) Segue e olha a resposta: 401 conta como tentativa de chave errada.
        status = {}

        async def observar(mensagem):
            if mensagem["type"] == "http.response.start":
                status["codigo"] = mensagem["status"]
            await enviar_com_headers(mensagem)

        await self.app(scope, receive, observar)

        if com_trava and status.get("codigo") == 401:
            total = falhas_auth.registrar(f"ip:{ip}", FALHAS_AUTH_JANELA)
            tipo = "admin_negado" if tipo_rota == "admin" else "chave_errada"
            detalhe = f"{total} erro(s) em {FALHAS_AUTH_JANELA // 60} min"
            if total == FALHAS_AUTH_MAX:
                detalhe += " -> ip bloqueado"
            registrar_evento(tipo, ip, metodo, caminho, user_agent, detalhe)

    def _avisar_429(self, chave, ip, metodo, caminho, user_agent, detalhe):
        # Um robô martelando geraria milhares de linhas iguais: registra o
        # 1º 429 de cada chave por janela e ignora o resto.
        agora = time.monotonic()
        if agora - _ultimo_aviso_429.get(chave, -math.inf) < JANELA_SEGUNDOS:
            return
        if len(_ultimo_aviso_429) >= MAX_CHAVES:
            _ultimo_aviso_429.clear()
        _ultimo_aviso_429[chave] = agora
        registrar_evento("limite_excedido", ip, metodo, caminho, user_agent, detalhe)

    @staticmethod
    async def _responder_429(send, espera: int, mensagem: str):
        corpo = json.dumps({"detail": mensagem}, ensure_ascii=False).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 429,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(corpo)).encode()),
                (b"retry-after", str(espera).encode()),
            ],
        })
        await send({"type": "http.response.body", "body": corpo})
