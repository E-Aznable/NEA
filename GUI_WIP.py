# this should be one of the bigger files that calls all the others

# NEED A MAJOR REFACTOR TO ACCOMMODATE MULTIPLE PAGES!!!!

import tkinter as tk
import sqlite3
from login import * # import login system
from tkinter import ttk
from tkinter import *

LARGE_FONT = ("Verdana", 12)


class DatabaseApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        # initializes tk functions, creates frames, containers and iterates through page layouts
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initializing frames to an empty array
        self.frames = {}

        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, CollectionPage):
            frame = F(container, self)

            # initializing frame of that object from
            # StartPage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

        # to display the current frame passed as
        # parameter

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # label of frame Layout 2
        label = ttk.Label(self, text="login page", font=LARGE_FONT)
        # putting the grid in its place by using grid
        label.grid(row=0, column=4, padx=10, pady=10)

        sign_in_button = tk.Button(self, text="Sign in", command=lambda: sign_in_user())
        sign_in_button.grid(row=4, column=1, padx=10, pady=10)

        # button1 = ttk.Button(self, text="Page 1", command=lambda: controller.show_frame(CollectionPage))
        # button1.grid(row=1, column=1, padx=10, pady=10)

        # Create a database or connect to an existing one
        conn = sqlite3.connect("MusicDB.db") # using our db
        cursor = conn.cursor()

        # Create GUI elements
        user_var=tk.StringVar() # set username as a string var for input later
        user_label = tk.Label(self, text="username:")
        user_label.grid(row=2, column=1, padx=10, pady=10)
        user_entry = tk.Entry(self, textvariable = user_var)
        user_entry.grid(row=2, column=2, padx=10, pady=10)

        pass_var=tk.StringVar() # set password as string var too
        pass_label = tk.Label(self, text="password:")
        pass_label.grid(row=3, column=1, padx=10, pady=10)
        pass_entry = tk.Entry(self, textvariable = pass_var)
        pass_entry.grid(row=3, column=2, padx=10, pady=10)

        # sign_up_button = tk.Button(self, text="Add new user", command=self.sign_up_user)
        # sign_up_button.grid(row=5, column=1, padx=10, pady=10)

        self.incorrect_label = tk.Label(self, text="no input yet") # as far as I can tell this kind of needs to exist before its actually used

        def sign_in_user():
            input_name = user_var.get() # I think this is probably the nicest way to do this
            input_pass = pass_var.get()
            login_result = login_system.login(self, input_name, input_pass)
            if login_result is None:
                incorrect_label_func()
            else: # login and screen switch here
                controller.show_frame(CollectionPage)
            user_var.set("")
            pass_var.set("")

        def incorrect_label_func():  # makes an 'incorrect username or password' msg appear
            if self.incorrect_label:
                self.incorrect_label.destroy()
            self.incorrect_label = tk.Label(self, text ="incorrect username or password", fg="red")
            self.incorrect_label.grid(row=5, column=1, padx=10, pady=10)

    login_system = login_system()



class CollectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Page 1", font=LARGE_FONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(self, text="StartPage",
                             command=lambda: controller.show_frame(StartPage))

        # putting the button in its place
        # by using grid
        button1.grid(row=1, column=1, padx=10, pady=10)



# class WIP(tk.Frame): # all messy
#     # need a function to display releases in a main collection screen
#     def display_collection(self, root, userID):
#         self.userID = userID
#         self.root = root
#         self.root.title("collection viewer")
#
#         self.conn = sqlite3.connect("MusicDB.db") # connect to db
#         self.cursor = self.conn.cursor()
#
#         self.cursor.execute("SELECT * FROM user_releases WHERE userID = ?", (self.userID,))
#         rows = self.cursor.fetchall()
#         print(rows)
#
#
#     # need a function to display specific release info if you click into it from collection screen
#
#     # need a function to display artists and select following
#
#     # need a function to display and edit reviews
#
#     # need a function that runs an 'add something' screen to get input new music/artists/both
#
#
#
#     def sign_up_user(self): # this will need some commit and load stuff here as well as the execute from login_system
#         new_name = self.user_var.get()
#         new_pass = self.pass_var.get()
#         login_system.register(self, new_name, new_pass)
#         login_system.add_to_users(self)
#         self.user_var.set("")
#         self.pass_var.set("")
#         self.load_users() # refresh table for testing
#
#
#     def load_users(self): # just displays usernames and passwords to make dev easy
#         self.user_listbox.delete(0, tk.END)
#         self.pass_listbox.delete(0, tk.END)
#         self.cursor.execute("SELECT * FROM users")
#         users = self.cursor.fetchall()
#         for row in users:
#             self.user_listbox.insert(tk.END, row[1])
#             self.pass_listbox.insert(tk.END, row[2])
#
#     # users should only be able to delete data that is theirs while logged in
#     # # so this needs to change
#     def delete_table_value(self):
#         pass
#         selected_user = self.user_listbox.get(tk.ACTIVE)
#         if selected_user:
#             self.cursor.execute("DELETE FROM users WHERE user=?", (selected_user,))
#             self.conn.commit()
#             self.load_table()
#         else:
#             messagebox.showwarning("Warning", "Please select a user to delete.")
#
#     def __del__(self):
#         # maybe i need this
#         self.conn.close()
#


app = DatabaseApp()
app.mainloop()
