from SatisPlanning.componente import Componente

class ComponenteAgregarObjeto(Componente):
    """
    Componente para agregar objetos al mundo.
    """
    def __init__(self, propietario):
        super().__init__(propietario)

    def agregar_objeto(self, objeto, mundo,tangible):
        """
        Agrega un objeto al mundo.
        :param objeto: El objeto a agregar.
        :param mundo: El mundo donde agregar el objeto.
        """
        while mundo.colisiona(objeto.hitbox, self.propietario):
            objeto.actualizar_posicion( objeto.x,objeto.y-1)

        mundo.agregar_objeto(objeto,tangible)
