# this is basically main, runs GUI and all the other files and functions

import tkinter as tk 
import sqlite3
from login import * # import login system
from tkinter import ttk
from tkinter import *
from PIL import ImageTk, Image # pillow package manages display of images from URLs
import requests
from io import BytesIO
from AddReleaseHandler import * # import SQL functions

with open("backend.py") as backend:
    exec(backend.read()) # run backend to make sure local DB exists and works

LARGE_FONT = ("Verdana", 16) # this is a fun way to do a global BIG FONT but I might change it

class WebImage:
    def __init__(self, url):
        try:
            # set the headers to simulate a browser request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" # fake ass browser request lol
            }

            # send the GET request with the user agent header
            u = requests.get(url, headers=headers, stream=True)
            u.raise_for_status()  # raise an exception for 4xx/5xx status codes

            # check if the content is an image (by looking at the content type header)
            if 'image' not in u.headers['Content-Type']:
                raise ValueError("URL does not point to a valid image")

            # img must be resized before it is a PhotoImage, annoyingly
            self.image = Image.open(BytesIO(u.content))
            self.resized_image = self.image.resize((200,200))
            self.image = ImageTk.PhotoImage(self.resized_image)
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            self.image = None
        except ValueError as e:
            print(f"Error: {e}")
            self.image = None
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image = None

    def get(self):
        return self.image # return image for actual use


class DatabaseApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        # initializes tk functions, creates frames, containers and iterates through page layouts
        tk.Tk.__init__(self, *args, **kwargs)

        self.login_result = None

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # iterating through an array consisting of the different page layouts
        for F in (StartPage, CollectionPage, ReleaseFocusPage, ReviewPage, ArtistsPage):
            frame = F(container, self)

            # initializing frame of that object from StartPage for loop
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

    def set_login_result(self, result): # user id number
        self.login_result = result  # store login result here for global access


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="login page", font=LARGE_FONT)
        label.grid(row=0, column=2, padx=10, pady=10)

        sign_in_button = tk.Button(self, text="Sign in", command=lambda: sign_in_user())
        sign_in_button.grid(row=4, column=2, padx=10, pady=10)
        sign_up_button = tk.Button(self, text="Sign up", command=lambda: sign_up_new_user())
        sign_up_button.grid(row=4, column=3, padx=10, pady=10)

        # conn = sqlite3.connect("MusicDB.db") # using our db
        # cursor = conn.cursor() # just in case

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

        self.incorrect_label = tk.Label(self, text="no input yet") # as far as I can tell this kind of needs to exist before its actually used

        def sign_in_user():
            input_name = user_var.get() # I think this is probably the nicest way to do this
            input_pass = pass_var.get()
            login_result = login_system.login(self, input_name, input_pass)
            if login_result is None:
                incorrect_label_func()
            else: # login and screen switch here
                controller.set_login_result(login_result) # set the login result
                controller.show_frame(CollectionPage)
            user_var.set("")
            pass_var.set("")

        def sign_up_new_user():
            input_name = user_var.get()
            input_pass = pass_var.get()
            login_system.register(self, input_name, input_pass)
            user_var.set("")
            pass_var.set("")
            success_msg_func()

        def incorrect_label_func():  # makes an 'incorrect username or password' msg appear
            if self.incorrect_label:
                self.incorrect_label.destroy()
            self.incorrect_label = tk.Label(self, text ="incorrect username or password", fg="red")
            self.incorrect_label.grid(row=5, column=2, padx=10, pady=10)

        def success_msg_func(): 
            if self.incorrect_label:
                self.incorrect_label.destroy()
            self.incorrect_label = tk.Label(self, text ="successfully added new user", fg="green")
            self.incorrect_label.grid(row=5, column=2, padx=10, pady=10)

        # controller.bind("<Return>", sign_in_user()) # keyboard shortcut to make enter key sign in, not working IDK I'll do it later

    login_system = login_system()


class CollectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="collection", font=LARGE_FONT)
        label.grid(row=0, column=1, padx=10, pady=10)
        button1 = ttk.Button(self, text="back to login", command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0, column=0, padx=10, pady=10)

        # make it scrolly with a canvas
        self.canvas = tk.Canvas(self, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(row=2, column=4, sticky="ns")
        self.canvas.grid(row=2, column=0, columnspan=4, sticky="nsew")

        # frame goes inside the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        # resize scroll region when contents change
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # allow the resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Buttons
        ttk.Button(self, text="Refresh Collection", command=self.display_database).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(self, text="Add New Artist or Release", command=self.pop_up_win).grid(row=1, column=1, padx=10, pady=10)

        # mouse scrolling for the scrolly canvas
        def _on_mousewheel(event):
            if self.tk.call("tk", "windowingsystem") == "aqua":  # actually useful for college computers lol
                self.canvas.yview_scroll(-1 * event.delta, "units")
            else:  # Windows and Linux
                self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def on_show(self):
        self.display_database()

    def display_database(self):
        current_user_id = self.controller.login_result
        if current_user_id is None:
            return

        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT releases.ReleaseName, artists.ArtistName, releases.ReleaseImage
                       FROM releases
                                JOIN artists ON releases.ArtistID = artists.ArtistID
                                JOIN user_releases ON user_releases.ReleaseID = releases.ReleaseID
                       WHERE user_releases.UserID = ?
                       """, (current_user_id,))

        row = 0
        col = 0

        for release_name, artist_name, image_url in cursor.fetchall():
            frame = ttk.LabelFrame(
                self.scrollable_frame,
                text=f"{release_name} - {artist_name}"
            )
            frame.grid(row=row, column=col, padx=10, pady=10)

            web_image = WebImage(image_url)
            img = web_image.get()

            img_label = ttk.Label(frame, image=img)
            img_label.image = img  # DONT trash it
            img_label.pack()

            col += 1
            if col >= 5: # new row after 5 columns
                col = 0
                row += 1

        conn.close()

    # going to put the 'add new release' thing as a popup in here for now
    def pop_up_win(self):
        top = Toplevel(self)
        top.geometry("400x400")

        artist_var = tk.StringVar()
        release_var = tk.StringVar()

        tk.Label(top, text="Artist name:").grid(row=2, column=1, padx=10, pady=10)
        tk.Entry(top, textvariable=artist_var).grid(row=2, column=2, padx=10, pady=10)

        tk.Label(top, text="Release name:").grid(row=3, column=1, padx=10, pady=10)
        tk.Entry(top, textvariable=release_var).grid(row=3, column=2, padx=10, pady=10)

        def get_inputs():
            self.input_artist = artist_var.get()
            self.input_release = release_var.get()
            artist_var.set("")
            release_var.set("")

        ttk.Button(top, text="Add New Artist",
                   command=lambda: [get_inputs(), AddArtist(self.input_artist, self.controller.login_result)]
                   ).grid(row=2, column=3)

        ttk.Button(top, text="Add New Release",
                   command=lambda: [get_inputs(), AddRelease(self.input_artist, self.input_release, self.controller.login_result)]
                   ).grid(row=3, column=3)

        ttk.Button(top, text="Close", command=top.destroy).grid(row=1, column=1)


class ReleaseFocusPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="focus", font=LARGE_FONT)
        label.grid(row=0, column=1, padx=10, pady=10)

        back_button = ttk.Button(self, text="back", command=lambda: controller.show_frame(CollectionPage))
        back_button.grid(row=1, column=1, padx=10, pady=10)

        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()


class ReviewPage(tk.Frame): # this is first on the chopping block if I run out of time
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


class ArtistsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)


app = DatabaseApp()
app.mainloop()
