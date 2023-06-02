import sqlite3
import os
from flask import Flask, render_template, session, make_response, request, redirect, url_for
conn = sqlite3.connect('super_quiz.db')
cursor = conn.cursor()

folder = os.getcwd()

cursor.execute('''CREATE TABLE IF NOT EXISTS quiz(
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    age_from INTEGER,
    age_to INTEGER)''')

#cursor.execute('''DROP TABLE IF EXISTS quiz''')

cursor.execute('''CREATE TABLE IF NOT EXISTS question(
    id INTEGER PRIMARY KEY,
    question VARCHAR,
    answer VARCHAR,
    wrong1 VARCHAR,
    wrong2 VARCHAR,
    wrong3 VARCHAR)''')


cursor.execute('''CREATE TABLE IF NOT EXISTS quiz_content(
    id INTEGER PRIMARY KEY,
    quiz_id INTEGER,
    question_id INTEGER, 
    FOREIGN KEY (quiz_id) REFERENCES quiz(id),
    FOREIGN KEY (question_id) REFERENCES question(id))''')

list_q = [
    ('Сколько месяцев в году имеют 28 дней?',
    'Все', 'Один', 'Ни одного', 'Два'),
    ('Чему равно число Пи?',
    'Примерно 3.14', '3', '0', 'Ровно 3.14'),
    ('Сколько костей в теле человека?', 
    '206', '204', '201' , '205'),
    ('Сколько градусов в круге?',
    '360', '90', '180', '270')
]

cursor.executemany('''INSERT INTO question
(question, answer, wrong1, wrong2, wrong3)
VALUES (?, ?, ?, ?, ?)''', list_q)

list_qu = [
    ('Викторина1', 7, 14),
    ('Викторина2', 15, 20)
]

cursor.executemany('''INSERT INTO quiz
(name, age_from, age_to) VALUES (?, ?, ?)''', list_qu)

list_id = [
    (1, 1),
    (2, 2),
    (1, 3),
    (2, 4)
]

cursor.executemany('''INSERT INTO quiz_content
(quiz_id, question_id) VALUES (?, ?)''', list_id)



cursor.execute('''SELECT quiz.name, quiz.age_from, quiz.age_to, quiz_content.id, question.question, question.answer   
FROM quiz_content, question, quiz 
WHERE quiz_content.question_id = question.id AND quiz_content.quiz_id = quiz.id AND quiz.id = 1''')

cursor.execute('''SELECT * 
FROM quiz''')
quizes = cursor.fetchall()
#conn.commit()

def index():
    # res = "<h1>Список викторин</h1>"
    # res += "<ol>"
    # for i in result:
    #     res += "<li><a href = '/quiz'>" + str(i[1]) + "</a></li>"
    # res += "</ol>"

    # if 'counter' in session:
    #     session['counter'] +=1
    # else:
    #     session['counter'] = 0
    resp = make_response(render_template('index.html', quizes = quizes, session=session))
    resp.set_cookie('somecookienname', 'i')
    return resp
    #return render_template('index.html', result = result, session=session)

def quiz():
    quiz_id = request.args.get('id')
    conn = sqlite3.connect('super_quiz.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT question.*   
FROM quiz_content, question, quiz 
WHERE quiz_content.question_id = question.id AND quiz_content.quiz_id = quiz.id AND quiz.id = ?''', quiz_id)
    questions = cursor.fetchall()
    if request.method == 'GET':
        counter = session.get(f'counter{quiz_id}', 0)
        if counter >= len(questions):
            counter = 0
        resp = make_response(render_template('index1.html', quiz_id = quiz_id, question = questions[counter]))
        #print(questions[counter])
        return resp
    elif request.method == 'POST':
        counter = session.get(f'counter{quiz_id}', 0)
        score = session.get(f'score{quiz_id}', 0)
        right_answer = questions[counter][2]
        answer = request.form.get('answer')
        if right_answer == answer:
            score += 1
        counter += 1
        session[f'counter{quiz_id}'] = counter
        session[f'score{quiz_id}'] = score
        if counter >= len(questions):
            del session[f'counter{quiz_id}']
            return redirect(f'/result?id={quiz_id}')
        else:
            return redirect(f'/quiz?id={quiz_id}')

def result():
    quiz_id = request.args.get('id')
    score = session.pop(f'score{quiz_id}', 0)
    resp = make_response(render_template('result.html', quiz_id = quiz_id, score = score))
    return resp

app = Flask(__name__, template_folder=folder, static_folder=folder)
app.config['SECRET_KEY'] = 'VeryStrongKey'
app.add_url_rule('/', 'index', index, methods = ['POST', 'GET'])
app.add_url_rule('/quiz', 'quiz', quiz, methods = ['POST', 'GET'])
app.add_url_rule('/result', 'result', result, methods = ['POST', 'GET'])
app.run()