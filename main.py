import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
from datetime import datetime
import calendar

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi To-Do List")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Inisialisasi database
        self.init_database()
        
        # Setup GUI
        self.setup_gui()
        
        # Load data
        self.load_tasks()
    
    def init_database(self):
        """Inisialisasi database SQLite"""
        self.conn = sqlite3.connect('todo_list.db')
        self.cursor = self.conn.cursor()
        
        # Buat tabel jika belum ada
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                priority TEXT DEFAULT 'Sedang',
                status TEXT DEFAULT 'Belum Selesai',
                created_date TEXT,
                completed_date TEXT,
                deadline_date TEXT,
                deadline_time TEXT,
                notes TEXT DEFAULT ''
            )
        ''')
        self.conn.commit()
    
    def reset_autoincrement(self):
        """Reset autoincrement ID ke 1"""
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
        self.conn.commit()
    
    def reorder_ids(self):
        """Mengatur ulang ID dari 1 secara berurutan"""
        self.cursor.execute("SELECT * FROM tasks ORDER BY id")
        all_tasks = self.cursor.fetchall()
        
        if not all_tasks:
            self.reset_autoincrement()
            return
        
        # Hapus semua data
        self.cursor.execute("DELETE FROM tasks")
        self.reset_autoincrement()
        
        # Insert ulang dengan ID berurutan
        for task in all_tasks:
            self.cursor.execute('''
                INSERT INTO tasks (task, priority, status, created_date, completed_date, deadline_date, deadline_time, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task[1], task[2], task[3], task[4], task[5], task[6], task[7], task[8] if len(task) > 8 else ''))
        
        self.conn.commit()
    
    def setup_gui(self):
        """Setup antarmuka GUI"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame, 
            text="📝 DAFTAR TUGAS SAYA",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg="#ecf0f1", pady=15)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Baris 1: Task Entry dan Priority
        tk.Label(
            input_frame, 
            text="Tugas Baru:", 
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.task_entry = tk.Entry(input_frame, width=35, font=("Arial", 10))
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        self.task_entry.bind('<Return>', lambda e: self.add_task())
        
        tk.Label(
            input_frame, 
            text="Prioritas:", 
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        ).grid(row=0, column=3, sticky="w", padx=5)
        
        self.priority_var = tk.StringVar(value="Sedang")
        priority_dropdown = ttk.Combobox(
            input_frame, 
            textvariable=self.priority_var,
            values=["Rendah", "Sedang", "Tinggi"],
            state="readonly",
            width=10
        )
        priority_dropdown.grid(row=0, column=4, padx=5)
        
        # Baris 2: Deadline Date dan Time
        tk.Label(
            input_frame, 
            text="Deadline:", 
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        ).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Date Frame dengan dropdown
        date_frame = tk.Frame(input_frame, bg="#ecf0f1")
        date_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Day
        self.day_var = tk.StringVar(value=str(datetime.now().day))
        day_spin = ttk.Combobox(
            date_frame,
            textvariable=self.day_var,
            values=[str(i) for i in range(1, 32)],
            width=3,
            state="readonly"
        )
        day_spin.pack(side=tk.LEFT, padx=2)
        
        tk.Label(date_frame, text="/", bg="#ecf0f1").pack(side=tk.LEFT)
        
        # Month
        self.month_var = tk.StringVar(value=str(datetime.now().month))
        month_spin = ttk.Combobox(
            date_frame,
            textvariable=self.month_var,
            values=[str(i) for i in range(1, 13)],
            width=3,
            state="readonly"
        )
        month_spin.pack(side=tk.LEFT, padx=2)
        
        tk.Label(date_frame, text="/", bg="#ecf0f1").pack(side=tk.LEFT)
        
        # Year
        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        year_spin = ttk.Combobox(
            date_frame,
            textvariable=self.year_var,
            values=[str(i) for i in range(current_year, current_year + 5)],
            width=5,
            state="readonly"
        )
        year_spin.pack(side=tk.LEFT, padx=2)
        
        # Time Frame
        time_frame = tk.Frame(input_frame, bg="#ecf0f1")
        time_frame.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        
        # Hour Spinbox
        self.hour_var = tk.StringVar(value="12")
        hour_spin = tk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            width=3,
            textvariable=self.hour_var,
            font=("Arial", 10),
            format="%02.0f"
        )
        hour_spin.pack(side=tk.LEFT)
        
        tk.Label(time_frame, text=":", bg="#ecf0f1", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Minute Spinbox
        self.minute_var = tk.StringVar(value="00")
        minute_spin = tk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=3,
            textvariable=self.minute_var,
            font=("Arial", 10),
            format="%02.0f"
        )
        minute_spin.pack(side=tk.LEFT)
        
        # Add Button
        add_btn = tk.Button(
            input_frame,
            text="➕ Tambah",
            command=self.add_task,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=15,
            pady=5
        )
        add_btn.grid(row=1, column=4, padx=5, pady=5)
        
        # Button Frame
        btn_frame = tk.Frame(self.root, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Action Buttons
        complete_btn = tk.Button(
            btn_frame,
            text="✓ Tandai Selesai",
            command=self.complete_task,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            padx=10
        )
        complete_btn.pack(side=tk.LEFT, padx=5)
        
        edit_btn = tk.Button(
            btn_frame,
            text="✎ Edit",
            command=self.edit_task,
            bg="#f39c12",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            padx=10
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(
            btn_frame,
            text="🗑 Hapus",
            command=self.delete_task,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            padx=10
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑 Hapus Semua",
            command=self.clear_all,
            bg="#c0392b",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            padx=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Info label untuk notes
        info_label = tk.Label(
            btn_frame,
            text="💡 Double-click tugas untuk menambah catatan",
            bg="#ecf0f1",
            fg="#7f8c8d",
            font=("Arial", 8, "italic")
        )
        info_label.pack(side=tk.RIGHT, padx=10)
        
        # Treeview Frame
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Tugas", "Prioritas", "Status", "Deadline", "Dibuat"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=13
        )
        scrollbar.config(command=self.tree.yview)
        
        # Define columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tugas", text="Tugas")
        self.tree.heading("Prioritas", text="Prioritas")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Deadline", text="Deadline")
        self.tree.heading("Dibuat", text="Tanggal Dibuat")
        
        # Column widths
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Tugas", width=280)
        self.tree.column("Prioritas", width=80, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Deadline", width=150, anchor="center")
        self.tree.column("Dibuat", width=130, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.open_notes)
        
        # Tags untuk warna
        self.tree.tag_configure("completed", background="#d5f4e6")
        self.tree.tag_configure("has_notes", background="#4BCAF0")
        self.tree.tag_configure("pending", background="#ffffff")
        self.tree.tag_configure("overdue", background="#fadbd8")
        
        # Footer
        footer_frame = tk.Frame(self.root, bg="#34495e", height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            footer_frame,
            text="Total Tugas: 0 | Selesai: 0 | Belum Selesai: 0 | Terlambat: 0",
            bg="#34495e",
            fg="white",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=5)
    
    def open_notes(self, event):
        """Buka window untuk menambah/edit catatan"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        task_name = item['values'][1]
        
        # Ambil notes dari database
        self.cursor.execute("SELECT notes FROM tasks WHERE id = ?", (task_id,))
        result = self.cursor.fetchone()
        current_notes = result[0] if result and result[0] else ""
        
        # Buat window notes
        notes_window = tk.Toplevel(self.root)
        notes_window.title(f"Catatan - {task_name[:50]}...")
        notes_window.geometry("500x400")
        
        # Header
        header = tk.Frame(notes_window, bg="#3498db")
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text=f"📝 Catatan untuk: {task_name}",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            wraplength=450
        ).pack(pady=10, padx=10)
        
        # Text area dengan scrollbar
        text_frame = tk.Frame(notes_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        notes_text = scrolledtext.ScrolledText(
            text_frame,
            font=("Arial", 10),
            wrap=tk.WORD,
            width=50,
            height=15
        )
        notes_text.pack(fill=tk.BOTH, expand=True)
        notes_text.insert("1.0", current_notes)
        notes_text.focus()
        
        # Button frame
        btn_frame = tk.Frame(notes_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_notes():
            new_notes = notes_text.get("1.0", tk.END).strip()
            self.cursor.execute(
                "UPDATE tasks SET notes = ? WHERE id = ?",
                (new_notes, task_id)
            )
            self.conn.commit()
            self.load_tasks()
            notes_window.destroy()
            messagebox.showinfo("Sukses", "Catatan berhasil disimpan!")
        
        def clear_notes():
            if messagebox.askyesno("Konfirmasi", "Hapus semua catatan?"):
                self.cursor.execute(
                    "UPDATE tasks SET notes = ? WHERE id = ?",
                    ("", task_id)
                )
                self.conn.commit()
                self.load_tasks()
                notes_text.delete("1.0", tk.END)
                notes_window.destroy()
                messagebox.showinfo("Sukses", f"Catatan pada '{task_name}' berhasil dihapus")
        
        tk.Button(
            btn_frame,
            text="💾 Simpan Catatan",
            command=save_notes,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🗑 Hapus Catatan",
            command=clear_notes,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Tutup",
            command=notes_window.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20
        ).pack(side=tk.RIGHT, padx=5)
    
    def add_task(self):
        """Tambah tugas baru"""
        task = self.task_entry.get().strip()
        priority = self.priority_var.get()
        
        if not task:
            messagebox.showwarning("Peringatan", "Mohon masukkan tugas!")
            return
        
        # Validasi tanggal
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            
            # Cek apakah tanggal valid
            datetime(year, month, day)
        except ValueError:
            messagebox.showerror("Error", "Tanggal tidak valid!")
            return
        
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Get deadline
        deadline_date = f"{year}-{month:02d}-{day:02d}"
        deadline_time = f"{self.hour_var.get().zfill(2)}:{self.minute_var.get().zfill(2)}"
        
        self.cursor.execute(
            "INSERT INTO tasks (task, priority, status, created_date, deadline_date, deadline_time, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (task, priority, "Belum Selesai", created_date, deadline_date, deadline_time, "")
        )
        self.conn.commit()
        
        self.task_entry.delete(0, tk.END)
        self.load_tasks()
        messagebox.showinfo("Sukses", "Tugas berhasil ditambahkan!")
    
    def is_overdue(self, deadline_date, deadline_time, status):
        """Cek apakah tugas sudah melewati deadline"""
        if status == "Selesai":
            return False
        
        try:
            deadline_str = f"{deadline_date} {deadline_time}"
            deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
            return datetime.now() > deadline_dt
        except:
            return False
    
    def load_tasks(self):
        """Load semua tugas dari database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load from database
        self.cursor.execute(
            "SELECT id, task, priority, status, created_date, deadline_date, deadline_time, notes FROM tasks ORDER BY deadline_date, deadline_time"
        )
        rows = self.cursor.fetchall()
        
        total = len(rows)
        completed = 0
        overdue = 0
        
        for row in rows:
            task_id, task, priority, status, created_date, deadline_date, deadline_time, notes = row
            
            # Format deadline untuk display
            try:
                deadline_dt = datetime.strptime(f"{deadline_date} {deadline_time}", "%Y-%m-%d %H:%M")
                deadline_display = deadline_dt.strftime("%d/%m/%Y %H:%M")
            except:
                deadline_display = "Tidak ada"
            
            # Format created date
            try:
                created_dt = datetime.strptime(created_date, "%Y-%m-%d %H:%M")
                created_display = created_dt.strftime("%d/%m/%Y %H:%M")
            except:
                created_display = created_date

            # Cek status notes apakah ada atau tidak
            current_tags = []
            
            # Tentukan tag berdasarkan status dan deadline
            if status == "Selesai":
                current_tags.append("completed")
                completed += 1
            elif self.is_overdue(deadline_date, deadline_time, status):
                current_tags.append("overdue")
                overdue += 1
            else:
                current_tags.append("pending")

            if notes and notes.strip():
                current_tags.append("has_notes")
            
            self.tree.insert(
                "", 
                tk.END, 
                values=(task_id, task, priority, status, deadline_display, created_display),
                tags=tuple(current_tags)
            )
        
        pending = total - completed
        self.status_label.config(
            text=f"Total Tugas: {total} | Selesai: {completed} | Belum Selesai: {pending} | Terlambat: {overdue}"
        )
    
    def complete_task(self):
        """Tandai tugas sebagai selesai"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih tugas terlebih dahulu!")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        current_status = item['values'][3]
        
        if current_status == "Selesai":
            messagebox.showinfo("Info", "Tugas sudah selesai!")
            return
        
        completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute(
            "UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?",
            ("Selesai", completed_date, task_id)
        )
        self.conn.commit()
        
        self.load_tasks()
        messagebox.showinfo("Sukses", "Tugas ditandai selesai!")
    
    def edit_task(self):
        """Edit tugas yang dipilih"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih tugas terlebih dahulu!")
            return
        
        item = self.tree.item(selected[0])
        task_id = item['values'][0]
        current_task = item['values'][1]
        
        # Get current deadline
        self.cursor.execute(
            "SELECT deadline_date, deadline_time FROM tasks WHERE id = ?",
            (task_id,)
        )
        deadline_data = self.cursor.fetchone()
        
        # Dialog edit
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Tugas")
        edit_window.geometry("450x240")
        edit_window.resizable(False, False)
        
        tk.Label(edit_window, text="Edit Tugas:", font=("Arial", 10, "bold")).pack(pady=10)
        
        edit_entry = tk.Entry(edit_window, width=50, font=("Arial", 10))
        edit_entry.pack(pady=5)
        edit_entry.insert(0, current_task)
        edit_entry.focus()
        
        # Deadline edit frame
        deadline_frame = tk.Frame(edit_window)
        deadline_frame.pack(pady=10)
        
        tk.Label(deadline_frame, text="Deadline Baru:", font=("Arial", 10, "bold")).pack()
        
        date_time_frame = tk.Frame(deadline_frame)
        date_time_frame.pack(pady=5)
        
        # Date dropdowns
        date_edit_frame = tk.Frame(date_time_frame)
        date_edit_frame.pack(side=tk.LEFT, padx=5)
        
        edit_day_var = tk.StringVar(value=str(datetime.now().day))
        edit_month_var = tk.StringVar(value=str(datetime.now().month))
        edit_year_var = tk.StringVar(value=str(datetime.now().year))
        
        # Set current deadline date
        if deadline_data and deadline_data[0]:
            try:
                current_date = datetime.strptime(deadline_data[0], "%Y-%m-%d")
                edit_day_var.set(str(current_date.day))
                edit_month_var.set(str(current_date.month))
                edit_year_var.set(str(current_date.year))
            except:
                pass
        
        # Day
        day_edit = ttk.Combobox(
            date_edit_frame,
            textvariable=edit_day_var,
            values=[str(i) for i in range(1, 32)],
            width=3,
            state="readonly"
        )
        day_edit.pack(side=tk.LEFT, padx=2)
        
        tk.Label(date_edit_frame, text="/").pack(side=tk.LEFT)
        
        # Month
        month_edit = ttk.Combobox(
            date_edit_frame,
            textvariable=edit_month_var,
            values=[str(i) for i in range(1, 13)],
            width=3,
            state="readonly"
        )
        month_edit.pack(side=tk.LEFT, padx=2)
        
        tk.Label(date_edit_frame, text="/").pack(side=tk.LEFT)
        
        # Year
        current_year = datetime.now().year
        year_edit = ttk.Combobox(
            date_edit_frame,
            textvariable=edit_year_var,
            values=[str(i) for i in range(current_year, current_year + 5)],
            width=5,
            state="readonly"
        )
        year_edit.pack(side=tk.LEFT, padx=2)
        
        # Time spinboxes
        time_edit_frame = tk.Frame(date_time_frame)
        time_edit_frame.pack(side=tk.LEFT, padx=10)
        
        edit_hour_var = tk.StringVar(value="12")
        edit_minute_var = tk.StringVar(value="00")
        
        # Set current time
        if deadline_data and deadline_data[1]:
            try:
                time_parts = deadline_data[1].split(":")
                edit_hour_var.set(time_parts[0].zfill(2))
                edit_minute_var.set(time_parts[1].zfill(2))
            except:
                pass
        
        hour_edit_spin = tk.Spinbox(
            time_edit_frame,
            from_=0,
            to=23,
            width=3,
            textvariable=edit_hour_var,
            font=("Arial", 10),
            format="%02.0f"
        )
        hour_edit_spin.pack(side=tk.LEFT)
        
        tk.Label(time_edit_frame, text=":", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        minute_edit_spin = tk.Spinbox(
            time_edit_frame,
            from_=0,
            to=59,
            width=3,
            textvariable=edit_minute_var,
            font=("Arial", 10),
            format="%02.0f"
        )
        minute_edit_spin.pack(side=tk.LEFT)
        
        def save_edit():
            new_task = edit_entry.get().strip()
            if not new_task:
                messagebox.showwarning("Peringatan", "Tugas tidak boleh kosong!")
                return
            
            # Validasi tanggal
            try:
                day = int(edit_day_var.get())
                month = int(edit_month_var.get())
                year = int(edit_year_var.get())
                datetime(year, month, day)
            except ValueError:
                messagebox.showerror("Error", "Tanggal tidak valid!")
                return
            
            new_deadline_date = f"{year}-{month:02d}-{day:02d}"
            new_deadline_time = f"{edit_hour_var.get().zfill(2)}:{edit_minute_var.get().zfill(2)}"
            
            self.cursor.execute(
                "UPDATE tasks SET task = ?, deadline_date = ?, deadline_time = ? WHERE id = ?",
                (new_task, new_deadline_date, new_deadline_time, task_id)
            )
            self.conn.commit()
            self.load_tasks()
            edit_window.destroy()
            messagebox.showinfo("Sukses", "Tugas berhasil diupdate!")
        
        tk.Button(
            edit_window, 
            text="Simpan", 
            command=save_edit,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10),
            cursor="hand2"
        ).pack(pady=10)
    
    def delete_task(self):
        """Hapus tugas yang dipilih"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih tugas terlebih dahulu!")
            return
        
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus tugas ini?"):
            item = self.tree.item(selected[0])
            task_id = item['values'][0]
            
            self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            
            # Reset ID setelah hapus
            self.reorder_ids()
            
            self.load_tasks()
            messagebox.showinfo("Sukses", "Tugas berhasil dihapus!")
    
    def clear_all(self):
        """Hapus semua tugas"""
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus SEMUA tugas?"):
            self.cursor.execute("DELETE FROM tasks")
            self.conn.commit()
            
            # Reset autoincrement
            self.reset_autoincrement()
            
            self.load_tasks()
            messagebox.showinfo("Sukses", "Semua tugas berhasil dihapus!")
    
    def __del__(self):
        """Tutup koneksi database saat aplikasi ditutup"""
        if hasattr(self, 'conn'):
            self.conn.close()

# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()