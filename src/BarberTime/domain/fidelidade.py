class Fidelidade:
    """Agregado responsável pelas regras de fidelidade do cliente."""

    def __init__(
        self,
        id: int,
        cliente_id: int,
        cortes_concluidos: int = 0,
        possui_no_show: bool = False,
        cortes_para_gratis: int = 10,
    ):
        if id is None or cliente_id is None:
            raise ValueError("ID da fidelidade e ID do cliente são obrigatórios")

        if isinstance(cortes_concluidos, bool) or not isinstance(cortes_concluidos, int):
            raise ValueError("A quantidade de cortes deve ser um inteiro")

        if cortes_concluidos < 0:
            raise ValueError("A quantidade de cortes não pode ser negativa")

        if (
            isinstance(cortes_para_gratis, bool)
            or not isinstance(cortes_para_gratis, int)
            or cortes_para_gratis <= 0
        ):
            raise ValueError("A meta de cortes deve ser um inteiro positivo")

        self.id = id
        self.cliente_id = cliente_id
        self.cortes_concluidos = cortes_concluidos
        self.possui_no_show = bool(possui_no_show)
        self.cortes_para_gratis = cortes_para_gratis

    @property
    def cortes_restantes(self) -> int:
        """Quantidade de cortes que faltam para obter o benefício."""
        return max(0, self.cortes_para_gratis - self.cortes_concluidos)

    @property
    def corte_gratis_disponivel(self) -> bool:
        """Indica se o cliente acumulou cortes suficientes."""
        return self.cortes_concluidos >= self.cortes_para_gratis

    def registrar_corte_concluido(self):
        """Adiciona um corte realizado ao progresso de fidelidade."""
        self.cortes_concluidos += 1
        return self

    def registrar_no_show(self):
        """Registra uma falta no histórico do cliente."""
        self.possui_no_show = True
        return self

    def pode_resgatar_corte_gratis(self) -> bool:
        """Verifica todas as condições para resgatar o benefício."""
        return (
            self.corte_gratis_disponivel
            and not self.possui_no_show
        )

    def resgatar_corte_gratis(self):
        """Resgata o benefício ou rejeita a operação."""
        if self.possui_no_show:
            raise ValueError(
                "Resgate negado: cliente possui no-show no histórico"
            )

        if not self.corte_gratis_disponivel:
            raise ValueError(
                "Resgate negado: cliente ainda não acumulou cortes suficientes"
            )

        self.cortes_concluidos -= self.cortes_para_gratis
        return self

    def __eq__(self, other):
        if not isinstance(other, Fidelidade):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
