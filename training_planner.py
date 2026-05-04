import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "workouts.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")

        # Данные тренировок: список словарей {"date": "YYYY-MM-DD", "type": str, "duration": float}
        self.workouts = []
        self.current_filter_type = "All"
        self.current_filter_date = ""

        # Загрузка данных из JSON
        self.load_data()

        # Построение интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()

    # ---------- Работа с JSON ----------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.workouts = json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showerror("Ошибка", "Не удалось загрузить данные из файла.")
                self.workouts = []

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.workouts, f, indent=4, ensure_ascii=False)
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные.")

    # ---------- Вспомогательные методы ----------
    def validate_date(self, date_str):
        """Проверка формата даты YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        """Проверка, что длительность — положительное число"""
        try:
            val = float(duration_str)
            return val > 0, val
        except ValueError:
            return False, None

    def get_distinct_types(self):
        """Возвращает отсортированный список уникальных типов тренировок"""
        types = sorted(set(w["type"] for w in self.workouts))
        return types

    def update_type_filter_combobox(self):
        """Обновляет варианты в фильтре по типу"""
        types = self.get_distinct_types()
        self.type_filter_combo['values'] = ["All"] + types
        if self.current_filter_type not in types and self.current_filter_type != "All":
            self.current_filter_type = "All"
            self.type_filter_combo.set("All")
        else:
            self.type_filter_combo.set(self.current_filter_type)

    # ---------- Основные операции ----------
    def add_workout(self):
        date = self.date_entry.get().strip()
        wtype = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()

        # Валидация
        if not date or not wtype or not duration:
            messagebox.showwarning("Предупреждение", "Заполните все поля.")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД (например, 2025-03-30).")
            return

        is_valid, dur_val = self.validate_duration(duration)
        if not is_valid:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом (целым или дробным).")
            return

        # Добавление
        self.workouts.append({
            "date": date,
            "type": wtype,
            "duration": dur_val
        })
        self.save_data()
        self.update_type_filter_combobox()
        self.refresh_table()
        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Информация", "Выберите запись для удаления.")
            return

        # Получаем идентификатор строки в treeview (виртуальный)
        for item in selected:
            values = self.tree.item(item, "values")
            if values:
                # Ищем тренировку в списке по дате, типу и длительности (может быть несколько одинаковых)
                # Для уникальности можно использовать индекс, но проще удалить первый подходящий
                for i, w in enumerate(self.workouts):
                    if (w["date"] == values[0] and w["type"] == values[1] and
                        abs(w["duration"] - float(values[2])) < 0.001):
                        del self.workouts[i]
                        break
        self.save_data()
        self.update_type_filter_combobox()
        self.refresh_table()

    def apply_filter(self):
        """Применить текущие значения фильтров"""
        type_val = self.type_filter_combo.get()
        date_val = self.date_filter_entry.get().strip()

        self.current_filter_type = type_val if type_val != "All" else "All"
        self.current_filter_date = date_val
        self.refresh_table()

    def reset_filter(self):
        """Сбросить фильтры и показать все записи"""
        self.type_filter_combo.set("All")
        self.date_filter_entry.delete(0, tk.END)
        self.current_filter_type = "All"
        self.current_filter_date = ""
        self.refresh_table()

    def refresh_table(self):
        """Очищает и заполняет таблицу с учётом фильтров"""
        # Очистка
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self.workouts[:]
        # Фильтр по типу
        if self.current_filter_type != "All":
            filtered = [w for w in filtered if w["type"] == self.current_filter_type]
        # Фильтр по дате
        if self.current_filter_date:
            filtered = [w for w in filtered if w["date"] == self.current_filter_date]

        # Заполнение
        for w in filtered:
            self.tree.insert("", tk.END, values=(w["date"], w["type"], w["duration"]))

    # ---------- Построение GUI ----------
    def create_widgets(self):
        # Левая панель: добавление тренировки
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_entry = ttk.Entry(left_frame, width=20)
        self.date_entry.grid(row=0, column=1, pady=5)

        ttk.Label(left_frame, text="Тип тренировки:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.type_entry = ttk.Entry(left_frame, width=20)
        self.type_entry.grid(row=1, column=1, pady=5)

        ttk.Label(left_frame, text="Длительность (мин):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.duration_entry = ttk.Entry(left_frame, width=20)
        self.duration_entry.grid(row=2, column=1, pady=5)

        add_btn = ttk.Button(left_frame, text="Добавить тренировку", command=self.add_workout)
        add_btn.grid(row=3, column=0, columnspan=2, pady=10)

        delete_btn = ttk.Button(left_frame, text="Удалить выбранную", command=self.delete_selected)
        delete_btn.grid(row=4, column=0, columnspan=2, pady=5)

        # Правая панель: таблица и фильтры
        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Фильтры
        filter_frame = ttk.LabelFrame(right_frame, text="Фильтры", padding=5)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, padx=5)
        self.type_filter_combo = ttk.Combobox(filter_frame, values=["All"], state="readonly", width=15)
        self.type_filter_combo.set("All")
        self.type_filter_combo.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=2, padx=5)
        self.date_filter_entry = ttk.Entry(filter_frame, width=12)
        self.date_filter_entry.grid(row=0, column=3, padx=5)

        filter_btn = ttk.Button(filter_frame, text="Применить", command=self.apply_filter)
        filter_btn.grid(row=0, column=4, padx=5)

        reset_btn = ttk.Button(filter_frame, text="Сброс", command=self.reset_filter)
        reset_btn.grid(row=0, column=5, padx=5)

        # Таблица
        columns = ("Дата", "Тип", "Длительность (мин)")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип", text="Тип")
        self.tree.heading("Длительность (мин)", text="Длительность (мин)")
        self.tree.column("Дата", width=100)
        self.tree.column("Тип", width=150)
        self.tree.column("Длительность (мин)", width=120)

        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Первоначальное заполнение фильтра по типам
        self.update_type_filter_combobox()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
