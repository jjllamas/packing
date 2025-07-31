import sqlite3
from typing import List, Tuple, Optional

DB_FILENAME = "packing.db"


def get_connection() -> sqlite3.Connection:
    """
    Devuelve una conexión a la base de datos con foreign_keys activadas.
    """
    conn = sqlite3.connect(DB_FILENAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ----- CRUD para Trips -----

def create_trip(name: str) -> int:
    """
    Crea un viaje y devuelve su ID.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trips (name) VALUES (?);",
        (name,)
    )
    conn.commit()
    trip_id = cursor.lastrowid
    conn.close()
    return trip_id


def get_trip(trip_id: int) -> Optional[Tuple[int, str]]:
    """
    Obtiene un viaje por su ID. Devuelve (id, name) o None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM trips WHERE id = ?;",
        (trip_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_trip(trip_id: int, new_name: str) -> None:
    """
    Actualiza el nombre de un viaje.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE trips SET name = ? WHERE id = ?;",
        (new_name, trip_id)
    )
    conn.commit()
    conn.close()


def delete_trip(trip_id: int) -> None:
    """
    Elimina un viaje y en cascada sus personas y trip_items.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM trips WHERE id = ?;",
        (trip_id,)
    )
    conn.commit()
    conn.close()

# ----- CRUD para Persons -----

def create_person(trip_id: int, name: str) -> int:
    """Crea una persona en un viaje y devuelve su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO persons (trip_id, name) VALUES (?, ?);",
        (trip_id, name)
    )
    conn.commit()
    person_id = cursor.lastrowid
    conn.close()
    return person_id


def get_person(person_id: int) -> Optional[Tuple[int, int, str]]:
    """
    Obtiene una persona por su ID. Devuelve (id, trip_id, name) o None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, trip_id, name FROM persons WHERE id = ?;",
        (person_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def update_person(person_id: int, new_name: str) -> None:
    """Actualiza el nombre de una persona."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE persons SET name = ? WHERE id = ?;",
        (new_name, person_id)
    )
    conn.commit()
    conn.close()


def delete_person(person_id: int) -> None:
    """Elimina una persona y en cascada sus asignaciones en trip_items."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM persons WHERE id = ?;",
        (person_id,)
    )
    conn.commit()
    conn.close()

# ----- CRUD para Categories -----

def create_category(name: str) -> int:
    """Crea una categoría y devuelve su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?);", (name,))
    conn.commit()
    cat_id = cursor.lastrowid
    conn.close()
    return cat_id


def list_categories() -> List[Tuple[int, str]]:
    """Devuelve todas las categorías."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories;")
    cats = cursor.fetchall()
    conn.close()
    return cats


def update_category(cat_id: int, new_name: str) -> None:
    """Actualiza el nombre de una categoría."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE categories SET name = ? WHERE id = ?;",
        (new_name, cat_id)
    )
    conn.commit()
    conn.close()


def delete_category(cat_id: int) -> None:
    """Elimina una categoría (solo si no hay ítems asociados)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM categories WHERE id = ?;",
        (cat_id,)
    )
    conn.commit()
    conn.close()

# ----- CRUD para Tags -----

def create_tag(name: str) -> int:
    """Crea una etiqueta y devuelve su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tags (name) VALUES (?);", (name,))
    conn.commit()
    tag_id = cursor.lastrowid
    conn.close()
    return tag_id


def list_tags() -> List[Tuple[int, str]]:
    """Devuelve todas las etiquetas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM tags;")
    tags = cursor.fetchall()
    conn.close()
    return tags


def update_tag(tag_id: int, new_name: str) -> None:
    """Actualiza el nombre de una etiqueta."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tags SET name = ? WHERE id = ?;",
        (new_name, tag_id)
    )
    conn.commit()
    conn.close()


def delete_tag(tag_id: int) -> None:
    """Elimina una etiqueta (cascada en item_tags)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM tags WHERE id = ?;",
        (tag_id,)
    )
    conn.commit()
    conn.close()

# ----- CRUD para Items -----

def create_item(name: str, category_id: int) -> int:
    """Crea un ítem y devuelve su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (name, category_id) VALUES (?, ?);",
        (name, category_id)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id


def list_items() -> List[Tuple[int, str, int]]:
    """Devuelve todos los ítems con su categoría."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category_id FROM items;")
    items = cursor.fetchall()
    conn.close()
    return items


def update_item(item_id: int, new_name: str, new_cat_id: int) -> None:
    """Actualiza nombre y categoría de un ítem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE items SET name = ?, category_id = ? WHERE id = ?;",
        (new_name, new_cat_id, item_id)
    )
    conn.commit()
    conn.close()


def delete_item(item_id: int) -> None:
    """Elimina un ítem y en cascada sus relaciones con tags y trip_items."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM items WHERE id = ?;",
        (item_id,)
    )
    conn.commit()
    conn.close()

# ----- Relaciones Tag-Item -----

def assign_tag_to_item(item_id: int, tag_id: int) -> None:
    """Asigna una etiqueta a un ítem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO item_tags (item_id, tag_id) VALUES (?, ?);",
        (item_id, tag_id)
    )
    conn.commit()
    conn.close()


def remove_tag_from_item(item_id: int, tag_id: int) -> None:
    """Elimina la relación etiqueta-ítem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM item_tags WHERE item_id = ? AND tag_id = ?;",
        (item_id, tag_id)
    )
    conn.commit()
    conn.close()

# ----- Asignación de Items a Personas -----

def assign_item(trip_id: int, person_id: int, item_id: int, quantity: int = 1) -> int:
    """Asigna un ítem a una persona en un viaje y devuelve el ID de la asignación."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trip_items (trip_id, person_id, item_id, quantity, packed) VALUES (?, ?, ?, ?, 0);",
        (trip_id, person_id, item_id, quantity)
    )
    conn.commit()
    ti_id = cursor.lastrowid
    conn.close()
    return ti_id


def update_assignment(assignment_id: int, quantity: Optional[int] = None, packed: Optional[int] = None) -> None:
    """Actualiza cantidad o estado packed de una asignación."""
    conn = get_connection()
    cursor = conn.cursor()
    parts = []
    params = []
    if quantity is not None:
        parts.append("quantity = ?")
        params.append(quantity)
    if packed is not None:
        parts.append("packed = ?")
        params.append(packed)
    params.append(assignment_id)
    sql = f"UPDATE trip_items SET {', '.join(parts)} WHERE id = ?;"
    cursor.execute(sql, params)
    conn.commit()
    conn.close()


def remove_assignment(assignment_id: int) -> None:
    """Elimina una asignación de ítem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trip_items WHERE id = ?;", (assignment_id,))
    conn.commit()
    conn.close()

# ----- Filtrado de Ítems por Tags -----

def filter_items_by_tags(tag_ids: List[int]) -> List[Tuple[int, str, int]]:
    """
    Devuelve list of items que tienen todas las etiquetas en tag_ids.

    La consulta usa GROUP BY y HAVING para requerir que el conteo de tags asociados coincida con len(tag_ids).
    """
    conn = get_connection()
    cursor = conn.cursor()
    # SQL:
    # SELECT i.id, i.name, i.category_id
    # FROM items i
    # JOIN item_tags it ON i.id = it.item_id
    # WHERE it.tag_id IN (?,?,...)
    # GROUP BY i.id
    # HAVING COUNT(DISTINCT it.tag_id) = ?;
    placeholders = ",".join("?" for _ in tag_ids)
    sql = f"""
    SELECT i.id, i.name, i.category_id
    FROM items i
    JOIN item_tags it ON i.id = it.item_id
    WHERE it.tag_id IN ({placeholders})
    GROUP BY i.id
    HAVING COUNT(DISTINCT it.tag_id) = ?;
    """
    params = tag_ids + [len(tag_ids)]
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Ejemplos de uso
if __name__ == "__main__":
    # Crear datos de prueba
    trip_id = create_trip("Vacaciones Verano")
    alice_id = create_person(trip_id, "Alicia")
    bob_id = create_person(trip_id, "Bob")
    cat_id = create_category("Ropa")
    tag_summer = create_tag("Verano")
    shirt_id = create_item("Camiseta", cat_id)
    assign_tag_to_item(shirt_id, tag_summer)
    # Filtrar ítems por etiqueta
    items_summer = filter_items_by_tags([tag_summer])
    print("Ítems de verano:", items_summer)
    # Asignar a Alicia
    assign_item(trip_id, alice_id, shirt_id, quantity=2)
    # Listar asignaciones
    conn = get_connection()
    for row in conn.execute("SELECT * FROM trip_items;"):
        print(row)
    conn.close()
