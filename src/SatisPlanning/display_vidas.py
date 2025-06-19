from SatisPlanning.patron_observer import Observer

class DisplayVidas(Observer):
    def __init__(self, vida_inicial=100, valor_corazon=20):
        self.valor_corazon = valor_corazon
        self.vida = vida_inicial
        self.corazones = self.calcular_corazones(vida_inicial)

    def calcular_corazones(self, vida):
        return max(1, (vida + self.valor_corazon - 1) // self.valor_corazon)

    def update(self, observable, *args, **kwargs):
        self.vida = args[0]
        self.corazones = self.calcular_corazones(self.vida)
