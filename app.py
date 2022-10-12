import sqlite3

from flask import Flask, render_template, request, session
from flask_session import Session

app = Flask("FlaskBooks")

# Tworzenie obsługi sesji
sess = Session()

# Ścieżka do pliku bazy danych w sqlite
DATABASE = 'database.db'


@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    con = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    con.execute("CREATE TABLE IF NOT EXISTS books (title TEXT, author TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS users ("
                "id INTEGER NOT NULL PRIMARY KEY, "
                "username TEXT UNIQUE, "
                "password TEXT, "
                "administrator INTEGER)")
    con.execute("INSERT OR IGNORE INTO users (username, password, administrator) VALUES('admin', 'admin', TRUE)")
    con.commit()
    # Zakończenie połączenia z bazą danych
    con.close()

    return index()


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return render_template('login.html')

    con = sqlite3.connect(DATABASE)

    # Pobranie danych z tabeli
    cur = con.cursor()
    cur.execute("select * from books")
    books = cur.fetchall()

    if 'admin' in session:
        return render_template('adminIndex.html', books=books)
    return render_template('index.html', books=books)


@app.route('/addBook', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']

    # Dodanie book do bazy danych
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

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()

    if user:
        session['user'] = username
        if user[3]:
            session['admin'] = username

    return index()


@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji
    if 'user' in session:
        session.pop('user')
    if 'admin' in session:
        session.pop('admin')
    return index()


@app.route('/users', methods=['GET', 'POST'])
def users():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users")
    _users = cur.fetchall()

    return render_template('users.html', users=_users)


@app.route('/users/<username>', methods=['GET'])
def user_by_username(username):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    _user = cur.fetchone()

    return render_template('user.html', user=_user)


@app.route('/users/<int:get_id>', methods=['GET'])
def user_by_id(get_id):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (get_id,))
    _user = cur.fetchone()

    return render_template('user.html', user=_user)


@app.route('/addUser', methods=['POST'])
def add_user():
    login = request.form['login']
    password = request.form['password']
    admin = 'admin' in request.form
    # Dodanie użytkownika do bazy danych
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, administrator) VALUES (?,?,?)", (login, password, admin))
    con.commit()
    con.close()

    return "Dodano użytkownika do bazy danych <br>" + users()


app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.run()
