import sqlite3

from flask import Flask, render_template, request, session
from flask_session import Session

app = Flask("Flask - Lab")

# Tworzenie obsługi sesji
sess = Session()

# Ścieżka do pliku bazy danych w sqlite
DATABASE = 'database.db'


@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE IF NOT EXISTS books (title TEXT, author TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, UNIQUE(username));')
    conn.execute("INSERT INTO users (username, password) VALUES('admin', 'admin')")
    # Zakończenie połączenia z bazą danych
    conn.close()

    return index()


@app.route('/', methods=['GET', 'POST'])
def index():
    con = sqlite3.connect(DATABASE)

    # Pobranie danych z tabeli
    cur = con.cursor()
    cur.execute("select * from books")
    books = cur.fetchall()

    if 'user' in session:
        return render_template('loggedIndex.html', books=books)
    return render_template('login.html', books=books)


@app.route('/addBook', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']

    # Dodanie użytkownika do bazy danych
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO books (title, author) VALUES (?,?)", (title, author))
    con.commit()
    con.close()

    return "Dodano książkę do bazy danych <br>" + index()


@app.route('/login', methods=['POST'])
def login():
    username = request.form['login']
    password = request.form['password']

    # Dodanie użytkownika do bazy danych
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    #cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchall()

    if user:
        session['user'] = "username"

    return index()


@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji
    if 'user' in session:
        session.pop('user')
    return index()


app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()
