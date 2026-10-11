def ler_valor_positivo(prompt: str) -> float:
    """Lê um valor numérico positivo do usuário, aceitando vírgula ou ponto.

    Fica em loop até o usuário digitar algo válido.
    """
    while True:
        try:
            entrada = input(prompt).replace(",", ".").strip()
            valor = float(entrada)
            if valor <= 0:
                print("❌ O valor deve ser maior que zero.")
                continue
            return valor
        except ValueError:
            print("❌ Digite um número válido.")


def ler_texto_obrigatorio(prompt: str) -> str:
    """Lê uma string não vazia do usuário.

    Fica em loop até o usuário digitar algo.
    """
    while True:
        texto = input(prompt).strip()
        if texto:
            return texto
        print("❌ Este campo não pode ficar vazio.")