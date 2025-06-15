from abc import ABC, abstractmethod

class Componente(ABC):
    """
    Clase base para todos los componentes.
    """
    def __init__(self, propietario):
        """
        Inicializa el componente con una referencia al objeto propietario.

        :param propietario: Objeto al que pertenece este componente.
        """
        self.propietario = propietario

    @abstractmethod
    def actualizar(self, dt):
        """
        Método que debe ser implementado por las subclases para actualizar la lógica del componente.

        :param dt: Delta time (tiempo transcurrido desde el último frame).
        """
        raise NotImplementedError("El método 'actualizar' debe ser implementado por las subclases.")
