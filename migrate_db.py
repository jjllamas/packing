import sqlite3

DDL = """
CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS item_tags (
  item_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  PRIMARY KEY(item_id, tag_id),
  FOREIGN KEY(item_id) REFERENCES items(id),
  FOREIGN KEY(tag_id) REFERENCES tags(id)
);
"""
conn = sqlite3.connect('packing.db')
conn.executescript(DDL)
conn.commit()
conn.close()
print("Migración completada.")
