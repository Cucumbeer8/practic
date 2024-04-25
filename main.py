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
    note_entry.delete(0, customtkinter.END)


def delete_note():
    index = notes_list.curselection()
    if index:
        selected_note = notes_list.get(index)
        cur.execute("DELETE FROM notes WHERE note=?", (selected_note,))
        conn.commit()
        update_notes_list()


def update_notes_list():
    notes_list.delete(0, customtkinter.END)
    cur.execute("SELECT * FROM notes")
    notes = cur.fetchall()
    for note in notes:
        note_text = note[1]
        notes_list.insert(customtkinter.END, note_text)


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

delete_button = customtkinter.CTkButton(root, text="Удалить заметку", command=delete_note)
delete_button.pack(pady=5)

notes_list = tk.Listbox(root, width=45, height=15)
notes_list.pack(pady=5)

db_start()
update_notes_list()

root.mainloop()
conn.close()
