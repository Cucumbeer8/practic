import tkinter as tk

root = tk.Tk()
root.title('Создай свой телефон')
width = 600
height = 800
backg = "grey"
icon = tk.PhotoImage(file='icon.png')
root.iconphoto(False, icon)
root.config(bg=backg)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
center_window(root, width, height)
root.resizable(False, False)


root.mainloop()