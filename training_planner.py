import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.trainings = []
        self.load_data()

        # Создаём виджеты
        self.create_widgets()

    def create_widgets(self):
        # Поля ввода
        tk.Label(self.root, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Тип тренировки:").grid(row=1, column=0, padx=5, pady=5)
        self.type_entry = ttk.Combobox(self.root, values=["Бег", "Плавание", "Велоспорт", "Силовая", "Йога"])
        self.type_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Длительность (мин):").grid(row=2, column=0, padx=5, pady=5)
        self.duration_entry = tk.Entry(self.root)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка добавления
        tk.Button(self.root, text="Добавить тренировку", command=self.add_training).grid(row=3, column=0, columnspan=2, pady=10)

        # Таблица
        self.tree = ttk.Treeview(self.root, columns=("Date", "Type", "Duration"), show="headings")
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Type", text="Тип")
        self.tree.heading("Duration", text="Длительность (мин)")
        self.tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Фильтры
        tk.Label(self.root, text="Фильтр по типу:").grid(row=5, column=0, padx=5, pady=5)
        self.filter_type = ttk.Combobox(self.root, values=["Все", "Бег", "Плавание", "Велоспорт", "Силовая", "Йога"])
        self.filter_type.set("Все")
        self.filter_type.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(self.root, text="Фильтр по дате (ДД.ММ.ГГГГ):").grid(row=6, column=0, padx=5, pady=5)
        self.filter_date = tk.Entry(self.root)
        self.filter_date.grid(row=6, column=1, padx=5, pady=5)

        tk.Button(self.root, text="Применить фильтры", command=self.apply_filters).grid(row=7, column=0, columnspan=2, pady=10)
