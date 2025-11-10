# another one of the classes I dont quite know what to do with

class artist(name, id, releases): # might need different variables maybe

    # need a proper .self thing here

    # table is always artists here
    # need to make sure artists table exists too
    def add_to_release (field, value): # value here is the actual data we want to add
        try:
            with sqlite3.connect("MusicDB.db") as conn:
                print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
                cursor = conn.cursor()
                # need to check if the value already exists first
                result = cursor.execute(f"""SELECT * FROM artists
                                        WHERE {field}=?""",(value,)).fetchone()
                
                if result: # if a thing already exists
                    print("value already exists")
                
                else: # if a thing doesn't exist
                    cursor.execute(f"""INSERT INTO artists ({field})
                                    VALUES ('{value}')""") 
                    print("added data successfully") # succes message for testing
                    conn.commit


        except sqlite3.OperationalError as e:
            print("Failed to open database:", e)

    # test_field = urllib.parse.quote('UserName')
    # test_value = urllib.parse.quote('slime')

    # add_to_artists(test_field, test_value)
