import tkinter as tk
import customtkinter
import sqlite3

def db_start():
    global conn, cur
    conn = sqlite3.connect('notes.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, content TEXT)""")
    conn.commit()

    cur.execute("PRAGMA table_info(notes)")
    columns = [column[1] for column in cur.fetchall()]
    if 'title' not in columns:
        cur.execute("ALTER TABLE notes ADD COLUMN title TEXT")
        conn.commit()
    if 'content' not in columns:
        cur.execute("ALTER TABLE notes ADD COLUMN content TEXT")
        conn.commit()

def save_note():
    # Получаем текст из поля ввода
    note_text = note_entry.get("1.0", tk.END).strip()
    # Разделяем текст на строки
    note_lines = note_text.split("\n")
    # Первая строка - заголовок, остальные - содержимое
    title = note_lines[0].upper()
    content = "\n".join(note_lines[1:])
    # Вставляем данные в базу данных
    cur.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    update_notes_list()
    # Очищаем поле ввода
    note_entry.delete("1.0", tk.END)

def capitalize_first_letter(event):
    # Получаем содержимое первой строки
    first_line = note_entry.get("1.0", "1.end")
    # Проверяем, является ли первый символ буквой нижнего регистра
    if first_line and first_line[0].islower():
        # Преобразуем его в верхний регистр
        note_entry.delete("1.0")
        note_entry.insert("1.0", first_line.capitalize())

def delete_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        cur.execute("DELETE FROM notes WHERE title=?", (selected_note,))
        conn.commit()
        update_notes_list()

def edit_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        # Поиск заметки в базе данных по заголовку
        cur.execute("SELECT * FROM notes WHERE title=?", (selected_note,))
        note = cur.fetchone()
        if note:
            # Отображение заметки в диалоговом окне для редактирования
            edit_window = tk.Toplevel(root)
            edit_window.title("Редактировать заметку")
            edit_window.geometry("400x400")  # Увеличиваем размеры основного окна

            # Фрейм для редактирования заголовка
            top_frame = tk.Frame(edit_window, bg="burlywood")
            top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

            edit_title_label = customtkinter.CTkLabel(top_frame, text="Измените заголовок заметки:", font=("Roboto", 12))
            edit_title_label.pack(pady=5)

            edited_title = tk.StringVar(value=note[1])  # Заголовок заметки
            edit_title_entry = customtkinter.CTkEntry(top_frame, textvariable=edited_title)
            edit_title_entry.pack(pady=5)

            # Фрейм для редактирования содержимого заметки
            bottom_frame = tk.Frame(edit_window, bg="burlywood")
            bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

            edit_content_label = customtkinter.CTkLabel(bottom_frame, text="Измените содержимое заметки:", font=("Roboto", 12))
            edit_content_label.pack(pady=5)

            edit_content_entry = tk.Text(bottom_frame, height=10, bg="burlywood", font=("Roboto", 14))  # Увеличиваем шрифт
            edit_content_entry.insert(tk.END, note[2])  # Вставляем содержание заметки
            edit_content_entry.pack(fill=tk.BOTH, expand=True)

            save_button = customtkinter.CTkButton(bottom_frame, text="Сохранить", command=lambda: save_edited_note(edit_window, note[0], edited_title.get(), edit_content_entry.get("1.0", tk.END).strip()))
            save_button.pack(pady=5)



def view_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        # Получаем содержание выбранной заметки из базы данных
        cur.execute("SELECT content FROM notes WHERE title=?", (selected_note,))
        content = cur.fetchone()[0]
        # Открываем новое окно для просмотра заметки
        view_window = tk.Toplevel(root)
        view_window.title(selected_note)  # Заголовок окна будет названием заметки
        view_window.geometry("400x400")
        view_window.resizable(False, False)

        # Создаем текстовое поле для отображения содержимого заметки
        content_text = tk.Text(view_window, wrap="word", font=("Roboto", 14), bg="burlywood", padx=10, pady=10)
        content_text.insert(tk.END, content)  # Вставляем содержимое заметки
        content_text.pack(expand=True, fill=tk.BOTH)

def save_edited_note(edit_window, note_id, new_title, new_content):
    # Обновляем данные заметки в базе данных
    cur.execute("UPDATE notes SET title=?, content=? WHERE id=?", (new_title, new_content, note_id))
    conn.commit()
    update_notes_list()
    edit_window.destroy()

def update_notes_list():
    notes_list.delete(0, tk.END)
    cur.execute("SELECT title FROM notes")
    notes = cur.fetchall()
    for note in notes:
        # Добавляем в список названия заметок
        notes_list.insert(tk.END, note[0])

def clear_notes():
    cur.execute("DELETE FROM notes")
    conn.commit()
    update_notes_list()

root = customtkinter.CTk()
root.title("Приложение для заметок")
root.geometry("800x800")  # Увеличиваем размер окна в 2 раза
root.resizable(0, 0)

note_label = customtkinter.CTkLabel(root, text="Заметка:")
note_label.pack(pady=5)

# Изменяем внешний вид поля ввода
note_entry = tk.Text(root, height=5, width=50, bg="burlywood", font=("Robotto", 16))
note_entry.pack(pady=5)

save_button = customtkinter.CTkButton(root, text="Добавить заметку", command=save_note)
save_button.pack(pady=5)

view_button = customtkinter.CTkButton(root, text="Просмотреть заметку", command=view_note)
view_button.pack(pady=5)

edit_button = customtkinter.CTkButton(root, text="Редактировать заметку", command=edit_note)
edit_button.pack(pady=5)

delete_button = customtkinter.CTkButton(root, text="Удалить заметку", command=delete_note)
delete_button.pack(pady=5)

clear_button = customtkinter.CTkButton(root, text="Очистить список", command=clear_notes)
clear_button.pack(pady=5)

notes_list = tk.Listbox(root, width=50, height=10, bg="burlywood", font=("Robotto", 16))
notes_list.pack(pady=5)

scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
scrollbar.config(command=notes_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

notes_list.config(yscrollcommand=scrollbar.set)

db_start()
update_notes_list()
note_entry.bind("<KeyRelease>", capitalize_first_letter)

root.mainloop()
conn.close()