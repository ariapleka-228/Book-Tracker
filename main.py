import json
import os
from tkinter import *
from tkinter import messagebox, ttk

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker — Трекер прочитанных книг")
        self.root.geometry("900x500")
        self.root.resizable(False, False)

        self.books = self.load_books()
        self.filtered_books = self.books.copy()

        # Поля ввода
        self.create_input_fields()
        # Кнопки
        self.create_buttons()
        # Таблица
        self.create_table()
        # Фильтры
        self.create_filters()

        self.update_table()

    # ========== Работа с JSON ==========
    def load_books(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_books(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

    # ========== GUI элементы ==========
    def create_input_fields(self):
        frame = Frame(self.root)
        frame.pack(pady=10)

        labels = ["Название книги:", "Автор:", "Жанр:", "Количество страниц:"]
        self.entries = {}

        for i, text in enumerate(labels):
            Label(frame, text=text).grid(row=0, column=i*2, padx=5, pady=5, sticky="e")
            entry = Entry(frame, width=20)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.entries[text] = entry

    def create_buttons(self):
        btn_frame = Frame(self.root)
        btn_frame.pack(pady=5)

        Button(btn_frame, text="➕ Добавить книгу", command=self.add_book, bg="lightgreen", width=20).pack(side=LEFT, padx=5)
        Button(btn_frame, text="🗑 Удалить выбранную", command=self.delete_book, bg="salmon", width=20).pack(side=LEFT, padx=5)
        Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_books, bg="lightblue", width=20).pack(side=LEFT, padx=5)

    def create_table(self):
        columns = ("Название", "Автор", "Жанр", "Страницы")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)

        scrollbar = Scrollbar(self.root, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True, padx=(10,0), pady=10)
        scrollbar.pack(side=RIGHT, fill=Y, pady=10)

    def create_filters(self):
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill=X, padx=10, pady=5)

        Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5)
        self.genre_filter = Entry(filter_frame, width=20)
        self.genre_filter.grid(row=0, column=1, padx=5)

        Label(filter_frame, text="Страниц >").grid(row=0, column=2, padx=5)
        self.pages_filter = Entry(filter_frame, width=10)
        self.pages_filter.grid(row=0, column=3, padx=5)

        Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter, bg="lightyellow").grid(row=0, column=4, padx=10)
        Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter, bg="#f0f0f0").grid(row=0, column=5, padx=5)

    # ========== Логика ==========
    def add_book(self):
        title = self.entries["Название книги:"].get().strip()
        author = self.entries["Автор:"].get().strip()
        genre = self.entries["Жанр:"].get().strip()
        pages = self.entries["Количество страниц:"].get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка, что страницы — число
        if not pages.isdigit():
            messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
            return

        pages = int(pages)

        self.books.append({
            "Название": title,
            "Автор": author,
            "Жанр": genre,
            "Страницы": pages
        })

        self.save_books()
        self.reset_filter()
        self.clear_entries()

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления!")
            return

        for item in selected:
            values = self.tree.item(item, "values")
            title, author, genre, pages = values
            pages = int(pages)

            # Удаляем из основного списка
            self.books = [b for b in self.books if not (b["Название"] == title and b["Автор"] == author)]

        self.save_books()
        self.reset_filter()

    def apply_filter(self):
        genre = self.genre_filter.get().strip().lower()
        pages_str = self.pages_filter.get().strip()

        self.filtered_books = self.books.copy()

        if genre:
            self.filtered_books = [b for b in self.filtered_books if genre in b["Жанр"].lower()]

        if pages_str:
            if pages_str.isdigit():
                pages_min = int(pages_str)
                self.filtered_books = [b for b in self.filtered_books if b["Страницы"] > pages_min]
            else:
                messagebox.showerror("Ошибка", "Значение страниц должно быть числом!")
                return

        self.update_table(data=self.filtered_books)

    def reset_filter(self):
        self.genre_filter.delete(0, END)
        self.pages_filter.delete(0, END)
        self.filtered_books = self.books.copy()
        self.update_table()

    def update_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if data is None:
            data = self.books

        for book in data:
            self.tree.insert("", END, values=(book["Название"], book["Автор"], book["Жанр"], book["Страницы"]))

    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, END)

if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()
