import sqlite3


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.cur = self.conn.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS sites (id INTEGER PRIMARY KEY, url TEXT, last_visited INTEGER, score INTEGER)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS contents (id INTEGER PRIMARY KEY, site_id INTEGER, contents TEXT, score INTEGER)")

        self.conn.commit()

    def new_site(self, url: str, last_visited: int, score: int):
        self.cur.execute("INSERT INTO sites (url, last_visited, score) VALUES (?, ?, ?)", (url, last_visited, score))
        self.conn.commit()
    
    def new_contents(self, site_id: int, contents: str, score: int):
        self.cur.execute("INSERT INTO contents (site_id, contents, score) VALUES (?, ?, ?)", (site_id, contents, score))
        self.conn.commit()
    


    def get_sites(self, url:str=None, id:int=None):
        if id is not None:
            self.cur.execute("SELECT * FROM sites WHERE id=?", (id,))

        elif url is not None:
            self.cur.execute("SELECT * FROM sites WHERE url=?", (url,))

        else:
            self.cur.execute("SELECT * FROM sites")

        return self.cur.fetchall()
    

    


    def __del__(self):
        self.conn.close()