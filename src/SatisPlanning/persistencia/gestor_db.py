import sqlite3
import os

class GestorDB:
    def __init__(self, ruta_db=None):
        base_path = os.path.dirname(__file__)
        datos_dir = os.path.join(base_path, "..", "datos")
        os.makedirs(datos_dir, exist_ok=True)  # Asegura que la carpeta exista
        if ruta_db is None:
            ruta_db = os.path.join(datos_dir, "base_juego.db")
        self.con = sqlite3.connect(ruta_db)
        self.cursor = self.con.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            experiencia INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1
        )
        """) #cambiar en un futuro
        self.con.commit()

    def agregar_jugador(self, nombre, experiencia=0, nivel=1):
        self.cursor.execute("""
        INSERT INTO jugadores (nombre, experiencia, nivel)
        VALUES (?, ?, ?)
        """, (nombre, experiencia, nivel))
        self.con.commit() #cambiar en un futuro

    def obtener_jugadores(self):
        self.cursor.execute("SELECT * FROM jugadores")
        return self.cursor.fetchall() #cambiar en un futuro

    def cerrar(self):
        self.con.close() #cambiar en un futuro
