class Observer:
    def update(self, observable, *args, **kwargs):
        pass

class Observable:
    def __init__(self):
        self._observers = []

    def agregar_observer(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def quitar_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notificar_observers(self, *args, **kwargs):
        for observer in self._observers:
            observer.update(self, *args, **kwargs)

class VidaLogger(Observer):
    def update(self, observable, *args, **kwargs):
        print(f"[Observer] Nueva vida del personaje: {args[0]}")

class GestorPresentadoresObserver(Observer):
    def __init__(self, gestor_presentadores):
        self.gestor_presentadores = gestor_presentadores

    def update(self, observable, *args, **kwargs):
        vida = args[0]
        if vida <= 0:
            # Cambia primero al menú para evitar que siga el juego
            self.gestor_presentadores.cambiar_a_menu()
            self.gestor_presentadores.mostrar_game_over()
