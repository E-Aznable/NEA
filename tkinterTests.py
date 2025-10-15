# test file
# modify this to save the input to a table rather than just clear it
# main could use this then trigger other relevant files if an artist or release was input
# should also output a boolean stating whether it was artist or release if that becomes the case

from tkinter import *
import tkinter as tk
 
root=tk.Tk()

# setting the windows size
# could make it more normal lol
root.geometry("600x400")
 
# declaring string variable
# for storing artist and release
artist_var=tk.StringVar()
release_var=tk.StringVar()

 
# defining a function that will
# get the artist and release and 
# print them on the screen
def submit():

    artist=artist_var.get()
    release=release_var.get()
    
    print("The artist is : " + artist)
    print("The release is : " + release)
    
    artist_var.set("")
    release_var.set("")
    
    
# creating a label for 
# artist using widget Label
artist_label = tk.Label(root, text = 'artist', font=('calibre',10, 'bold'))
 
# creating a entry for input
# artist using widget Entry
artist_entry = tk.Entry(root,textvariable = artist_var, font=('calibre',10,'normal'))
 
# creating a label for release
release_label = tk.Label(root, text = 'release', font = ('calibre',10,'bold'))
 
# creating a entry for release
release_entry=tk.Entry(root, textvariable = release_var, font = ('calibre',10,'normal'))
 
# creating a button using the widget 
# Button that will call the submit function 
sub_btn=tk.Button(root,text = 'Submit', command = submit)
 
# placing the label and entry in
# the required position using grid
# method
artist_label.grid(row=0,column=0)
artist_entry.grid(row=0,column=1)
release_label.grid(row=1,column=0)
release_entry.grid(row=1,column=1)
sub_btn.grid(row=2,column=1)
 
# performing an infinite loop 
# for the window to display
root.mainloop()