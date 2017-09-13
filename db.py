import sqlite3

def init_db():
	sqlite_db_path = './links.sqlite'
	conn = sqlite3.connect(sqlite_db_path)
	sql = conn.cursor()
	sql.execute('CREATE TABLE IF NOT EXISTS links (id INTEGER PRIMARY KEY, url VARCHAR(255), filename VARCHAR(255), UNIQUE (url, filename) ON CONFLICT IGNORE)')
	sql.execute('CREATE TABLE IF NOT EXISTS checks (id INTEGER PRIMARY KEY, datetime DATETIME, result VARCHAR(255), link INTEGER, FOREIGN KEY(link) REFERENCES links(id))')	
	return (conn, sql)

if __name__ == '__main__':
	conn, sql = init_db()
	conn.commit()
	conn.close()
