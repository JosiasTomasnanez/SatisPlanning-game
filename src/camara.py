import constantes as ct
class Camera:
    def __init__(self):
        self.screen_width = ct.ANCHO
        self.screen_height = ct.ALTO
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_x, target_y):
        """
        Update the camera's offset to center on the target position.
        """
        self.offset_x = target_x - (self.screen_width // 2)
        self.offset_y = target_y - (self.screen_height // 2)

    def apply(self, x, y):
        """
        Apply the camera's offset to a given position.
        """
        return x - self.offset_x, y - self.offset_y
