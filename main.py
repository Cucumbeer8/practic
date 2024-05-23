import tkinter as tk
import customtkinter
import sqlite3

def db_start():
    global conn, cur
    conn = sqlite3.connect('notes.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, content TEXT)")
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
    note_text = note_entry.get("1.0", tk.END).strip()
    note_lines = note_text.split("\n")
    title = note_lines[0].upper()
    content = "\n".join(note_lines[1:])
    cur.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    update_notes_list()
    note_entry.delete("1.0", tk.END)

def capitalize_first_letter(event):
    first_line = note_entry.get("1.0", "1.end")
    if first_line and first_line[0].islower():
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
        cur.execute("SELECT * FROM notes WHERE title=?", (selected_note,))
        note = cur.fetchone()
        if note:
            edit_window = customtkinter.CTkToplevel(root)
            edit_window.title("Просмотреть заметку")
            edit_window.geometry("400x600")
            edit_window.configure(bg='#757272')
            edit_window.focus_force()

            top_frame = tk.Frame(edit_window, bg="burlywood")
            top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

            edit_title_label = customtkinter.CTkLabel(top_frame, text="Измените заголовок заметки:", font=("Roboto", 12), text_color="#555657")
            edit_title_label.pack(pady=5)

            edited_title = tk.StringVar(value=note[1])
            edit_title_entry = customtkinter.CTkEntry(top_frame, textvariable=edited_title)
            edit_title_entry.pack(pady=5)

            bottom_frame = tk.Frame(edit_window, bg="burlywood")
            bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

            edit_content_label = customtkinter.CTkLabel(bottom_frame, text="Измените содержимое заметки:", font=("Roboto", 12), text_color="#555657")
            edit_content_label.pack(pady=5)

            edit_content_entry = tk.Text(bottom_frame, height=10, bg="burlywood", font=("Roboto", 14))
            edit_content_entry.insert(tk.END, note[2])
            edit_content_entry.pack(fill=tk.BOTH, expand=True)

            save_button = customtkinter.CTkButton(bottom_frame, text="Сохранить",
                                                  command=lambda: save_edited_note(edit_window, note[0], edited_title.get(), edit_content_entry.get("1.0", tk.END).strip()),
                                                  fg_color="burlywood", text_color="#555657")
            save_button.pack(pady=5)

def save_edited_note(edit_window, note_id, new_title, new_content):
    cur.execute("UPDATE notes SET title=?, content=? WHERE id=?", (new_title, new_content, note_id))
    conn.commit()
    update_notes_list()
    edit_window.destroy()

def update_notes_list():
    notes_list.delete(0, tk.END)
    cur.execute("SELECT title FROM notes")
    notes = cur.fetchall()
    for note in notes:
        notes_list.insert(tk.END, note[0])

def clear_notes():
    cur.execute("DELETE FROM notes")
    conn.commit()
    update_notes_list()

root = customtkinter.CTk()
root.title("Приложение для заметок")
root.geometry("800x800")
root.resizable(0, 0)

note_label = customtkinter.CTkLabel(root, text="Заметка:")
note_label.pack(pady=5)

note_entry = tk.Text(root, height=5, width=50, bg="burlywood", font=("Robotto", 16))
note_entry.pack(pady=5)

save_button = customtkinter.CTkButton(root, text="Добавить заметку", command=save_note)
save_button.pack(pady=5)

edit_button = customtkinter.CTkButton(root, text="Просмотреть заметку", command=edit_note)
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