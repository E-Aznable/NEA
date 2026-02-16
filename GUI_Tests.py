# test files
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
            self.resized_image = self.image.resize((200,200)) # nice middle ground size
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
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("LoginTitle.TLabel", font=("Segoe UI", 20, "bold")) # there's probably an easy way to set these in the database class but this is simple
        style.configure("Login.TLabel", font=("Segoe UI", 11))
        style.configure("Login.TButton", font=("Segoe UI", 10))

        card = ttk.Frame(self, padding=30)
        card.grid(row=0, column=0)

        ttk.Label(card, text="Welcome Back", style="LoginTitle.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 20))

        user_var = tk.StringVar()
        pass_var = tk.StringVar()

        ttk.Label(card, text="Username", style="Login.TLabel").grid(row=1, column=0, sticky="w", pady=5)
        user_entry = ttk.Entry(card, textvariable=user_var, width=25)
        user_entry.grid(row=2, column=0, columnspan=2, pady=(0, 15))

        ttk.Label(card, text="Password", style="Login.TLabel").grid(row=3, column=0, sticky="w", pady=5)
        pass_entry = ttk.Entry(card, textvariable=pass_var, show="*", width=25)
        pass_entry.grid(row=4, column=0, columnspan=2, pady=(0, 20))

        self.message_label = ttk.Label(card, text="")
        self.message_label.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        def sign_in_user():
            input_name = user_var.get()
            input_pass = pass_var.get()
            result = login_system.login(self, input_name, input_pass) # dw about this its literally fine

            if result is None:
                self.message_label.config(
                    text="Incorrect username or password",
                    foreground="red"
                )
            else:
                controller.set_login_result(result)
                controller.show_frame(CollectionPage)

            user_var.set("")
            pass_var.set("")

        def sign_up_user():
            input_name = user_var.get()
            input_pass = pass_var.get()
            login_system.register(self, input_name, input_pass)

            self.message_label.config(text="User successfully created",foreground="green")

            user_var.set("")
            pass_var.set("")

        ttk.Button(card,text="Sign In",style="Login.TButton",command=sign_in_user).grid(row=5, column=0, pady=5, sticky="ew")
        ttk.Button(card,text="Sign Up",style="Login.TButton",command=sign_up_user).grid(row=5, column=1, pady=5, padx=(10, 0), sticky="ew") # these cards look way nicer than the frames what was I doing

        user_entry.focus()



class CollectionPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent) # should maybe change this to a super, might be nicer
        self.controller = controller
        self.images = []  # keep Tk references

        label = ttk.Label(self, text="Collection", font=LARGE_FONT)
        label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        back_button = ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame(StartPage))
        back_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        all_artists_button = ttk.Button(self, text="All Artists", command=lambda: controller.show_frame(ArtistsPage))
        all_artists_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # scrolly canvas + scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=2, sticky="ns")
        self.canvas.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # scroll and resize handling
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.wrap_images())
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # make canvas resizable
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        ttk.Button(self, text="Refresh Collection", command=self.display_database).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(self, text="Add New Artist or Release", command=self.pop_up_win).grid(row=2, column=1, padx=10, pady=10, sticky="e")

    def _on_mousewheel(self, event): # rlly stupid how difficult this is
        if event.num == 4:  # linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # windows/mac is simpler
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def display_database(self):
        # remove old scrolly frame and canvas window
        self.canvas.delete("all")

        # new scrolly
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.images.clear()  # clear old image references

        user_id = self.controller.login_result
        if not user_id:
            return

        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT releases.ReleaseID, releases.ReleaseName, artists.ArtistName, releases.ReleaseImage
                       FROM releases
                                JOIN artists ON releases.ArtistID = artists.ArtistID
                                JOIN user_releases ON user_releases.ReleaseID = releases.ReleaseID
                       WHERE user_releases.UserID = ?
                       """, (user_id,))
        data = cursor.fetchall()
        conn.close()

        # create cards for each release
        for idx, (release_id, release_name, artist_name, image_url) in enumerate(data):
            card = ttk.Frame(self.scrollable_frame, padding=10)
            card.grid(row=0, column=idx, padx=15, pady=15)

            web_image = WebImage(image_url)
            img = web_image.get()
            if img:
                self.images.append(img)
                img_label = ttk.Label(card, image=img)
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, rid=release_id: self.open_release_page(rid))

            ttk.Label(card, text=release_name, style="CardTitle.TLabel").pack(pady=(8, 0))
            ttk.Label(card, text=artist_name).pack()

        # update scrolly
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.wrap_images()

    def wrap_images(self):
        children = self.scrollable_frame.winfo_children()
        if not children:
            return

        canvas_width = self.canvas.winfo_width()
        if canvas_width < 10:
            self.after(100, self.wrap_images) # this wait is for safety but i might get rid
            return

        padding = 10
        frame_widths = [w.winfo_reqwidth() + padding for w in children]
        avg_width = max(frame_widths)
        cols = max(1, canvas_width // avg_width)

        for idx, widget in enumerate(children):
            row = idx // cols
            col = idx % cols
            widget.grid_configure(row=row, column=col, padx=padding, pady=padding, sticky="n")

    def open_release_page(self, release_id): # func that makes clickable images useful
        page = self.controller.frames[ReleaseFocusPage]
        if hasattr(page, "set_release"): # what a weird function name
            page.set_release(release_id)
        self.controller.show_frame(ReleaseFocusPage)

    # pop up to add new stuff
    def pop_up_win(self):
        top = Toplevel(self)
        top.geometry("400x400")

        artist_var = tk.StringVar()
        release_var = tk.StringVar()

        tk.Label(top, text="Artist name:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(top, textvariable=artist_var).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(top, text="Release name:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(top, textvariable=release_var).grid(row=1, column=1, padx=10, pady=10)

        def get_inputs():
            self.input_artist = artist_var.get()
            self.input_release = release_var.get()
            artist_var.set("")
            release_var.set("")

        ttk.Button(top, text="Add New Artist",command=lambda: [get_inputs(), AddArtist(self.input_artist, self.controller.login_result)]).grid(row=2, column=0, padx=10, pady=10) # these variables always get set dont worry about it
        ttk.Button(top, text="Add New Release",command=lambda: [get_inputs(), AddRelease(self.input_artist, self.input_release, self.controller.login_result)]).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(top, text="Close", command=top.destroy).grid(row=3, column=0, columnspan=2, pady=10)



class ReleaseFocusPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_image = None

        style = ttk.Style()
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Track.TLabel", font=("Segoe UI", 11))
        style.configure("Header.TButton", font=("Segoe UI", 10))

        self.header = ttk.Frame(self)
        self.header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        self.grid_columnconfigure(0, weight=1)

        self.back_button = ttk.Button(self.header,text="← Back",style="Header.TButton",command=lambda: controller.show_frame(CollectionPage))
        self.back_button.pack(side="left")

        self.title_artist_label = ttk.Label(self.header,text="",style="Title.TLabel")
        self.title_artist_label.pack(side="left", padx=20)

        self.main = ttk.Frame(self)
        self.main.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        self.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=2)
        self.main.grid_rowconfigure(0, weight=1)

        self.image_label = ttk.Label(self.main)
        self.image_label.grid(row=0, column=0, sticky="n")

        # tracklist
        self.track_container = ttk.Frame(self.main)
        self.track_container.grid(row=0, column=1, sticky="nsew", padx=(30, 0))

        ttk.Label(self.track_container,text="Tracklist",font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # scrolly
        self.canvas = tk.Canvas(self.track_container,borderwidth=0,highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.track_container,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0),window=self.scrollable_frame,anchor="nw")

        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # scroll only when mouse is over canvas
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_release(self, release_id):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT releases.ReleaseName, artists.ArtistName, releases.ReleaseImage
            FROM releases
            JOIN artists ON releases.ArtistID = artists.ArtistID
            WHERE releases.ReleaseID = ?
        """, (release_id,))
        row = cursor.fetchone()

        if row:
            release_name, artist_name, image_url = row
            self.title_artist_label.config(
                text=f"{release_name} — {artist_name}"
            )

            web_image = WebImage(image_url)
            img = web_image.get()

            if img:
                self.current_image = img
                self.image_label.config(image=img)
            else:
                self.image_label.config(text="Image not available")

        conn.close()
        self.display_tracks(release_id)

    def display_tracks(self, release_id):
        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT TrackName, TrackNum
            FROM tracks
            WHERE ReleaseID = ?
            ORDER BY TrackNum
        """, (release_id,))

        tracks = cursor.fetchall()
        conn.close()

        for track_name, track_num in tracks:
            track_frame = ttk.Frame(self.scrollable_frame)
            track_frame.pack(fill="x", pady=4)
            ttk.Label(track_frame,text=f"{track_num}.",width=4,anchor="w",style="Track.TLabel").pack(side="left")
            ttk.Label(track_frame,text=track_name,style="Track.TLabel").pack(side="left", fill="x", expand=True)



class ReviewPage(tk.Frame): # this is first on the chopping block if I run out of time
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller



class ArtistsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.artist_id_vars = {}  # store checkbox states
        self.artist_name_vars = {}

        # header
        label = ttk.Label(self, text="Artists", font=LARGE_FONT)
        label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        back_button = ttk.Button(self,text="Back to Login",command=lambda: controller.show_frame(StartPage))
        back_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        collection_button = ttk.Button(self,text="Collection",command=lambda: controller.show_frame(CollectionPage))
        collection_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # scrolly
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.grid(row=1, column=2, sticky="ns")
        self.canvas.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>",lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # button yay
        ttk.Button(self,text="Find New Releases",command=self.fetch_new_music).grid(row=2, column=0, columnspan=3, pady=10)

    def display_artists_checkable(self):
        # clear old widgets just in case
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.artist_id_vars.clear()

        user_id = self.controller.login_result
        if not user_id:
            return

        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT artists.ArtistID, artists.ArtistName
            FROM artists
            JOIN releases ON releases.ArtistID = artists.ArtistID
            JOIN user_releases ON user_releases.ReleaseID = releases.ReleaseID
            WHERE user_releases.UserID = ?
            ORDER BY artists.ArtistName
        """, (user_id,))

        artists = cursor.fetchall()
        conn.close()

        for artist_id, artist_name in artists:
            var = tk.BooleanVar()
            self.artist_id_vars[artist_id] = var
            self.artist_name_vars[artist_name] = var

            frame = ttk.Frame(self.scrollable_frame, padding=5)
            frame.pack(fill="x", padx=15, pady=5)

            checkbox = ttk.Checkbutton(frame,text=artist_name,variable=var)
            checkbox.pack(anchor="w")

    def fetch_new_music(self):
        selected_artist_ids = [
            artist_id
            for artist_id, var in self.artist_id_vars.items()
            if var.get() # get artist IDs from checkboxed artists
        ]
        selected_artist_names = [
            artist_name
            for artist_name, var in self.artist_name_vars.items()
            if var.get()
        ]

        print("selected artists:", selected_artist_ids, selected_artist_names)

        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()

        for i in range(len(selected_artist_ids)):
            user_id = self.controller.login_result # duplicate but whatever ive got 4 days to finish this
            if not user_id:
                return
            artist_id = selected_artist_ids[i]

            cursor.execute("""
                           SELECT DiscogsArtistID
                           FROM artists
                           WHERE ArtistID = ?
                           """, (artist_id,))

            artist_discogs_id_tuple = cursor.fetchone() # discogs id is what we need, not table id
            artist_discogs_id = artist_discogs_id_tuple[0]
            print(artist_discogs_id)

            artist_name = selected_artist_names[i]
            AddNew(artist_discogs_id, artist_name, user_id)

        conn.close()

    def on_show(self): # I should use this more in other classes lol
        self.display_artists_checkable()



app = DatabaseApp()
app.mainloop()
