from datetime import datetime


def formatar_moeda(valor: float) -> str:
    """Formata um float como moeda brasileira.

    Exemplo:
        formatar_moeda(1234.5)  ->  'R$ 1.234,50'
        formatar_moeda(5)       ->  'R$ 5,00'
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_data(data: datetime) -> str:
    """Formata um datetime como 'dd/mm/aaaa hh:mm'.

    Exemplo:
        formatar_data(datetime(2026, 10, 11, 6, 54))
        ->  '11/10/2026 06:54'
    """
    return data.strftime("%d/%m/%Y %H:%M")