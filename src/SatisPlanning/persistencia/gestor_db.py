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
        self.cursor.executescript("""
         CREATE TABLE IF NOT EXISTS inventario (
           id_inventario INTEGER PRIMARY KEY
           );

         CREATE TABLE IF NOT EXISTS jugador (
            id_jugador INTEGER PRIMARY KEY,
            id_inventario INTEGER,
            vida REAL,
            mana REAL,
            efecto TEXT,
            FOREIGN KEY (id_inventario) REFERENCES inventario(id_inventario)
        );

        CREATE TABLE IF NOT EXISTS objeto_inventario (
            id_objeto_inventario INTEGER PRIMARY KEY,
            id_inventario INTEGER,
            durabilidad REAL,
            bufo TEXT,
            FOREIGN KEY (id_inventario) REFERENCES inventario(id_inventario)
        );

        CREATE TABLE IF NOT EXISTS equipable (
            id_equipable INTEGER PRIMARY KEY,
            id_jugador INTEGER,
            id_objeto_inventario INTEGER,
            FOREIGN KEY (id_jugador) REFERENCES jugador(id_jugador),
            FOREIGN KEY (id_objeto_inventario) REFERENCES objeto_inventario(id_objeto_inventario)
        );

        CREATE TABLE IF NOT EXISTS mundo (
            semilla TEXT PRIMARY KEY,
            fecha TEXT,
            tamano TEXT
        );

        CREATE TABLE IF NOT EXISTS objeto_mundo (
            id_objeto_mundo INTEGER PRIMARY KEY,
            semilla TEXT,
            durabilidad REAL,
            bufo TEXT,
            x REAL,
            y REAL,
            FOREIGN KEY (semilla) REFERENCES mundo(semilla)
        );

        CREATE TABLE IF NOT EXISTS bloque (
            id_bloque INTEGER PRIMARY KEY,
            semilla TEXT,
            durabilidad REAL,
            bufo TEXT,
            i INTEGER,
            j INTEGER,
            FOREIGN KEY (semilla) REFERENCES mundo(semilla)
        );
        """)
        self.con.commit()

    def insertar_inventario(self, id_inventario):
        self.cursor.execute("INSERT INTO inventario (id_inventario) VALUES (?)", (id_inventario,))
        self.con.commit()

    def insertar_jugador(self, id_jugador, id_inventario, vida, mana, efecto):
        self.cursor.execute("""
        INSERT INTO jugador (id_jugador, id_inventario, vida, mana, efecto)
        VALUES (?, ?, ?, ?, ?)
    """, (id_jugador, id_inventario, vida, mana, efecto))
        self.con.commit()

    def insertar_objeto_inventario(self, id_objeto, id_inventario, durabilidad, bufo):
        self.cursor.execute("""
        INSERT INTO objeto_inventario (id_objeto_inventario, id_inventario, durabilidad, bufo)
        VALUES (?, ?, ?, ?)
    """, (id_objeto, id_inventario, durabilidad, bufo))
        self.con.commit()
    
    def insertar_equipable(self, id_equipable, id_jugador, id_objeto_inventario):
        self.cursor.execute("""
        INSERT INTO equipable (id_equipable, id_jugador, id_objeto_inventario)
        VALUES (?, ?, ?)
    """, (id_equipable, id_jugador, id_objeto_inventario))
        self.con.commit()

    def insertar_mundo(self, semilla, fecha, tamano):
        self.cursor.execute("""
        INSERT INTO mundo (semilla, fecha, tamano)
        VALUES (?, ?, ?)
    """, (semilla, fecha, tamano))
        self.con.commit()

    def insertar_objeto_mundo(self, id_objeto, semilla, durabilidad, bufo, x, y):
        self.cursor.execute("""
        INSERT INTO objeto_mundo (id_objeto_mundo, semilla, durabilidad, bufo, x, y)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_objeto, semilla, durabilidad, bufo, x, y))
        self.con.commit()

    def insertar_bloque(self, id_bloque, semilla, durabilidad, bufo, i, j):
        self.cursor.execute("""
        INSERT INTO bloque (id_bloque, semilla, durabilidad, bufo, i, j)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_bloque, semilla, durabilidad, bufo, i, j))
        self.con.commit()

    def cerrar(self):
        self.con.close() #cambiar en un futuro
