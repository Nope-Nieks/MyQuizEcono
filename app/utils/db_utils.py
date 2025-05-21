from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def get_user_by_id(user_id):
    with db.get_connection() as conn:
        cursor = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()

def get_user_by_username(username):
    with db.get_connection() as conn:
        cursor = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def create_user(username, email, password):
    with db.get_connection() as conn:
        password_hash = generate_password_hash(password)
        cursor = conn.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid

def verify_password(user, password):
    return check_password_hash(user['password_hash'], password)

def create_quiz(title, description, user_id, category=None, difficulty=None):
    with db.get_connection() as conn:
        cursor = conn.execute(
            '''INSERT INTO quizzes 
               (title, description, user_id, category, difficulty) 
               VALUES (?, ?, ?, ?, ?)''',
            (title, description, user_id, category, difficulty)
        )
        conn.commit()
        return cursor.lastrowid

def add_question(quiz_id, text, order, points=1):
    with db.get_connection() as conn:
        cursor = conn.execute(
            'INSERT INTO questions (quiz_id, text, order_num, points) VALUES (?, ?, ?, ?)',
            (quiz_id, text, order, points)
        )
        conn.commit()
        return cursor.lastrowid

def add_answer(question_id, text, is_correct, order):
    with db.get_connection() as conn:
        cursor = conn.execute(
            'INSERT INTO answers (question_id, text, is_correct, order_num) VALUES (?, ?, ?, ?)',
            (question_id, text, is_correct, order)
        )
        conn.commit()
        return cursor.lastrowid

def save_score(user_id, quiz_id, score, max_score, correct_answers, total_questions, time_taken=None):
    with db.get_connection() as conn:
        percentage = (score / max_score) * 100
        cursor = conn.execute(
            '''INSERT INTO scores 
               (user_id, quiz_id, score, max_score, percentage, correct_answers, total_questions, time_taken) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, quiz_id, score, max_score, percentage, correct_answers, total_questions, time_taken)
        )
        conn.commit()
        return cursor.lastrowid

def get_quiz_with_questions(quiz_id):
    with db.get_connection() as conn:
        # Récupérer le quiz
        quiz = conn.execute('SELECT * FROM quizzes WHERE id = ?', (quiz_id,)).fetchone()
        if not quiz:
            return None

        # Récupérer les questions
        questions = conn.execute(
            'SELECT * FROM questions WHERE quiz_id = ? ORDER BY order_num',
            (quiz_id,)
        ).fetchall()

        # Pour chaque question, récupérer les réponses
        for question in questions:
            question['answers'] = conn.execute(
                'SELECT * FROM answers WHERE question_id = ? ORDER BY order_num',
                (question['id'],)
            ).fetchall()

        quiz['questions'] = questions
        return quiz

def get_user_scores(user_id):
    with db.get_connection() as conn:
        return conn.execute(
            '''SELECT s.*, q.title as quiz_title 
               FROM scores s 
               JOIN quizzes q ON s.quiz_id = q.id 
               WHERE s.user_id = ? 
               ORDER BY s.date_attempted DESC''',
            (user_id,)
        ).fetchall()

def get_quiz_scores(quiz_id):
    with db.get_connection() as conn:
        return conn.execute(
            '''SELECT s.*, u.username 
               FROM scores s 
               JOIN users u ON s.user_id = u.id 
               WHERE s.quiz_id = ? 
               ORDER BY s.percentage DESC''',
            (quiz_id,)
        ).fetchall() 