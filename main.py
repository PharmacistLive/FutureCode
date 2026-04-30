import random
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Файл для сохранения истории
        self.history_file = "task_history.json"
        
        # Предопределённые задачи по категориям
        self.default_tasks = {
            "учёба": [
                "Прочитать статью",
                "Выучить 10 новых слов",
                "Решить 5 математических задач",
                "Просмотреть лекцию",
                "Сделать конспект",
                "Подготовиться к экзамену",
                "Выполнить домашнее задание"
            ],
            "спорт": [
                "Сделать зарядку",
                "Пробежать 2 км",
                "Сделать растяжку",
                "Потренироваться 30 минут",
                "Сходить в спортзал",
                "Сделать 50 отжиманий",
                "Поплавать в бассейне"
            ],
            "работа": [
                "Ответить на письма",
                "Составить отчёт",
                "Провести встречу",
                "Спланировать задачи на день",
                "Завершить проект",
                "Позвонить клиенту",
                "Сделать презентацию"
            ]
        }
        
        # Загружаем историю или создаём новую
        self.history = self.load_history()
        
        # Переменные для фильтрации
        self.current_filter = tk.StringVar(value="все")
        self.new_task_text = tk.StringVar()
        self.new_task_category = tk.StringVar(value="учёба")
        
        self.setup_ui()
        self.update_task_list()
        
    def setup_ui(self):
        # Стиль
        style = ttk.Style()
        style.theme_use('clam')
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка веса для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🎲 Random Task Generator", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=10)
        
        # Фрейм для генерации задачи
        generate_frame = ttk.LabelFrame(main_frame, text="Генератор задач", padding="10")
        generate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.generate_btn = ttk.Button(generate_frame, text="🎯 Сгенерировать задачу", 
                                       command=self.generate_task, width=30)
        self.generate_btn.grid(row=0, column=0, padx=5)
        
        self.current_task_label = ttk.Label(generate_frame, text="Нажмите кнопку для генерации", 
                                            font=('Arial', 11), foreground='blue')
        self.current_task_label.grid(row=0, column=1, padx=10, sticky=(tk.W))
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(main_frame, text="Фильтрация", padding="10")
        filter_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(filter_frame, text="Все задачи", variable=self.current_filter, 
                       value="все", command=self.update_task_list).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(filter_frame, text="Учёба", variable=self.current_filter, 
                       value="учёба", command=self.update_task_list).grid(row=0, column=1, padx=10)
        ttk.Radiobutton(filter_frame, text="Спорт", variable=self.current_filter, 
                       value="спорт", command=self.update_task_list).grid(row=0, column=2, padx=10)
        ttk.Radiobutton(filter_frame, text="Работа", variable=self.current_filter, 
                       value="работа", command=self.update_task_list).grid(row=0, column=3, padx=10)
        
        # Фрейм для добавления новых задач
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(add_frame, text="Задача:").grid(row=0, column=0, padx=5)
        task_entry = ttk.Entry(add_frame, textvariable=self.new_task_text, width=40)
        task_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5)
        category_combo = ttk.Combobox(add_frame, textvariable=self.new_task_category, 
                                      values=["учёба", "спорт", "работа"], width=15)
        category_combo.grid(row=0, column=3, padx=5)
        
        ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_new_task).grid(row=0, column=4, padx=10)
        
        # Фрейм для отображения истории
        history_frame = ttk.LabelFrame(main_frame, text="История задач", padding="10")
        history_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Создаём Treeview для отображения истории
        columns = ("#", "Задача", "Категория", "Время")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        # Настройка колонок
        self.tree.heading("#", text="№")
        self.tree.heading("Задача", text="Задача")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Время", text="Время генерации")
        
        self.tree.column("#", width=50, anchor='center')
        self.tree.column("Задача", width=250)
        self.tree.column("Категория", width=100, anchor='center')
        self.tree.column("Время", width=200)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(history_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Кнопки управления историей
        control_frame = ttk.Frame(history_frame)
        control_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(control_frame, text="🗑️ Очистить историю", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 Сохранить историю", 
                  command=self.save_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📂 Загрузить историю", 
                  command=self.load_history_from_file).pack(side=tk.LEFT, padx=5)
        
        # Информационная метка
        self.info_label = ttk.Label(main_frame, text="✅ Готов к работе", font=('Arial', 9), foreground='green')
        self.info_label.grid(row=5, column=0, pady=5)
        
    def generate_task(self):
        """Генерирует случайную задачу"""
        # Объединяем все категории или используем конкретную
        if self.current_filter.get() == "все":
            # Выбираем случайную категорию и задачу
            category = random.choice(list(self.default_tasks.keys()))
            task = random.choice(self.default_tasks[category])
            category_name = category
        else:
            category = self.current_filter.get()
            category_name = category
            if category not in self.default_tasks:
                messagebox.showerror("Ошибка", "Категория не найдена")
                return
            task = random.choice(self.default_tasks[category])
        
        # Добавляем в историю
        history_entry = {
            "task": task,
            "category": category_name,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().timestamp()
        }
        self.history.append(history_entry)
        
        # Обновляем отображение
        self.current_task_label.config(text=f"✨ Текущая задача: {task} ✨", foreground='green')
        self.update_task_list()
        self.save_history()
        
        # Анимация кнопки
        self.generate_btn.config(text="✅ Сгенерировано!", state='disabled')
        self.root.after(1500, lambda: self.generate_btn.config(text="🎯 Сгенерировать задачу", state='normal'))
        
    def add_new_task(self):
        """Добавляет новую задачу в список"""
        task = self.new_task_text.get().strip()
        category = self.new_task_category.get()
        
        # Проверка на пустую строку
        if not task:
            messagebox.showwarning("Предупреждение", "Задача не может быть пустой!")
            return
        
        # Проверка на существование категории
        if category not in self.default_tasks:
            messagebox.showerror("Ошибка", "Неверная категория!")
            return
        
        # Добавляем задачу в соответствующий список
        self.default_tasks[category].append(task)
        
        # Очищаем поле ввода
        self.new_task_text.set("")
        
        # Обновляем отображение
        self.update_task_list()
        self.save_history()
        
        messagebox.showinfo("Успех", f"Задача '{task}' добавлена в категорию '{category}'")
        self.info_label.config(text=f"✅ Добавлена задача: {task}", foreground='green')
        self.root.after(3000, lambda: self.info_label.config(text="✅ Готов к работе", foreground='green'))
        
    def update_task_list(self):
        """Обновляет отображение списка задач с учётом фильтра"""
        # Очищаем дерево
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтруем историю
        current_filter = self.current_filter.get()
        if current_filter == "все":
            filtered_history = self.history
        else:
            filtered_history = [item for item in self.history if item["category"] == current_filter]
        
        # Отображаем отфильтрованную историю
        for i, entry in enumerate(reversed(filtered_history), 1):
            self.tree.insert("", "end", values=(i, entry["task"], entry["category"], entry["time"]))
        
        self.info_label.config(text=f"📊 Показано задач: {len(filtered_history)} из {len(self.history)}")
        
    def clear_history(self):
        """Очищает всю историю"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_task_list()
            self.save_history()
            self.info_label.config(text="🗑️ История очищена", foreground='orange')
            self.root.after(3000, lambda: self.info_label.config(text="✅ Готов к работе", foreground='green'))
        
    def save_history(self):
        """Сохраняет историю в JSON файл"""
        try:
            data = {
                "history": self.history,
                "tasks": self.default_tasks
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.info_label.config(text="💾 История сохранена", foreground='blue')
            self.root.after(2000, lambda: self.info_label.config(text="✅ Готов к работе", foreground='green'))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
            
    def load_history(self):
        """Загружает историю из JSON файла при запуске"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Загружаем историю и пользовательские задачи
                    history = data.get("history", [])
                    user_tasks = data.get("tasks", {})
                    
                    # Объединяем пользовательские задачи с предопределёнными
                    for category in user_tasks:
                        if category in self.default_tasks:
                            self.default_tasks[category].extend(user_tasks[category])
                        else:
                            self.default_tasks[category] = user_tasks[category]
                    
                    return history
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
                return []
        return []
    
    def load_history_from_file(self):
        """Загружает историю из файла вручную"""
        if messagebox.askyesno("Подтверждение", "Загрузка истории заменит текущие данные. Продолжить?"):
            if os.path.exists(self.history_file):
                try:
                    with open(self.history_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.history = data.get("history", [])
                        user_tasks = data.get("tasks", {})
                        
                        # Обновляем задачи
                        for category in user_tasks:
                            if category in self.default_tasks:
                                # Объединяем без дубликатов (просто добавляем)
                                existing = set(self.default_tasks[category])
                                new_tasks = [t for t in user_tasks[category] if t not in existing]
                                self.default_tasks[category].extend(new_tasks)
                            else:
                                self.default_tasks[category] = user_tasks[category]
                        
                        self.update_task_list()
                        messagebox.showinfo("Успех", "История успешно загружена!")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
            else:
                messagebox.showwarning("Предупреждение", "Файл с историей не найден!")

def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()