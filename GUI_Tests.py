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
        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="login page", font=LARGE_FONT)
        label.grid(row=0, column=2, padx=10, pady=10)

        # conn = sqlite3.connect("MusicDB.db") # using our db
        # cursor = conn.cursor() # just in case

        user_var=tk.StringVar() # set username as a string var for input later
        user_label = tk.Label(self, text="username:")
        user_label.grid(row=2, column=1, padx=10, pady=10)
        user_entry = tk.Entry(self, textvariable = user_var)
        user_entry.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

        pass_var=tk.StringVar() # set password as string var too
        pass_label = tk.Label(self, text="password:")
        pass_label.grid(row=3, column=1, padx=10, pady=10)
        pass_entry = tk.Entry(self, textvariable = pass_var)
        pass_entry.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

        sign_in_button = tk.Button(self, text="Sign in", command=lambda: sign_in_user())
        sign_in_button.grid(row=4, column=2, sticky="w")
        sign_up_button = tk.Button(self, text="Sign up", command=lambda: sign_up_new_user())
        sign_up_button.grid(row=4, column=3, sticky="w")

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
        # clear old widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.images.clear()

        user_id = self.controller.login_result
        if not user_id: # get the id of the current user
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

        # create frames for each release
        for idx, (release_id, release_name, artist_name, image_url) in enumerate(data):
            frame = ttk.LabelFrame(self.scrollable_frame, text=f"{release_name} - {artist_name}")
            web_image = WebImage(image_url)
            img = web_image.get()
            if img:
                self.images.append(img)  # keep reference
                label = ttk.Label(frame, image=img)
                label.image = img
                label.grid(row=0, column=0)
                label.bind("<Button-1>", lambda e, rid=release_id: self.open_release_page(rid)) # first part of the super cool clickable images

            frame.grid(row=0, column=idx, padx=10, pady=10)  # temp row/col, wrap_images will fix

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

        ttk.Button(top, text="Add New Artist",command=lambda: [get_inputs(), AddArtist(self.input_artist, self.controller.login_result)]).grid(row=2, column=0, padx=10, pady=10)
        ttk.Button(top, text="Add New Release",command=lambda: [get_inputs(), AddRelease(self.input_artist, self.input_release, self.controller.login_result)]).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(top, text="Close", command=top.destroy).grid(row=3, column=0, columnspan=2, pady=10)


class ReleaseFocusPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.current_image = None  # keep reference to Tk image

        self.back_button = ttk.Button(self, text="Back to Collection", command=lambda: controller.show_frame(CollectionPage))
        self.back_button.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        
        self.title_artist_label = ttk.Label(self, text="", font=("Verdana", 12)) # make to set later
        self.title_artist_label.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        self.image_label = ttk.Label(self) # make to set later
        self.image_label.grid(row=2, column=0, padx=10, pady=10, sticky="nw")

        self.tracklist_label = ttk.Label(self, text="Tracklist", font=("Verdana", 12))
        self.tracklist_label.grid(row=1, column=2, columnspan=2, sticky="nw")

        # scrolly canvas + scrollbar AGAIN for tracks 
        self.canvas = tk.Canvas(self, borderwidth=0, background="#f0f0f0")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=2, column=4, rowspan=2, sticky="ns")
        self.canvas.grid(row=2, column=2, columnspan=2, rowspan=2, sticky="nsew")
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) # mousewheel in two classes seems to break it in both? bad
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _on_mousewheel(self, event): # still stupid that this is the best way to do this
        if event.num == 4:  # linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # windows/mac is simpler
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def set_release(self, release_id):
        # clear old widgets just in case
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # fetch release info from DB and display it
        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT releases.ReleaseName, artists.ArtistName, releases.ReleaseImage
            FROM releases
            JOIN artists ON releases.ArtistID = artists.ArtistID
            WHERE releases.ReleaseID = ?
        """, (release_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            release_name, artist_name, image_url = row
            self.title_artist_label.config(text=release_name + " - " + artist_name) # dynamic release name
            # self.artist_label.config(text=f"By {artist_name}") # dynamic artist name

            web_image = WebImage(image_url)
            img = web_image.get()
            if img:
                self.current_image = img  # keep reference
                self.image_label.config(image=img)
            else:
                self.image_label.config(image="", text="Image not available")
        else:
            self.title_artist_label.config(text="Release not found")
            # self.artist_label.config(text="")
            self.image_label.config(image="", text="")

        conn.close()
        self.display_tracks(release_id)

    def display_tracks(self, release_id):
        conn = sqlite3.connect("MusicDB.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tracks.TrackName, tracks.TrackNum
            FROM tracks
            WHERE ReleaseID = ?
        """, (release_id,))
        tracks = cursor.fetchall()

        if tracks:
            for track in tracks:
                track_name = track[0]
                print(track_name)
                track_num = track[1]
                print(track_num)
                frame = ttk.LabelFrame(self.scrollable_frame)
                test_label = ttk.Label(frame, text=f"{track_num} - {track_name}")
                test_label.grid(row=0, column=0)
                frame.grid(row=track_num, column=0, padx=2, sticky="w") # might wrap later

        else:
            self.title_artist_label.config(text="Tracks not found")
            # self.artist_label.config(text="")
            self.image_label.config(image="", text="")
            
        conn.close()


class ReviewPage(tk.Frame): # this is first on the chopping block if I run out of time
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller


class ArtistsPage(tk.Frame): # next up?
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text="Artists", font=LARGE_FONT)
        label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        back_button = ttk.Button(self, text="Back to Login", command=lambda: controller.show_frame(StartPage))
        back_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        all_artists_button = ttk.Button(self, text="Collection", command=lambda: controller.show_frame(CollectionPage))
        all_artists_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # labels and buttons and scrolly canvas and stuff
        # big button that has command=self.fetch_new_music

    def display_artists_checkable(self):
        # func to retrieve all user artists, display them in a scrolly list and with a checkbox so the user can select them for finding new music
        pass

    def fetch_new_music(self):
        # func that uses fetch_new_releases from (FindNewReleases, needs to go into AddReleaseHandler) on any checkboxed artists
        pass


app = DatabaseApp()
app.mainloop()
