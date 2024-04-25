import tkinter as tk
import customtkinter
import sqlite3

def db_start():
    global conn, cur
    conn = sqlite3.connect('notes.db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, note TEXT)""")

def save_note():
    note = note_entry.get()
    cur.execute("INSERT INTO notes (note) VALUES (?)", (note,))
    conn.commit()
    update_notes_list()
    note_entry.delete(0, tk.END)

def delete_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        cur.execute("DELETE FROM notes WHERE note=?", (selected_note,))
        conn.commit()
        update_notes_list()

def edit_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        edit_window = tk.Toplevel(root)
        edit_window.title("Редактировать заметку")
        edit_window.geometry("300x100")
        edit_window.resizable(False, False)

        edit_label = tk.Label(edit_window, text="Измените содержимое заметки:")
        edit_label.pack(pady=5)

        edited_note = tk.StringVar()
        edited_note.set(selected_note)
        edit_entry = tk.Entry(edit_window, textvariable=edited_note)
        edit_entry.pack(pady=5)

        save_button = tk.Button(edit_window, text="Сохранить", command=lambda: save_edited_note(edit_window, selected_note, edited_note.get()))
        save_button.pack(pady=5)

def save_edited_note(edit_window, old_note, new_note):
    cur.execute("UPDATE notes SET note=? WHERE note=?", (new_note, old_note))
    conn.commit()
    update_notes_list()
    edit_window.destroy()

def update_notes_list():
    notes_list.delete(0, tk.END)
    cur.execute("SELECT * FROM notes")
    notes = cur.fetchall()
    for note in notes:
        note_text = note[1]
        notes_list.insert(tk.END, note_text)

def clear_notes():
    cur.execute("DELETE FROM notes")
    conn.commit()
    update_notes_list()

root = customtkinter.CTk()
root.title("Приложение для заметок")
root.geometry("300x400")
root.resizable(0, 0)

note_label = customtkinter.CTkLabel(root, text="Заметка:")
note_label.pack(pady=5)

note_entry = customtkinter.CTkEntry(root)
note_entry.pack(pady=5)

save_button = customtkinter.CTkButton(root, text="Добавить заметку", command=save_note)
save_button.pack(pady=5)

edit_button = customtkinter.CTkButton(root, text="Редактировать заметку", command=edit_note)
edit_button.pack(pady=5)

delete_button = customtkinter.CTkButton(root, text="Удалить заметку", command=delete_note)
delete_button.pack(pady=5)

clear_button = customtkinter.CTkButton(root, text="Очистить список", command=clear_notes)
clear_button.pack(pady=5)

notes_list = tk.Listbox(root, width=45, height=15)
notes_list.pack(pady=5)

scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
scrollbar.config(command=notes_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

notes_list.config(yscrollcommand=scrollbar.set)

db_start()
update_notes_list()

root.mainloop()
conn.close()
