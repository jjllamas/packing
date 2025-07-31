#!/usr/bin/env python3
# init_db.py
import sqlite3
import os

DB_FILENAME = "packing.db"

def init_db(db_path=DB_FILENAME):
    # Si existe, lo eliminamos para inicializar desde cero:
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Eliminado antiguo {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Activar soporte de foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Crear tablas
    cursor.executescript("""
    CREATE TABLE trips (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE persons (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id  INTEGER NOT NULL,
        name     TEXT    NOT NULL,
        FOREIGN KEY(trip_id) REFERENCES trips(id) ON DELETE CASCADE
    );

    CREATE TABLE categories (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE tags (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE items (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT    NOT NULL UNIQUE,
        category_id  INTEGER NOT NULL,
        FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
    );

    CREATE TABLE item_tags (
        item_id  INTEGER NOT NULL,
        tag_id   INTEGER NOT NULL,
        PRIMARY KEY(item_id, tag_id),
        FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE CASCADE,
        FOREIGN KEY(tag_id)  REFERENCES tags(id)  ON DELETE CASCADE
    );

    CREATE TABLE trip_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id    INTEGER NOT NULL,
        person_id  INTEGER NOT NULL,
        item_id    INTEGER NOT NULL,
        quantity   INTEGER NOT NULL DEFAULT 1,
        packed     INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(trip_id)   REFERENCES trips(id) ON DELETE CASCADE,
        FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE CASCADE,
        FOREIGN KEY(item_id)   REFERENCES items(id) ON DELETE RESTRICT
    );
    """)

    conn.commit()
    conn.close()
    print(f"Base de datos inicializada en {db_path}")

if __name__ == "__main__":
    init_db()
