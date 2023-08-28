import sqlite3
def dbComm(database):
    #database param should be string type, i.e. relative path to db
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    command = input(f"\nEnter your SQL command for {database}: ")
    while command.lower() != "exit":
        try:
            for row in cursor.execute(command):
                print(row)
            conn.commit()
        except:
            print("invalid request")
        command = input(f"\nEnter your SQL command for {database}: ")

class DB_Execute():
    def __init__(self,db):
        self.db = db
        self.conn=sqlite3.connect(self.db)
        self.cursor=self.conn.cursor()

    def select(self,command):
        try:
            self.cursor.execute(command)
            self.items=self.cursor.fetchall()
            print(self.items)
            self.conn.commit()
            return self.items
        except:
            print(f'The command {command} could not be executed, or it returned no result.')
            return None
    
    def other_com(self,command):
        try:
            self.cursor.execute(command)
            self.conn.commit()
            print(f"The command {command} has been executed.")
        except:
            print(f'The command {command} could not be executed.')
