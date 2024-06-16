import tkinter as tk
import customtkinter
from tkcalendar import Calendar
import sqlite3
import datetime
import threading
import tkinter.messagebox
import time
import winsound  # Импортируем модуль winsound для воспроизведения звуков

# Функция для инициализации базы данных
def db_start():
    global conn, cur
    conn = sqlite3.connect('notes.db')  # Подключаемся к базе данных 'notes.db'
    cur = conn.cursor()
    # Создаем таблицу 'notes', если она не существует
    cur.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, content TEXT, created_at TEXT, notified INTEGER)")
    conn.commit()

    # Проверяем, существуют ли необходимые столбцы и добавляем их, если нет
    cur.execute("PRAGMA table_info(notes)")
    columns = [column[1] for column in cur.fetchall()]
    if 'title' not in columns:
        cur.execute("ALTER TABLE notes ADD COLUMN title TEXT")
        conn.commit()
    if 'content' not in columns:
        cur.execute("ALTER TABLE notes ADD COLUMN content TEXT")
        conn.commit()
    if 'created_at' not in columns:
        cur.execute("ALTER TABLE notes ADD COLUMN created_at TEXT")
        conn.commit()
    if 'notified' not in columns:
        cur.execute("ALTER TABLE notes ADD COLUMN notified INTEGER DEFAULT 0")
        conn.commit()

# Функция для инициализации столбца created_at, если он пуст
def initialize_created_at():
    cur.execute("SELECT id, created_at FROM notes")
    notes = cur.fetchall()
    for note in notes:
        note_id, created_at = note
        if created_at is None:
            cur.execute("UPDATE notes SET created_at = ? WHERE id = ?",
                        (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), note_id))
    conn.commit()

# Функция для сохранения новой заметки
def save_note():
    note_text = note_entry.get("1.0", tk.END).strip()  # Получаем текст из текстового поля
    if not note_text:  # Проверяем, если текст заметки пустой, не сохраняем заметку
        return
    note_lines = note_text.split("\n")
    if not note_lines:
        return
    title = note_lines[0].upper()  # Заголовок - первая строка, преобразованная в верхний регистр
    content = "\n".join(note_lines[1:])  # Содержание - все остальные строки
    created_at = calendar.get_date() + " " + datetime.datetime.now().strftime("%H:%M:%S")  # Время создания заметки
    cur.execute("INSERT INTO notes (title, content, created_at, notified) VALUES (?, ?, ?, ?)", (title, content, created_at, 0))
    conn.commit()
    update_notes_list()
    note_entry.delete("1.0", tk.END)  # Очищаем текстовое поле

# Функция для капитализации первой буквы первой строки
def capitalize_first_letter(event):
    first_line = note_entry.get("1.0", "1.end")
    if first_line and first_line[0].islower():
        note_entry.delete("1.0")
        note_entry.insert("1.0", first_line.capitalize())

# Функция для удаления заметки из режима редактирования
def delete_note_from_edit(note_id, edit_window):
    cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    update_notes_list()
    edit_window.destroy()

# Функция для удаления выбранной заметки
def delete_selected_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        if not selected_note[0].isdigit():  # Проверяем, что это не дата
            cur.execute("SELECT id FROM notes WHERE title=?", (selected_note.strip(),))
            note = cur.fetchone()
            if note:
                note_id = note[0]
                cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
                conn.commit()
                update_notes_list()

# Функция для редактирования заметки
def edit_note():
    index = notes_list.curselection()  # Получаем выбранную заметку
    if index:
        selected_note = notes_list.get(index)
        if selected_note[0].isdigit():  # Проверяем, что это не дата
            return
        cur.execute("SELECT * FROM notes WHERE title=?", (selected_note.strip(),))
        note = cur.fetchone()
        if note:
            edit_window = customtkinter.CTkToplevel(root)
            edit_window.title("Просмотреть заметку")
            edit_window.geometry("400x600")
            edit_window.configure(bg='#757272')

            edit_window.grab_set()
            edit_window.lift()
            edit_window.attributes('-topmost', True)
            edit_window.after(1, lambda: edit_window.attributes('-topmost', False))

            top_frame = tk.Frame(edit_window, bg="burlywood")
            top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

            title_label = customtkinter.CTkLabel(top_frame, text="Измените заголовок заметки:",
                                                 font=("Roboto", 12), text_color="#555657")
            title_label.pack(pady=5)

            edited_title = customtkinter.CTkEntry(top_frame, width=300, fg_color="burlywood", text_color="#555657")
            edited_title.insert(0, note[1])
            edited_title.pack(pady=5)

            date_label = customtkinter.CTkLabel(top_frame, text="Измените дату и время создания заметки:",
                                                font=("Roboto", 12), text_color="#555657")
            date_label.pack(pady=5)

            edit_calendar = Calendar(top_frame, selectmode='day', date_pattern='yyyy-MM-dd')
            edit_calendar.pack(pady=5)

            edit_calendar.selection_set(note[3].split(" ")[0])

            bottom_frame = tk.Frame(edit_window, bg="burlywood")
            bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

            edit_content_label = customtkinter.CTkLabel(bottom_frame, text="Измените содержимое заметки:",
                                                        font=("Roboto", 12), text_color="#555657")
            edit_content_label.pack(pady=5)

            edit_content_entry = tk.Text(bottom_frame, height=10, bg="burlywood", font=("Roboto", 14))
            edit_content_entry.insert(tk.END, note[2])
            edit_content_entry.pack(fill=tk.BOTH, expand=True)

            save_button = customtkinter.CTkButton(bottom_frame, text="Сохранить",
                                                  command=lambda: save_edited_note(edit_window, note[0],
                                                                                   edited_title.get(),
                                                                                   edit_content_entry.get("1.0",
                                                                                                          tk.END).strip(),
                                                                                   edit_calendar.get_date()),
                                                  fg_color="burlywood", text_color="#555657")
            save_button.pack(pady=5)

            delete_button = customtkinter.CTkButton(bottom_frame, text="Удалить",
                                                    command=lambda: delete_note_from_edit(note[0], edit_window),
                                                    fg_color="burlywood", text_color="#555657")
            delete_button.pack(pady=5)

            edit_window.protocol("WM_DELETE_WINDOW", lambda: edit_window.grab_release() or edit_window.destroy())

# Функция для сохранения изменений заметки
def save_edited_note(edit_window, note_id, new_title, new_content, new_date):
    new_datetime = new_date + " " + datetime.datetime.now().strftime("%H:%M:%S")
    cur.execute("UPDATE notes SET title=?, content=?, created_at=?, notified=? WHERE id=?", (new_title, new_content, new_datetime, 0, note_id))
    conn.commit()
    update_notes_list()
    edit_window.grab_release()
    edit_window.destroy()

# Функция для обновления списка заметок
def update_notes_list():
    notes_list.delete(0, tk.END)
    cur.execute("SELECT title, created_at FROM notes ORDER BY created_at DESC")
    notes = cur.fetchall()

    current_date = None
    for note in notes:
        title, created_at = note
        if created_at is None:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        note_date = created_at.split(" ")[0]

        if note_date != current_date:
            notes_list.insert(tk.END, note_date)
            notes_list.itemconfig(tk.END, {'bg': '#cccccc'})
            current_date = note_date

        notes_list.insert(tk.END, "  " + title)

# Функция для очистки всех заметок
def clear_notes():
    cur.execute("DELETE FROM notes")
    conn.commit()
    update_notes_list()

# Функция для обработки двойного щелчка на заметке
def on_note_double_click(event):
    edit_note()

# Функция для добавления заметки при нажатии на Tab
def add_note_with_tab(event):
    if event.keysym == "Tab":
        save_note()

# Функция для обработки нажатия клавиши Delete для удаления заметки
def on_delete_key(event):
    delete_selected_note()

# Функция для проверки и отображения уведомлений
def notify():
    conn = sqlite3.connect('notes.db')
    cur = conn.cursor()
    while True:
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT id, title, created_at FROM notes WHERE created_at LIKE ? AND notified = 0", (now + "%",))
        notes = cur.fetchall()
        if notes:
            message = "Заметки на сегодня:\n\n"
            for note in notes:
                message += f"- {note[1]}\n"
            # Воспроизводим звуковой сигнал
            winsound.Beep(1000, 500)  # Звук частотой 1000 Гц и длительностью 500 мс
            if tkinter.messagebox.askyesno("Уведомление", message + "\nВы хотите отложить уведомление?"):
                time.sleep(30)  # Отложить на 30 сек
            else:
                cur.execute("UPDATE notes SET notified = 1 WHERE id IN ({})".format(",".join([str(note[0]) for note in notes])))
                conn.commit()
        time.sleep(10)  # Проверка каждые 10 секунд

# Инициализация главного окна
root = customtkinter.CTk()
root.title("Приложение для заметок")
root.geometry("800x800")
root.resizable(0, 0)

# Метка для заметок
note_label = customtkinter.CTkLabel(root, text="Заметка:")
note_label.pack(pady=5)

# Поле для ввода заметок
note_entry = tk.Text(root, height=5, width=50, bg="burlywood", font=("Robotto", 16))
note_entry.pack(pady=5)
note_entry.bind("<Tab>", add_note_with_tab)

# Выбор даты для новой заметки
calendar = Calendar(root, selectmode='day', date_pattern='yyyy-MM-dd')
calendar.pack(pady=5)

# Список для отображения заметок
notes_list = tk.Listbox(root, width=50, height=10, bg="burlywood", font=("Robotto", 16))
notes_list.pack(pady=5)
notes_list.bind("<Double-Button-1>", on_note_double_click)
notes_list.bind("<Delete>", on_delete_key) # Привязываем удаление заметки к клавише Delete

# Полоса прокрутки для списка заметок
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
scrollbar.config(command=notes_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

notes_list.config(yscrollcommand=scrollbar.set)

# Кнопка для очистки всех заметок
clear_button = customtkinter.CTkButton(root, text="Очистить список", command=clear_notes)
clear_button.pack(pady=5)

# Инициализация базы данных и данных
db_start()
initialize_created_at()
update_notes_list()

# Привязка событий к текстовому полю
note_entry.bind("<KeyRelease>", capitalize_first_letter)

# Запуск функции уведомлений в отдельном потоке
notification_thread = threading.Thread(target=notify, daemon=True)
notification_thread.start()

# Запуск главного цикла приложения
root.mainloop()
conn.close() # Закрываем соединение с базой данных после закрытия приложения
