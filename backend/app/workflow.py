"""Máquina de estados do chamado: a regra de quais transições valem fica num só lugar.

    aberto ──▶ em_andamento ──▶ resolvido ──▶ fechado
       │            │  ▲            │
       │            ▼  │            └──▶ em_andamento (reaberto)
       │        aguardando
       └──▶ cancelado
"""

TRANSICOES: dict[str, set[str]] = {
    "aberto": {"em_andamento", "cancelado"},
    "em_andamento": {"aguardando", "resolvido"},
    "aguardando": {"em_andamento"},
    "resolvido": {"fechado", "em_andamento"},
    "fechado": set(),
    "cancelado": set(),
}

STATUS = list(TRANSICOES)


def transicoes_possiveis(status_atual: str) -> list[str]:
    return sorted(TRANSICOES.get(status_atual, set()))


def pode_transitar(de: str, para: str) -> bool:
    return para in TRANSICOES.get(de, set())
