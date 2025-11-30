from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = 'my_goals_secret_2024'


def init_db():
    conn = sqlite3.connect('goals.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            created_at TEXT,
            is_completed INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


init_db()


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/goals')
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('goals.db')
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            session['user_id'] = user[0]
            session['username'] = username

            conn.close()
            return redirect('/goals')

        except:
            conn.close()
            return "Ошибка: Имя пользователя уже занято"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('goals.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/goals')
        else:
            return "Неверные данные для входа"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/goals')
def goals():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('goals.db')
    c = conn.cursor()
    c.execute('SELECT id, title, description, created_at, is_completed FROM goals WHERE user_id = ?',
              (session['user_id'],))
    goals_list = c.fetchall()
    conn.close()

    return render_template('goals.html', goals=goals_list, username=session['username'])


@app.route('/add_goal', methods=['POST'])
def add_goal():
    if 'user_id' not in session:
        return redirect('/login')

    title = request.form['title']
    description = request.form['description']

    conn = sqlite3.connect('goals.db')
    c = conn.cursor()
    c.execute('INSERT INTO goals (user_id, title, description, created_at) VALUES (?, ?, ?, ?)',
              (session['user_id'], title, description, datetime.now().strftime("%d.%m.%Y")))
    conn.commit()
    conn.close()

    return redirect('/goals')


@app.route('/delete_goal/<int:goal_id>')
def delete_goal(goal_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('goals.db')
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, session['user_id']))
    conn.commit()
    conn.close()

    return redirect('/goals')




@app.route('/complete_goal/<int:goal_id>')
def complete_goal(goal_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('goals.db')
    c = conn.cursor()
    c.execute("UPDATE goals SET is_completed = 1 WHERE id = ? AND user_id = ?", (goal_id, session['user_id']))
    conn.commit()
    conn.close()

    return redirect('/goals')


if __name__ == '__main__':
    app.run(debug=True)