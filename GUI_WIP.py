# example of a really simple GUI database, still in progress

import tkinter as tk
import sqlite3
from login import * # import login system
from tkinter import messagebox
from tkinter import *

class DatabaseApp:
    def __init__(self, root):
        # initializes database and shows login screen
        self.root = root
        self.pane = Frame(root)
        self.pane.pack(fill=BOTH, expand=True) # pane that expands to window size, more flexible than just using root
        self.root.title("SQLite Database GUI v1.5")

        # Create a database or connect to an existing one
        self.conn = sqlite3.connect("MusicDB.db") # using our db
        self.cursor = self.conn.cursor()

        # was considering a CREATE IF NOT statement but main should always run before GUI so im not going to worry

        # Create GUI elements
        self.user_var=tk.StringVar() # set username as a string var for input later
        self.user_label = tk.Label(self.pane, text="username:")
        self.user_label.pack(side=TOP, fill=X)
        self.user_entry = tk.Entry(self.pane, textvariable = self.user_var)
        self.user_entry.pack(side=TOP)
        
        self.pass_var=tk.StringVar() # set password as string var too
        self.pass_label = tk.Label(self.pane, text="password:")
        self.pass_label.pack(side=TOP, fill=X)
        self.pass_entry = tk.Entry(self.pane, textvariable = self.pass_var)
        self.pass_entry.pack(side=TOP)

        self.sign_in_button = tk.Button(self.pane, text="Sign in", command=self.sign_in_user)
        self.sign_in_button.pack()
        self.sign_up_button = tk.Button(self.pane, text="Add new user", command=self.sign_up_user)
        self.sign_up_button.pack()
        
        self.incorrect_label = tk.Label(self.pane, text="no input yet") # bad input message, no need to pack it


        # this stuff is only necessary for testing

        # self.user_listbox = tk.Listbox(self.pane)
        # self.pass_listbox = tk.Listbox(self.pane)
        # self.user_listbox.pack(side=LEFT, fill=X, expand=True, padx=5, pady=5)
        # self.pass_listbox.pack(side=RIGHT, fill=X, expand=True, padx=5, pady=5)

        # self.load_users() 

    login_system = login_system()

    # need a function to display releases in a main collection screen

    # need a function to display specific release info if you click into it from collection screen

    # need a function to display artists and select following

    # need a function to display and edit reviews

    # need a function that runs an 'add something' screen to get input new music/artists/both

    def incorrect_label_func(self): # trying to make an 'incorrect input' message appear in the gui
        if self.incorrect_label:
            self.incorrect_label.destroy()
        self.incorrect_label = tk.Label(self.pane, text = "incorrect username or password", fg="red")
        self.incorrect_label.pack(side=TOP)

    def sign_in_user(self):
        input_name = self.user_var.get() # i think this is probably the nicest way to do this
        input_pass = self.pass_var.get()
        login_result = login_system.login(self, input_name, input_pass) # this works yes
        if login_result is None:
            self.incorrect_label_func()
        self.user_var.set("")
        self.pass_var.set("")
        # need to return user ID to load pages for the correct user


    def sign_up_user(self): # this will need some commit and load stuff here as well as the execute from login_system
        new_name = self.user_var.get()
        new_pass = self.pass_var.get()
        login_system.register(self, new_name, new_pass)
        login_system.add_to_users(self)
        self.user_var.set("")
        self.pass_var.set("")
        self.load_users() # refresh table for testing

    
    def load_users(self): # to make logging in easy for development
        self.user_listbox.delete(0, tk.END)
        self.pass_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT * FROM users")
        users = self.cursor.fetchall()
        for row in users:
            # self.user_listbox.insert(tk.END, row[0]) # want to display these with relavant field names and not one afer the others as they are now
            self.user_listbox.insert(tk.END, row[1])
            self.pass_listbox.insert(tk.END, row[2])
        
    # users should only be able to delete data that is theirs while logged in
    # # so this needs to change
    def delete_table_value(self): 
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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x200")
    app = DatabaseApp(root)
    root.mainloop()