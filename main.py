import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.expenses = []
        self.load_data()
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Категория:").grid(row=1, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Жильё", "Прочее"]
        self.category_combo = ttk.Combobox(self.root, textvariable=self.category_var, values=categories)
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления
        tk.Button(self.root, text="Добавить расход", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица
        self.tree = ttk.Treeview(self.root, columns=("Сумма", "Категория", "Дата"), show="headings")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Фильтрация
        tk.Label(self.root, text="Фильтр по категории:").grid(row=5, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_combo = ttk.Combobox(self.root, textvariable=self.filter_category_var, values=["Все"] + categories)
        self.filter_combo.set("Все")
        self.filter_combo.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Период с (ГГГГ-ММ-ДД):").grid(row=6, column=0, padx=5, pady=5)
        self.start_date_entry = tk.Entry(self.root)
        self.start_date_entry.grid(row=6, column=1, padx=5, pady=5)

        tk.Label(self.root, text="по (ГГГГ-ММ-ДД):").grid(row=7, column=0, padx=5, pady=5)
        self.end_date_entry = tk.Entry(self.root)
        self.end_date_entry.grid(row=7, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Применить фильтры", command=self.apply_filters).grid(row=8, column=0, columnspan=2, pady=5)

        # Подсчёт суммы
        self.total_label = tk.Label(self.root, text="Общая сумма: 0")
        self.total_label.grid(row=9, column=0, columnspan=2, pady=5)

    def validate_input(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")
            return False

        date_str = self.date_entry.get()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты (используйте ГГГГ-ММ-ДД)")
            return False

        if not self.category_var.get():
            messagebox.showerror("Ошибка", "Выберите категорию")
            return False

        return True

    def add_expense(self):
        if not self.validate_input():
            return

        expense = {
            "amount": float(self.amount_entry.get()),
            "category": self.category_var.get(),
            "date": self.date_entry.get()
        }
        self.expenses.append(expense)
        self.save_data()
        self.update_table()
        self.clear_form()

    def clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.category_var.set("")

    def load_data(self):
        try:
            with open("expenses.json", "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []

    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def apply_filters(self):
        filtered = self.expenses

        # Фильтр по категории
        category = self.filter_category_var.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]

        # Фильтр по дате
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= start]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат начальной даты")
                return

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= end]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат конечной даты")
                return

        self.update_table(filtered)
        total = sum(e["amount"] for e in filtered)
        self.total_label.config(text=f"Общая сумма: {total}")

    def update_table(self, expenses=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        data = expenses if expenses is not None else self.expenses
        for expense in data:
            self.tree.insert("", "end", values=(expense["amount"], expense["category"], expense["date"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
