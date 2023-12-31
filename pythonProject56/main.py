import customtkinter
from tkinter import *
from tkinter import ttk
from datetime import datetime
import sqlite3

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


def db_start():
    global conn, cur
    conn = sqlite3.connect('tasks_db.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS notes_table (completed bool, task text, date text)''')


def loading_data():
    cur.execute("SELECT * FROM notes_table")
    rows = cur.fetchall()

    for row in rows:
        if row[0] == 'True':
            tree.insert('', 'end', values=(row[1], row[2], '✖'), tags='checked')
        else:
            tree.insert('', 'end', values=(row[1], row[2], '✖'), tags='unchecked')


def processing_events(e):
    try:
        selected_item = tree.selection()[0]
        values = tree.item(selected_item, option="values")

        if tree.identify_column(e.x) == '#0':
            rowid = tree.identify_row(e.y)
            tag = tree.item(rowid, 'tags')[0]

            if tag == 'checked':
                tree.item(rowid, tags='unchecked')
                cur.execute('''UPDATE notes_table SET completed = ? WHERE task = ?''', ('False', values[0], ))
                conn.commit()
            else:
                tree.item(rowid, tags='checked')
                cur.execute('''UPDATE notes_table SET completed = ? WHERE task = ?''', ('True', values[0],))
                conn.commit()
        elif tree.identify_column(e.x) == '#3':
            tree.delete(selected_item)
            cur.execute('''DELETE FROM notes_table WHERE task = ?''', (values[0], ))
            conn.commit()
        else:
            pass
    except IndexError:
        pass


def add(task):
    tree.insert('', 'end', values=(task, f'{datetime.now():%d-%m-%y %H:%M:%S}', '✖'), tags='unchecked')
    cur.execute("INSERT INTO notes_table VALUES ('%s','%s','%s')" % (False, task, f'{datetime.now():%d-%m-%y %H:%M:%S}'))
    conn.commit()


def add_task():
    window = customtkinter.CTkToplevel(root)
    window.title('Добавить задачу')
    window.wm_attributes('-topmost', True)
    window.geometry('300x80')

    task_text = customtkinter.CTkEntry(window, width=250)
    task_text.pack(pady=5)

    customtkinter.CTkButton(window, text='Добавить',
                            font=customtkinter.CTkFont(family='Arial', size=13, weight='bold'),
                            command=lambda: add(task_text.get())).pack()


root = customtkinter.CTk()
root.title("Планировщик задач")
root.geometry('810x305')
root.resizable(0, 0)

style = ttk.Style()
style.theme_use('default')


style.configure('Treeview',
                background='#2a2d2e',
                foreground='white',
                rowheight=25,
                fieldbackground='#343638',
                bordercolor='#343638',
                borderwidth=0)
style.map('Treeview', background=[('selected', '#22559b')])

style.configure('Treeview.Heading',
                background='#565b5e',
                foreground='white',
                relief='flat')
style.map('Treeview.Heading',
          background=[('active', '#3484F0')])

im_checked = PhotoImage('checked', data=b'GIF89a\x0e\x00\x0e\x00\xf0\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x0e\x00\x0e\x00\x00\x02#\x04\x82\xa9v\xc8\xef\xdc\x83k\x9ap\xe5\xc4\x99S\x96l^\x83qZ\xd7\x8d$\xa8\xae\x99\x15Zl#\xd3\xa9"\x15\x00;')
im_unchecked = PhotoImage('unchecked', data=b'GIF89a\x0e\x00\x0e\x00\xf0\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x0e\x00\x0e\x00\x00\x02\x1e\x04\x82\xa9v\xc1\xdf"|i\xc2j\x19\xce\x06q\xed|\xd2\xe7\x89%yZ^J\x85\x8d\xb2\x00\x05\x00;')

tree = ttk.Treeview(root)
tree.tag_configure('checked', image=im_checked)
tree.tag_configure('unchecked', image=im_unchecked)
tree['columns'] = ('column1', 'column2', 'column3', 'column4')

tree.heading('#0', text='Статус')
tree.column("#0", width=50)
tree.heading('#1', text='Задача')
tree.column("#1", width=600)
tree.heading('#2', text='Дата')
tree.column("#2", width=100)
tree.heading('#3', text='Удалить')
tree.column("#3", width=60, anchor=CENTER)

tree.pack()

btn_add_task = customtkinter.CTkButton(root, text='Добавить задачу',
                                       font=customtkinter.CTkFont(family='Arial', size=13, weight='bold'),
                                       command=add_task)
btn_add_task.pack(anchor=S, side=BOTTOM, pady=5)

db_start()
loading_data()
tree.bind('<Button-1>', processing_events)

root.mainloop()
conn.close()