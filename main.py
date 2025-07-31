import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import (
    get_connection,
    create_trip, delete_trip, get_trip,
    create_person, update_person, delete_person,
    assign_item, remove_assignment,
    list_categories, create_category, update_category, delete_category,
    list_tags, create_tag, update_tag, delete_tag,
    list_items, create_item, assign_tag_to_item
)

class PackingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Packing List")
        self.geometry("800x600")
        self._create_main_ui()

    def _create_main_ui(self):
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        self.trips_lb = tk.Listbox(frame)
        self.trips_lb.grid(row=0, column=0, rowspan=8, sticky="nsew")
        self._load_trips()

        ttk.Button(frame, text="Crear", command=self._create_trip).grid(row=0, column=1)
        ttk.Button(frame, text="Abrir", command=self._open_trip).grid(row=1, column=1)
        ttk.Button(frame, text="Borrar", command=self._delete_trip).grid(row=2, column=1)
        ttk.Button(frame, text="Clonar", command=self._clone_trip).grid(row=3, column=1)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(row=4, column=1, sticky="ew", pady=5)
        ttk.Button(frame, text="Categorías", command=self._manage_categories).grid(row=5, column=1)
        ttk.Button(frame, text="Etiquetas", command=self._manage_tags).grid(row=6, column=1)
        ttk.Button(frame, text="Crear ítem", command=self._create_item).grid(row=7, column=1)

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(7, weight=1)

    def _load_trips(self):
        self.trips_lb.delete(0, tk.END)
        conn = get_connection()
        for row in conn.execute("SELECT id, name FROM trips ORDER BY name;"):
            self.trips_lb.insert(tk.END, f"{row[0]}: {row[1]}")
        conn.close()

    def _create_trip(self):
        name = simpledialog.askstring("Nuevo viaje", "Nombre del viaje:")
        if name:
            create_trip(name)
            self._load_trips()

    def _delete_trip(self):
        sel = self.trips_lb.curselection()
        if not sel:
            return
        trip_id = int(self.trips_lb.get(sel[0]).split(':')[0])
        if messagebox.askyesno("Confirmar", "Eliminar este viaje? Esto borrará todo."):
            delete_trip(trip_id)
            self._load_trips()

    def _clone_trip(self):
        sel = self.trips_lb.curselection()
        if not sel:
            return
        trip_id = int(self.trips_lb.get(sel[0]).split(':')[0])
        trip = get_trip(trip_id)
        if trip:
            create_trip(f"{trip[1]} (copia)")
            self._load_trips()

    def _open_trip(self):
        sel = self.trips_lb.curselection()
        if not sel:
            return
        trip_id = int(self.trips_lb.get(sel[0]).split(':')[0])
        TripWindow(self, trip_id)

    def _manage_categories(self):
        dlg = tk.Toplevel(self)
        dlg.title("Gestionar Categorías e Ítems")
        dlg.geometry("600x400")

        paned = ttk.Panedwindow(dlg, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left frame: categories
        left = ttk.Frame(paned, width=200)
        paned.add(left, weight=1)
        ttk.Label(left, text="Categorías").pack()
        cat_lb = tk.Listbox(left)
        cat_lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Buttons for category CRUD
        btnf = ttk.Frame(left)
        btnf.pack(pady=5)
        ttk.Button(btnf, text="Añadir", command=lambda: add_cat()).grid(row=0, column=0, padx=2)
        ttk.Button(btnf, text="Editar", command=lambda: edit_cat()).grid(row=0, column=1, padx=2)
        ttk.Button(btnf, text="Borrar", command=lambda: del_cat()).grid(row=0, column=2, padx=2)

        # Right frame: items of selected category
        right = ttk.Frame(paned, width=400)
        paned.add(right, weight=3)
        ttk.Label(right, text="Ítems de la categoría").pack()
        item_lb = tk.Listbox(right)
        item_lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Populate categories
        def load_cats():
            cat_lb.delete(0, tk.END)
            for cid, name in list_categories():
                cat_lb.insert(tk.END, f"{cid}: {name}")
        load_cats()

        # Load items when category selected
        def on_cat_select(evt):
            sel = cat_lb.curselection()
            if not sel:
                return
            cid = int(cat_lb.get(sel[0]).split(':')[0])
            item_lb.delete(0, tk.END)
            for iid, iname, cat_id in list_items():
                if cat_id == cid:
                    item_lb.insert(tk.END, f"{iid}: {iname}")
        cat_lb.bind("<<ListboxSelect>>", on_cat_select)

        # Category CRUD functions
        def add_cat():
            name = simpledialog.askstring("Nueva categoría", "Nombre:", parent=dlg)
            if name:
                create_category(name)
                load_cats()
        def edit_cat():
            sel = cat_lb.curselection()
            if not sel:
                return
            cid, old = cat_lb.get(sel[0]).split(': ')
            new = simpledialog.askstring("Editar categoría", "Nuevo nombre:", initialvalue=old, parent=dlg)
            if new:
                update_category(int(cid), new)
                load_cats()
        def del_cat():
            sel = cat_lb.curselection()
            if not sel:
                return
            cid = int(cat_lb.get(sel[0]).split(':')[0])
            if messagebox.askyesno("Confirmar", "Borrar categoría?", parent=dlg):
                delete_category(cid)
                item_lb.delete(0, tk.END)
                load_cats()
                # Add new item to selected category
        def add_item():
            sel = cat_lb.curselection()
            name = new_item_var.get().strip()
            if not sel or not name:
                messagebox.showerror("Error", "Seleccione categoría y escriba nombre de ítem.", parent=dlg)
                return
            cid = int(cat_lb.get(sel[0]).split(':')[0])
            create_item(name, cid)
            # refresh list
            on_cat_select(None)
            new_item_var.set("")
            messagebox.showinfo("OK", f"Ítem '{name}' añadido a la categoría.")

    def _manage_tags(self):
        dlg = tk.Toplevel(self)
        dlg.title("Gestionar Etiquetas")
        dlg.geometry("300x300")
        lb = tk.Listbox(dlg)
        lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        def load():
            lb.delete(0, tk.END)
            for tid, name in list_tags():
                lb.insert(tk.END, f"{tid}: {name}")
        load()
        def add():
            name = simpledialog.askstring("Nueva etiqueta", "Nombre:", parent=dlg)
            if name:
                create_tag(name)
                load()
        def edit():
            sel = lb.curselection()
            if not sel:
                return
            tid, old = lb.get(sel[0]).split(': ')
            new = simpledialog.askstring("Editar etiqueta", "Nuevo nombre:", initialvalue=old, parent=dlg)
            if new:
                update_tag(int(tid), new)
                load()
        def remove():
            sel = lb.curselection()
            if not sel:
                return
            tid = int(lb.get(sel[0]).split(':')[0])
            if messagebox.askyesno("Confirmar", "Borrar etiqueta?", parent=dlg):
                delete_tag(tid)
                load()
        bf = ttk.Frame(dlg)
        bf.pack(pady=5)
        ttk.Button(bf, text="Añadir", command=add).grid(row=0, column=0, padx=5)
        ttk.Button(bf, text="Editar", command=edit).grid(row=0, column=1, padx=5)
        ttk.Button(bf, text="Borrar", command=remove).grid(row=0, column=2, padx=5)

    def _create_item(self):
        dlg = tk.Toplevel(self)
        dlg.title("Crear Ítem")
        # Hacemos la ventana más alta y redimensionable
        dlg.geometry("500x600")
        dlg.resizable(True, True)

        # 1) Nombre
        ttk.Label(dlg, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dlg, textvariable=name_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        # 2) Categoría
        ttk.Label(dlg, text="Categoría:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        cat_cb = ttk.Combobox(dlg, values=[f"{cid}: {n}" for cid,n in list_categories()])
        cat_cb.grid(row=1, column=1, padx=5, pady=5)

        # 3) Etiquetas
        ttk.Label(dlg, text="Etiquetas (Ctrl+clic):").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        tags_lb = tk.Listbox(dlg, selectmode=tk.MULTIPLE, height=4)
        tags_lb.grid(row=2, column=1, padx=5, pady=5)
        for tid, name in list_tags():
            tags_lb.insert(tk.END, f"{tid}: {name}")

        # Ítems existentes en la categoría, con mayor altura
        ttk.Label(dlg, text="Ítems existentes en la categoría:") \
            .grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        exist_lb = tk.Listbox(dlg, height=12)  # de 6 → 12 filas visibles
        exist_lb.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
        
        # Si quieres que el Listbox crezca junto con el diálogo,
        # añade esto después de grid:
        dlg.grid_rowconfigure(3, weight=1)
        dlg.grid_columnconfigure(1, weight=1)

        # Función para recargar la lista cuando cambias de categoría:
        def update_existing(evt=None):
            exist_lb.delete(0, tk.END)
            sel = cat_cb.get().split(':')[0]
            if not sel.isdigit(): return
            cid = int(sel)
            for iid, iname, cat_id in list_items():
                if cat_id == cid:
                    exist_lb.insert(tk.END, f"{iid}: {iname}")

        cat_cb.bind("<<ComboboxSelected>>", update_existing)

        # 5) Botón Añadir que NO cierra el diálogo
        def add_and_clear():
            item_name = name_var.get().strip()
            sel_cat = cat_cb.get().split(':')[0]
            if not item_name or not sel_cat.isdigit():
                messagebox.showerror("Error", "Nombre y categoría requeridos", parent=dlg)
                return
            cid = int(sel_cat)
            item_id = create_item(item_name, cid)
            for idx in tags_lb.curselection():
                tid = int(tags_lb.get(idx).split(':')[0])
                assign_tag_to_item(item_id, tid)
            update_existing()        # refrescar la lista existente
            name_var.set("")        # limpiar el campo de nombre
            messagebox.showinfo("OK", f"Ítem '{item_name}' añadido.", parent=dlg)

        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=4, column=1, sticky="e", pady=10)
        ttk.Button(btn_frame, text="Añadir", command=add_and_clear).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cerrar", command=dlg.destroy).pack(side=tk.LEFT, padx=5)


class TripWindow(tk.Toplevel):
    def __init__(self, master, trip_id):
        super().__init__(master)
        # Obtener nombre del viaje para usar en el fichero
        trip = get_trip(trip_id)
        self.trip_id = trip_id
        self.trip_name = trip[1]
        self.title(f"Packing - {self.trip_name}")
        self.geometry("900x600")
        self.cat_map = {cid: name for cid, name in list_categories()}
        self.person_id = None
        self._create_ui()

    def _create_ui(self):
        left = ttk.Frame(self, padding=5)
        left.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(left, text="Personas").pack()
        self.persons_lb = tk.Listbox(left)
        self.persons_lb.pack(fill=tk.Y, expand=True)
        self._load_persons()
        ttk.Button(left, text="Gestionar personas", command=self._manage_persons).pack(pady=5)
        self.selected_lbl = ttk.Label(left, text="Seleccionado: Ninguno")
        self.selected_lbl.pack(pady=5)
        self.persons_lb.bind("<<ListboxSelect>>", lambda e: self._on_person_select())

        mid = ttk.Frame(self, padding=5)
        mid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.cat_cb = ttk.Combobox(mid, values=list(self.cat_map.values()))
        self.cat_cb.pack(fill=tk.X)
        ttk.Button(mid, text="Aplicar filtro", command=self._apply_filters).pack(pady=2)
        ttk.Button(mid, text="Limpiar filtros", command=self._clear_filters).pack(pady=2)
        self.items_lb = tk.Listbox(mid, selectmode=tk.MULTIPLE)
        self.items_lb.pack(fill=tk.BOTH, expand=True)
        qty_frame = ttk.Frame(mid)
        qty_frame.pack(fill=tk.X)
        ttk.Label(qty_frame, text="Cantidad").pack(side=tk.LEFT)
        self.qty_var = tk.IntVar(value=1)
        ttk.Entry(qty_frame, textvariable=self.qty_var, width=5).pack(side=tk.LEFT)
        ttk.Button(qty_frame, text="Agregar", command=self._add_items).pack(side=tk.LEFT, padx=5)

        right = ttk.Frame(self, padding=5)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(right, text="Asignados").pack()
        self.assigned_tv = ttk.Treeview(right, show='tree')
        self.assigned_tv.pack(fill=tk.BOTH, expand=True)
        ttk.Button(right, text="Quitar ítem", command=self._remove_items).pack(pady=5)
        ttk.Button(self, text="Imprimir", command=self._print_list).pack(side=tk.BOTTOM, pady=5)

    def _load_persons(self):
        self.persons_lb.delete(0, tk.END)
        conn = get_connection()
        for r in conn.execute("SELECT id, name FROM persons WHERE trip_id=?;", (self.trip_id,)):
            self.persons_lb.insert(tk.END, f"{r[0]}: {r[1]}")
        conn.close()

    def _manage_persons(self):
        dlg = tk.Toplevel(self)
        dlg.title("Gestionar personas")
        dlg.geometry("300x300")
        lb = tk.Listbox(dlg)
        lb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        def load_list():
            lb.delete(0, tk.END)
            conn = get_connection()
            for r in conn.execute("SELECT id, name FROM persons WHERE trip_id=?;", (self.trip_id,)):
                lb.insert(tk.END, f"{r[0]}: {r[1]}")
            conn.close()
        load_list()
        def add_person():
            name = simpledialog.askstring("Nueva persona", "Nombre:", parent=dlg)
            if name:
                create_person(self.trip_id, name)
                load_list()
                self._load_persons()
        def edit_person():
            sel = lb.curselection()
            if not sel:
                return
            pid, old = lb.get(sel[0]).split(': ')
            new = simpledialog.askstring("Editar persona", "Nuevo nombre:", initialvalue=old, parent=dlg)
            if new:
                update_person(int(pid), new)
                load_list()
                self._load_persons()
        def remove_person():
            sel = lb.curselection()
            if not sel:
                return
            pid = int(lb.get(sel[0]).split(':')[0])
            if messagebox.askyesno("Confirmar", "Borrar persona?", parent=dlg):
                delete_person(pid)
                load_list()
                self._load_persons()
        bf = ttk.Frame(dlg)
        bf.pack(pady=5)
        ttk.Button(bf, text="Añadir", command=add_person).grid(row=0, column=0, padx=5)
        ttk.Button(bf, text="Editar", command=edit_person).grid(row=0, column=1, padx=5)
        ttk.Button(bf, text="Borrar", command=remove_person).grid(row=0, column=2, padx=5)

    def _on_person_select(self):
        sel = self.persons_lb.curselection()
        if not sel:
            return
        pid, name = self.persons_lb.get(sel[0]).split(': ')
        self.person_id = int(pid)
        self.selected_lbl.config(text=f"Seleccionado: {name}")
        self._load_catalog()
        self._load_assigned()

    def _get_available_items(self, category=None):
        """Return catalog items not yet assigned to the selected person."""
        items = list_items()
        if category:
            items = [i for i in items if self.cat_map.get(i[2]) == category]
        if self.person_id is not None:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT item_id FROM trip_items WHERE trip_id=? AND person_id=?;",
                (self.trip_id, self.person_id),
            )
            assigned = {row[0] for row in cur.fetchall()}
            conn.close()
            items = [i for i in items if i[0] not in assigned]
        return items

    def _load_catalog(self):
        self.items_lb.delete(0, tk.END)
        for itm in self._get_available_items():
            self.items_lb.insert(tk.END, f"{itm[0]}: {itm[1]}")

    def _apply_filters(self):
        cat = self.cat_cb.get() or None
        items = self._get_available_items(cat)
        self.items_lb.delete(0, tk.END)
        for i in items:
            self.items_lb.insert(tk.END, f"{i[0]}: {i[1]}")

    def _clear_filters(self):
        self.cat_cb.set("")
        self._load_catalog()

    def _add_items(self):
        sel = self.items_lb.curselection()
        if not sel or self.person_id is None:
            return
        conn = get_connection()
        cur = conn.cursor()
        dups = []
        for idx in sel:
            item_id = int(self.items_lb.get(idx).split(':')[0])
            assign_item(self.trip_id, self.person_id, item_id, self.qty_var.get())
        conn.close()
        if dups:
            names = []
            for d in dups:
                c2 = get_connection()
                nm = c2.execute("SELECT name FROM items WHERE id=?;", (d,)).fetchone()[0]
                c2.close()
                names.append(nm)
            messagebox.showwarning("Duplicados", f"Los siguientes ítems ya estaban asignados: {', '.join(names)}")
        self._load_catalog()
        self._load_assigned()

    def _load_assigned(self):
        for c in self.assigned_tv.get_children():
            self.assigned_tv.delete(c)
        conn = get_connection()
        data = conn.execute(
            """
            SELECT ti.id, i.name, c.name, ti.quantity
            FROM trip_items ti
            JOIN items i ON ti.item_id=i.id
            JOIN categories c ON i.category_id=c.id
            WHERE ti.trip_id=? AND ti.person_id=?
            ORDER BY c.name, i.name
            """, (self.trip_id, self.person_id)
        ).fetchall()
        conn.close()
        grouped = {}
        for tid, name, cat, qty in data:
            grouped.setdefault(cat, []).append((tid, name, qty))
        for cat, items in grouped.items():
            parent = self.assigned_tv.insert('', 'end', text=cat)
            for tid, name, qty in items:
                self.assigned_tv.insert(parent, 'end', iid=str(tid), text=f"{name} x{qty}")

    def _remove_items(self):
        sel = self.assigned_tv.selection()
        if not sel:
            messagebox.showinfo("Info", "Seleccione un ítem para quitar")
            return
        for iid in sel:
            try:
                aid = int(iid)
            except ValueError:
                continue
            if messagebox.askyesno("Confirmar", "Eliminar ítem asignado?", parent=self):
                remove_assignment(aid)
        self._load_assigned()
        
    def _load_available_items(self):
        # Limpio la lista
        self.available_lb.delete(0, tk.END)

        # 1) Identifico categoría y persona
        cat_txt = self.cat_filter_cb.get()
        if ':' not in cat_txt or self.person_id is None:
            return
        cid = int(cat_txt.split(':')[0])

        # 2) Recojo todos los ítems de esa categoría
        all_items = [(iid, iname) 
                     for iid, iname, cat_id in list_items() 
                     if cat_id == cid]

        # 3) Consulto los ítems ya asignados a esta persona
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
          "SELECT item_id FROM trip_items WHERE trip_id=? AND person_id=?",
          (self.trip_id, self.person_id)
        )
        assigned_ids = {row[0] for row in cur.fetchall()}
        conn.close()

        # 4) Sólo muestro los NO asignados
        for iid, iname in all_items:
            if iid not in assigned_ids:
                self.available_lb.insert(tk.END, f"{iid}: {iname}")


    def _print_list(self):
        # Construir contenido
        content = []
        conn = get_connection()
        for pid, pname in conn.execute("SELECT id, name FROM persons WHERE trip_id=?;", (self.trip_id,)):
            content.append(f"=== {pname} ===")
            current_cat = None
            for cat, iname, qty in conn.execute(
                """
                SELECT c.name, i.name, ti.quantity
                FROM trip_items ti
                JOIN items i ON ti.item_id=i.id
                JOIN categories c ON i.category_id=c.id
                WHERE ti.trip_id=? AND ti.person_id=?
                ORDER BY c.name, i.name
                """, (self.trip_id, pid)
            ):
                if cat != current_cat:
                    content.append(f"-- {cat} --")
                    current_cat = cat
                content.append(f"   {iname}: {qty}")
        conn.close()
        # Nombre fichero con viaje y fecha
        now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        safe_name = "".join(c for c in self.trip_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_name}_{now}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        messagebox.showinfo("Guardado", f"Lista guardada en {os.path.abspath(filename)}")

if __name__ == "__main__":
    app = PackingApp()
    app.mainloop()
