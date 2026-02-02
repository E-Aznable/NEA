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
        label = ttk.Label(self, text="collection", font=LARGE_FONT)
        label.grid(row=0, column=2, padx=10, pady=10)

        button1 = ttk.Button(self, text="back to login", command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0, column=1, padx=10, pady=10)

        current_user_id = controller.login_result

        def display_database(current_user_id):
            conn = sqlite3.connect("MusicDB.db")
            cursor = conn.cursor()
            # SQL query for release names, art and artist names
            cursor.execute(f"""SELECT releases.ReleaseName, artists.ArtistName, releases.ReleaseImage
                            FROM releases, artists, user_releases, user_artists, users
                            WHERE user_releases.ReleaseID = releases.ReleaseID
                            AND user_artists.ArtistID = artists.ArtistID
                            AND user_releases.UserID = users.UserID
                            AND user_artists.UserID = users.UserID
                            AND releases.ArtistID = artists.ArtistID
                            AND users.UserID = {current_user_id}""") # this isnt happy
            i = 1
            j = 2
            for release in cursor:
                release_grouped = ttk.LabelFrame(self, text=f"{release[0]} - {release[1]}") # contain a release in an individual box that can be made clickable (hopefully)
                release_grouped.grid(row=j, column=i, padx=10, pady=10)

                # using webimage class
                web_image = WebImage(release[2]) #  I'm pretty sure this is the nicest way to get the image, be careful if you add more return fields though!
                img = web_image.get() # return the img to be used
                imagelab = ttk.Label(release_grouped, image=img) # stick the image in the release group frame
                imagelab.grid(row=0, column=0)
                imagelab.image = img # store the image reference in the label so its displayed and not trashed

                i+=1
                if i > 5: # count up to 5 images in a row before a new row is started
                    i = 1
                    j += 1
            
        display_database(current_user_id)
        refresh_button = ttk.Button(self, text="refresh collection", command=lambda: display_database(current_user_id))
        refresh_button.grid(row=1, column=2, padx=10, pady=10)

        # going to put the 'add new release' thing as a popup in here for now
        def close_popup(top):
            top.destroy()

        def popupwin():
            # Toplevel window so it appears above the rest of the app
            top = Toplevel(self)
            top.geometry("400x400")

            artist_var=tk.StringVar()
            artist_label = tk.Label(top, text="artist name:")
            artist_label.grid(row=2, column=1, padx=10, pady=10)
            artist_entry = tk.Entry(top, textvariable = artist_var)
            artist_entry.grid(row=2, column=2, padx=10, pady=10)

            release_var=tk.StringVar()
            release_label = tk.Label(top, text="release name:")
            release_label.grid(row=3, column=1, padx=10, pady=10)
            release_entry = tk.Entry(top, textvariable = release_var)
            release_entry.grid(row=3, column=2, padx=10, pady=10)

            def get_inputs():
                self.input_artist = artist_var.get()
                self.input_release = release_var.get()
                artist_var.set("")
                release_var.set("")

            artist_insert_button = ttk.Button(top,text="Add new artist", command=lambda:[get_inputs(), AddArtist(self.input_artist, controller.login_result)])
            artist_insert_button.grid(row=2, column=3)

            release_insert_button = ttk.Button(top,text="Add new release (requires artist)", command=lambda:[get_inputs(), AddRelease(self.input_artist, self.input_release, controller.login_result)])
            release_insert_button.grid(row=3, column=3)

            popup_close_button = ttk.Button(top, text="Ok", command=lambda:close_popup(top))
            popup_close_button.grid(row=1, column=1)
        
        label= ttk.Label(self, text="Add new artist or release")
        label.grid(row=0, column=3)

        button= ttk.Button(self, text= "Click Me!", command=popupwin)
        button.grid(row=1, column=3)


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
