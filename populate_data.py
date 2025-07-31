#!/usr/bin/env python3
# populate_data.py

from models import (
    create_category, create_tag,
    create_item, assign_tag_to_item
)

def main():
    # 1. Categorías
    ropa_id       = create_category("Ropa")
    electronica_id= create_category("Electrónica")
    higiene_id    = create_category("Higiene")
    print(f"Categorías creadas: Ropa={ropa_id}, Electrónica={electronica_id}, Higiene={higiene_id}")

    # 2. Tags
    verano_id     = create_tag("Verano")
    invierno_id   = create_tag("Invierno")
    importante_id = create_tag("Importante")
    fragil_id     = create_tag("Frágil")
    print(f"Tags creados: Verano={verano_id}, Invierno={invierno_id}, Importante={importante_id}, Frágil={fragil_id}")

    # 3. Ítems y asignación de tags
    camisa_id   = create_item("Camisa", ropa_id)
    pantalones_id = create_item("Pantalones", ropa_id)
    cepillo_id  = create_item("Cepillo de dientes", higiene_id)
    movil_id    = create_item("Móvil", electronica_id)
    cargador_id = create_item("Cargador", electronica_id)

    # Etiquetado
    assign_tag_to_item(camisa_id, verano_id)
    assign_tag_to_item(pantalones_id, verano_id)
    assign_tag_to_item(cepillo_id, importante_id)
    assign_tag_to_item(movil_id, fragil_id)
    assign_tag_to_item(cargador_id, importante_id)

    print("Ítems y tags enlazados.")

if __name__ == "__main__":
    main()
