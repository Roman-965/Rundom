import random
import json
import os
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator - Генератор случайных задач")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Предопределённые задачи с типами
        self.tasks_db = {
            "Учёба": [
                "Прочитать статью по Python",
                "Решить 5 математических задач",
                "Выучить 10 новых английских слов",
                "Посмотреть лекцию по истории",
                "Написать конспект по физике",
                "Подготовиться к экзамену",
                "Сделать домашнее задание",
                "Изучить новую тему по программированию"
            ],
            "Спорт": [
                "Сделать зарядку (15 мин)",
                "Пробежка 3 км",
                "Отжаться 20 раз",
                "Планка 2 минуты",
                "Растяжка 10 минут",
                "Пойти в спортзал",
                "Покататься на велосипеде",
                "Йога 20 минут"
            ],
            "Работа": [
                "Сделать отчёт по проекту",
                "Ответить на важные письма",
                "Провести код-ревью",
                "Написать документацию",
                "Спланировать задачи на неделю",
                "Провести встречу с командой",
                "Разобрать рабочие задачи",
                "Изучить новую технологию"
            ]
        }

        # Файл для хранения истории
        self.history_file = "task_history.json"
        self.history = self.load_history()

        # Переменные для фильтрации
        self.filter_type = StringVar(value="Все")

        self.create_widgets()
        self.update_history_display()

    def create_widgets(self):
        # Рамка для генерации
        gen_frame = LabelFrame(self.root, text="🎲 Генератор задач", padx=15, pady=10, 
                                font=("Arial", 12, "bold"))
        gen_frame.pack(fill="x", padx=10, pady=5)

        self.generate_btn = Button(gen_frame, text="✨ Сгенерировать задачу", 
                                   command=self.generate_task, 
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                   padx=20, pady=10)
        self.generate_btn.pack(pady=10)

        self.current_task_label = Label(gen_frame, text="Нажмите кнопку, чтобы получить задачу", 
                                        font=("Arial", 11), fg="#2196F3", wraplength=700)
        self.current_task_label.pack(pady=5)

        # Рамка для фильтрации
        filter_frame = LabelFrame(self.root, text="🔍 Фильтр по типу", padx=15, pady=10, 
                                   font=("Arial", 12, "bold"))
        filter_frame.pack(fill="x", padx=10, pady=5)

        types = ["Все"] + list(self.tasks_db.keys())
        for i, t in enumerate(types):
            Radiobutton(filter_frame, text=t, variable=self.filter_type, 
                        value=t, command=self.update_history_display,
                        font=("Arial", 10)).pack(side="left", padx=15, pady=5)

        # Рамка для истории
        history_frame = LabelFrame(self.root, text="📜 История задач", padx=10, pady=10, 
                                    font=("Arial", 12, "bold"))
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Список с прокруткой
        scrollbar = Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = Listbox(history_frame, yscrollcommand=scrollbar.set, 
                                        font=("Courier", 10), height=15)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Кнопки управления
        control_frame = Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        Button(control_frame, text="🗑 Очистить историю", command=self.clear_history,
               bg="#f44336", fg="white", font=("Arial", 9, "bold"), padx=10).pack(side="left", padx=5)
        
        Button(control_frame, text="➕ Добавить свою задачу", command=self.add_custom_task,
               bg="#4CAF50", fg="white", font=("Arial", 9, "bold"), padx=10).pack(side="left", padx=5)
        
        Button(control_frame, text="💾 Сохранить историю", command=self.save_history_manual,
               bg="#2196F3", fg="white", font=("Arial", 9, "bold"), padx=10).pack(side="left", padx=5)
        
        Button(control_frame, text="📊 Статистика", command=self.show_statistics,
               bg="#FF9800", fg="white", font=("Arial", 9, "bold"), padx=10).pack(side="left", padx=5)

        # Статусная строка
        self.status_label = Label(self.root, text="✅ Готово", bd=1, relief=SUNKEN, anchor=W, 
                                   font=("Arial", 9), bg="#f0f0f0")
        self.status_label.pack(side="bottom", fill="x")

        # Информационная строка
        self.info_label = Label(self.root, text="", font=("Arial", 9), fg="#666")
        self.info_label.pack(side="bottom", fill="x")

    def generate_task(self):
        """Генерация случайной задачи"""
        filter_value = self.filter_type.get()
        
        if filter_value == "Все":
            # Собираем все задачи из всех категорий
            all_tasks = []
            for task_type, tasks in self.tasks_db.items():
                for task in tasks:
                    all_tasks.append((task, task_type))
            if not all_tasks:
                messagebox.showwarning("Нет задач", "Добавьте хотя бы одну задачу!")
                return
            selected_task, task_type = random.choice(all_tasks)
        else:
            # Выбираем из конкретной категории
            if filter_value not in self.tasks_db or not self.tasks_db[filter_value]:
                messagebox.showwarning("Нет задач", f"В категории '{filter_value}' нет задач!")
                return
            selected_task = random.choice(self.tasks_db[filter_value])
            task_type = filter_value

        # Добавляем в историю
        history_entry = {
            "id": self.get_next_id(),
            "datetime": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "task": selected_task,
            "type": task_type
        }
        
        self.history.append(history_entry)
        self.save_history()
        self.update_history_display()
        self.current_task_label.config(text=f"🎯 {selected_task}  [{task_type}]")
        self.status_label.config(text=f"✅ Сгенерирована задача: {selected_task}")

    def update_history_display(self):
        """Обновление отображения истории с учётом фильтра"""
        self.history_listbox.delete(0, END)
        
        filtered = self.filter_history()
        
        if not filtered:
            self.history_listbox.insert(END, "  📭 История пуста")
            self.info_label.config(text="Всего задач в истории: 0")
            return
        
        # Отображаем в обратном порядке (новые сверху)
        for i, entry in enumerate(reversed(filtered), 1):
            display_text = f"{i:3d}. [{entry['type']:6s}] {entry['task']}  ({entry['datetime']})"
            self.history_listbox.insert(END, display_text)
        
        total = len(self.history)
        shown = len(filtered)
        self.info_label.config(text=f"Всего задач в истории: {total} | Показано: {shown}")

    def filter_history(self):
        """Фильтрация истории по выбранному типу"""
        if self.filter_type.get() == "Все":
            return self.history
        else:
            return [item for item in self.history if item["type"] == self.filter_type.get()]

    def add_custom_task(self):
        """Диалог добавления новой задачи"""
        dialog = Toplevel(self.root)
        dialog.title("Добавить новую задачу")
        dialog.geometry("450x280")
        dialog.resizable(False, False)
        dialog.grab_set()

        Label(dialog, text="Название задачи:", font=("Arial", 10, "bold")).pack(pady=10)
        task_entry = Entry(dialog, width=50, font=("Arial", 10))
        task_entry.pack(pady=5)

        Label(dialog, text="Тип задачи:", font=("Arial", 10, "bold")).pack(pady=10)
        type_var = StringVar()
        type_combo = ttk.Combobox(dialog, textvariable=type_var, 
                                   values=list(self.tasks_db.keys()), 
                                   width=30, font=("Arial", 10))
        type_combo.pack(pady=5)

        def save_task():
            task_text = task_entry.get().strip()
            task_type = type_var.get().strip()

            # Проверка на пустую строку
            if not task_text:
                messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
                return
            if not task_type:
                messagebox.showerror("Ошибка", "Выберите тип задачи!")
                return
            if task_type not in self.tasks_db:
                messagebox.showerror("Ошибка", "Некорректный тип задачи!")
                return

            # Добавляем задачу
            self.tasks_db[task_type].append(task_text)
            dialog.destroy()
            self.status_label.config(text=f"➕ Добавлена задача: {task_text} [{task_type}]")
            messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена в категорию '{task_type}'")

        Button(dialog, text="💾 Сохранить", command=save_task, 
               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), 
               padx=20, pady=5).pack(pady=20)

    def clear_history(self):
        """Очистка истории после подтверждения"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю задач?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            self.status_label.config(text="🗑 История очищена")
            self.current_task_label.config(text="Нажмите кнопку, чтобы получить задачу")

    def show_statistics(self):
        """Показывает статистику по истории задач"""
        if not self.history:
            messagebox.showinfo("Статистика", "История задач пуста. Сгенерируйте несколько задач.")
            return
        
        total = len(self.history)
        
        # Статистика по типам
        type_stats = {}
        for entry in self.history:
            task_type = entry['type']
            type_stats[task_type] = type_stats.get(task_type, 0) + 1
        
        # Статистика по дням
        day_stats = {}
        for entry in self.history:
            day = entry['datetime'][:10]  # Берём только дату
            day_stats[day] = day_stats.get(day, 0) + 1
        
        most_common_type = max(type_stats.items(), key=lambda x: x[1]) if type_stats else ("Нет", 0)
        most_productive_day = max(day_stats.items(), key=lambda x: x[1]) if day_stats else ("Нет", 0)
        
        stats_text = f"""📊 СТАТИСТИКА ГЕНЕРАЦИИ ЗАДАЧ

📌 Всего сгенерировано: {total}

🏷️ Распределение по типам:"""
        
        for task_type, count in type_stats.items():
            percentage = (count / total) * 100
            stats_text += f"\n   • {task_type}: {count} ({percentage:.1f}%)"
        
        stats_text += f"\n\n⭐ Чаще всего генерируемый тип: {most_common_type[0]} ({most_common_type[1]} раз)"
        stats_text += f"\n📅 Самый продуктивный день: {most_productive_day[0]} ({most_productive_day[1]} задач)"
        
        # Последние 5 задач
        stats_text += "\n\n🆕 Последние 5 сгенерированных задач:"
        for entry in self.history[-5:]:
            stats_text += f"\n   • [{entry['type']}] {entry['task'][:40]}"
        
        messagebox.showinfo("📊 Статистика", stats_text)

    def save_history(self):
        """Автоматическое сохранение истории в JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def save_history_manual(self):
        """Ручное сохранение истории"""
        self.save_history()
        messagebox.showinfo("Успех", "История сохранена в файл task_history.json")
        self.status_label.config(text="💾 История сохранена")

    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def get_next_id(self):
        """Получение следующего ID"""
        if not self.history:
            return 1
        return max(entry['id'] for entry in self.history) + 1

if __name__ == "__main__":
    root = Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()