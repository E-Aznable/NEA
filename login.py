# not quite sure how to lay this all out yet
# i think login should be it's own file
# basically just take a user login or make a new one
# and return the id to main

import urllib.parse
import urllib.request
import json
import sqlite3
import os.path

# need to import a list of usernames and passwords

class login_system:
    def __init__(self):
        pass

    def register(self):
        happy = False
        while not happy:
            new_name = input("new name: ")
            confirm_pass = 1
            new_pass = -1
            while new_pass != confirm_pass:
                print("please enter and confirm password")
                new_pass = input("new password: ")
                confirm_pass = input("confirm password: ")
            while True:
                user_happy = input(f"are you happy with this username: -{new_name}- and this password: -{new_pass}- ? Yes/No: ")
                if user_happy.lower() in ["y", "yes"]:
                    print("cool")
                    happy = True
                    break
                elif user_happy.lower() in ["n", "no"]:
                    print("try again then")
                    break
                else:
                    print("invalid input")
            
        # add username and password to table + ID is generated automatically
        self.fields = ["UserName", "UserPass"]
        self.values = [new_name, new_pass]

    # add to table seperately
    def add_to_users (self): # value here is the actual data we want to add
        try:
            with sqlite3.connect("MusicDB.db") as conn:
                print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
                cursor = conn.cursor()
                # need to check if the value already exists first
                result = cursor.execute(f"""SELECT * FROM users
                                        WHERE {self.fields[0]}=?""",(self.values[0],)).fetchone()
                    
                if result: # if a thing already exists
                    print("value already exists")
                    
                else: # if a thing doesn't exist
                    cursor.execute(f"""INSERT INTO users ({self.fields[0]}, {self.fields[1]})
                                    VALUES ('{self.values[0]}', '{self.values[1]}')""")
                    print("added data successfully") # succes message for testing
                    conn.commit

        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)
                
        
    def login(self):
        print("login is case sensitive")
        input_name = input("enter username: ")
        input_pass = input("input password: ")
        # if input_name in usernames[] and input_pass in passwords[]:
        #     print("nice")
        # else:
        #     print("bad")
        try: # this section could be done at the top of the class but is only actually necessary here to check
            with sqlite3.connect("MusicDB.db") as conn:
                print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
                cursor = conn.cursor()
                # check for values and assign a local list
                cursor = conn.cursor()
                cursor.execute('SELECT UserID, UserName, UserPass FROM users')
                rows = cursor.fetchall()

                self.IDs = []
                self.usernames = []
                self.passwords = []

                for row in rows:
                    print(row[0], row[1], row[2])
                    self.IDs.append(row[0])
                    self.usernames.append(row[1])
                    self.passwords.append(row[2])

        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)

        success = False
        for i in range(len(self.usernames)):
            if input_name in self.usernames[i] and input_pass in self.passwords[i]:
                print("login recognised")
                success = True
                break
        if not success:
            print("username or password not recognised")


    def choose(self):
        choice = input("enter n for new user or e for exsisting user: ")
        if choice == 'n':
            self.register()
            self.add_to_users()
        if choice == 'e':
            self.login()

obj = login_system()
obj.choose()
