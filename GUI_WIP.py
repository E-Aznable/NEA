# example of a really simple GUI database, still in progress

import tkinter as tk
import sqlite3
from login import * # import login system
from tkinter import messagebox

class DatabaseApp:
    def __init__(self, root):
        # initializes database and shows login screen
        self.root = root
        self.root.title("SQLite Database GUI v1")

        # Create a database or connect to an existing one
        self.conn = sqlite3.connect("MusicDB.db") # using our db
        self.cursor = self.conn.cursor()

        # was considering a CREATE IF NOT statement but main should always run before GUI so im not going to worry

        # Create GUI elements
        self.user_var=tk.StringVar() # set username as a string var for input later
        self.user_label = tk.Label(root, text="username:")
        self.user_label.pack()
        self.user_entry = tk.Entry(root, textvariable = self.user_var)
        self.user_entry.pack()
        
        self.pass_var=tk.StringVar() # set password as string var too
        self.pass_label = tk.Label(root, text="password:")
        self.pass_label.pack()
        self.pass_entry = tk.Entry(root, textvariable = self.pass_var)
        self.pass_entry.pack()

        self.sign_in_button = tk.Button(root, text="Sign in", command=self.sign_in_user)
        self.sign_in_button.pack()
        self.sign_up_button = tk.Button(root, text="Add new user", command=self.sign_up_user)
        self.sign_up_button.pack()

        self.user_listbox = tk.Listbox(root)
        self.user_listbox.pack()

        self.delete_button = tk.Button(root, text="Delete value", command=self.delete_table_value)
        self.delete_button.pack()

        self.load_users()

    login_system = login_system()

    def sign_in_user(self):
        input_name = self.user_var.get() # i think this is probably the nicest way to do this
        input_pass = self.pass_var.get()
        # print(input_name, input_pass) # testing
        login_system.login(self, input_name, input_pass) # this works yes
        self.user_var.set("")
        self.pass_var.set("")


    def sign_up_user(self): # this will need some commit and load stuff here as well as the execute from login_system
        user_name = self.user_name_entry.get()
        user_pass = self.user_pass_entry.get()
        if user:
            self.cursor.execute("INSERT INTO users (user) VALUES (?)", (user,))
            self.conn.commit()
            self.load_table()
            self.user_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please input a user.")

    def load_users(self): # to make logging in easy for development
        self.user_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for row in users:
            self.user_listbox.insert(tk.END, row[0]) # want to display these with relavant field names and not one afer the others as they are now
            self.user_listbox.insert(tk.END, row[1])
            self.user_listbox.insert(tk.END, row[2])

    def delete_table_value(self): # modify to take input values
        pass
        selected_user = self.user_listbox.get(tk.ACTIVE)
        if selected_user:
            self.cursor.execute("DELETE FROM users WHERE user=?", (selected_user,))
            self.conn.commit()
            self.load_table()
        else:
            messagebox.showwarning("Warning", "Please select a user to delete.")

    def __del__(self):
        # maybe i need this
        self.conn.close()

    # need a function to display releases in a main collection screen

    # need a function to display specific release info if you click into it from collection screen

    # need a function to display artists and select following

    # need a function to display and edit reviews

    # need a function that runs an 'add something' screen to get input new music/artists/both

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x400")
    app = DatabaseApp(root)
    root.mainloop()