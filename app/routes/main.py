from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app.utils.pdf_utils import extract_questions_from_pdf, extract_questions_from_text
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.models.score import Score
from app import db
import random
from sqlalchemy import func
from app.models.user import User

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    recent_quizzes = (
        Quiz.query
        .join(User, Quiz.user_id == User.id)
        .filter(Quiz.is_public == True)
        .order_by(Quiz.created_at.desc())
        .limit(6)
        .all()
    )

    subquery = (
        db.session.query(Score.quiz_id, func.count(Score.id).label('attempt_count'))
        .group_by(Score.quiz_id)
        .subquery()
    )

    popular_quizzes_query = (
        Quiz.query
        .join(User, Quiz.user_id == User.id)
        .outerjoin(subquery, Quiz.id == subquery.c.quiz_id)
        .filter(Quiz.is_public == True)
        .order_by(func.coalesce(subquery.c.attempt_count, 0).desc())
        .limit(6)
    )
    
    popular_quizzes_results = popular_quizzes_query.all()

    return render_template('main/index.html',
                           recent_quizzes=recent_quizzes,
                           popular_quizzes=popular_quizzes_results)

@bp.route('/my-quizzes')
@login_required
def my_quizzes():
    quizzes = Quiz.get_by_user(current_user.id)
    return render_template('main/my_quizzes.html', quizzes=quizzes)

@bp.route('/create-quiz', methods=['GET', 'POST'])
@login_required
def create_quiz():
    if request.method == 'POST':
        import_type = request.form.get('import_type', 'manual')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')
        is_public = request.form.get('is_public') == 'on'

        if not title:
            flash("Le titre du quiz est obligatoire.", "error")
            return render_template('main/create_quiz.html')

        quiz = Quiz(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            is_public=is_public,
            user_id=current_user.id
        )
        db.session.add(quiz)
        db.session.flush()

        questions_data = []
        if import_type == 'text':
            text_content = request.form.get('text_content')
            delimiter = request.form.get('text_delimiter', '\n')
            if text_content:
                questions_data = extract_questions_from_text(text_content, delimiter)
            else:
                flash("Le contenu textuel est vide.", "warning")

        elif import_type == 'pdf':
            if 'pdf_file' not in request.files or not request.files['pdf_file'].filename:
                flash('Aucun fichier PDF sélectionné ou fichier vide.', 'error')
            else:
                pdf_file = request.files['pdf_file']
                if not pdf_file.filename.endswith('.pdf'):
                    flash('Le fichier doit être au format PDF.', 'error')
                else:
                    filename = secure_filename(pdf_file.filename)
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    temp_path = os.path.join(upload_folder, filename)
                    pdf_file.save(temp_path)
                    try:
                        questions_data = extract_questions_from_pdf(temp_path)
                    except Exception as e:
                        current_app.logger.error(f"Erreur extraction PDF: {e}")
                        flash("Erreur lors de l'extraction des questions du PDF.", "error")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        
        if questions_data:
            new_questions_to_add = []
            # D'abord, on crée tous les objets Question
            for q_data in questions_data:
                question = Question(
                    quiz_id=quiz.id,
                    text=q_data['question'],
                    points=q_data.get('points', 1) 
                )
                new_questions_to_add.append(question)
            
            # On ajoute toutes les nouvelles questions à la session en une fois
            if new_questions_to_add: # Vérifier si la liste n'est pas vide
                db.session.add_all(new_questions_to_add)
                # On flush pour obtenir les IDs des questions qui viennent d'être créées
                # Ces IDs sont nécessaires pour créer les objets Answer avec la bonne foreign key
                db.session.flush() 

            new_answers_to_add = []
            # new_questions_to_add contient maintenant les objets Question avec leurs IDs de la DB
            for i, question_obj in enumerate(new_questions_to_add):
                q_data = questions_data[i] # Récupérer les données originales correspondantes
                for ans_data in q_data.get('answers', []):
                    ans_text = ans_data
                    is_correct = False
                    if isinstance(ans_data, dict):
                        ans_text = ans_data.get('text', '')
                        is_correct = ans_data.get('is_correct', False)
                    elif isinstance(ans_data, str): # Si c'est juste une chaîne, on la prend comme texte
                        ans_text = ans_data
                    
                    answer = Answer(
                        question_id=question_obj.id, # Utiliser l'ID de l'objet Question de la DB
                        text=ans_text,
                        is_correct=is_correct
                    )
                    new_answers_to_add.append(answer)
            
            if new_answers_to_add:
                db.session.add_all(new_answers_to_add)
        
        # Un seul commit à la fin, que des questions aient été importées ou non
        db.session.commit()

        if import_type != 'manual': # Pour import texte ou PDF
            if questions_data:
                flash('Quiz et questions importées avec succès ! Vous pouvez maintenant les éditer.', 'success')
            else:
                # Si questions_data est vide après une tentative d'import, c'est peut-être que le fichier était vide ou l'extraction a échoué
                # Le message d'erreur spécifique sur l'extraction aura déjà été flashé.
                flash('Quiz créé. Aucune question n\'a pu être importée. Vous pouvez les ajouter manuellement.', 'warning')
        else: # Mode manuel
            flash('Quiz créé avec succès ! Ajoutez maintenant des questions.', 'success')
        
        return redirect(url_for('main.edit_questions', quiz_id=quiz.id))

    return render_template('main/create_quiz.html')

@bp.route('/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz:
        flash('Quiz non trouvé', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('main/view_quiz.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        flash('Quiz non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('main.my_quizzes'))

    if request.method == 'POST':
        quiz.title = request.form.get('title')
        quiz.description = request.form.get('description')
        quiz.category = request.form.get('category')
        quiz.difficulty = request.form.get('difficulty')
        quiz.is_public = request.form.get('is_public') == 'on'
        
        db.session.commit()
        flash('Quiz mis à jour avec succès !', 'success')
        return redirect(url_for('main.view_quiz', quiz_id=quiz.id))

    return render_template('main/edit_quiz.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        flash('Quiz non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('main.my_quizzes'))

    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz supprimé avec succès !', 'success')
    return redirect(url_for('main.my_quizzes'))

@bp.route('/quiz/<int:quiz_id>/edit-questions', methods=['GET', 'POST'])
@login_required
def edit_questions(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        flash('Quiz non trouvé ou accès non autorisé', 'error')
        return redirect(url_for('main.my_quizzes'))

    if request.method == 'POST':
        questions_data = request.form.to_dict()
        
        # Traiter les données du formulaire
        for question_id, data in questions_data.items():
            if question_id.startswith('questions[') and question_id.endswith('][text]'):
                # Extraire l'ID de la question
                q_id = question_id.split('[')[1].split(']')[0]
                
                # Mettre à jour ou créer la question
                if q_id.startswith('new_'):
                    question = Question(
                        quiz_id=quiz.id,
                        text=data,
                        points=1
                    )
                    db.session.add(question)
                    db.session.flush()
                else:
                    question = Question.get_by_id(int(q_id))
                    if question:
                        question.text = data

                # Mettre à jour les réponses
                answers_data = {k: v for k, v in questions_data.items() 
                              if k.startswith(f'questions[{q_id}][answers]')}
                correct_answer = questions_data.get(f'questions[{q_id}][correct_answer]')

                for answer_id, answer_text in answers_data.items():
                    a_id = answer_id.split('[')[-1].split(']')[0]
                    
                    if a_id.startswith('new_'):
                        answer = Answer(
                            question_id=question.id,
                            text=answer_text,
                            is_correct=(a_id == correct_answer)
                        )
                        db.session.add(answer)
                    else:
                        answer = Answer.get_by_id(int(a_id))
                        if answer:
                            answer.text = answer_text
                            answer.is_correct = (a_id == correct_answer)

        # Supprimer les questions et réponses qui ne sont plus présentes
        existing_questions = {str(q.id): q for q in quiz.questions}
        for q_id in list(existing_questions.keys()):
            if f'questions[{q_id}][text]' not in questions_data:
                db.session.delete(existing_questions[q_id])

        db.session.commit()
        flash('Questions mises à jour avec succès !', 'success')
        return redirect(url_for('main.view_quiz', quiz_id=quiz.id))

    return render_template('main/edit_questions.html', quiz=quiz)

@bp.route('/quiz/<int:quiz_id>/train', methods=['GET', 'POST'])
@login_required
def train_quiz(quiz_id):
    quiz = Quiz.get_by_id(quiz_id)
    if not quiz:
        flash('Quiz non trouvé', 'error')
        return redirect(url_for('main.index'))

    questions = list(quiz.questions)
    random.shuffle(questions)
    for q in questions:
        if hasattr(q, 'answers') and q.answers:
            ans_list = list(q.answers)
            random.shuffle(ans_list)
            q.answers_shuffled = ans_list
        else:
            q.answers_shuffled = []

    if request.method == 'POST':
        score_val = 0
        submitted_answers = request.form.to_dict()
        total_quiz_questions = len(questions)

        for q in questions:
            user_answer_id = submitted_answers.get(f'question_{q.id}')
            if user_answer_id:
                answer_obj = Answer.get_by_id(int(user_answer_id))
                if answer_obj and answer_obj.is_correct:
                    score_val += q.points

        score_record = Score(
            user_id=current_user.id,
            quiz_id=quiz.id,
            score=score_val,
            max_score=sum(q.points for q in questions),
            correct_answers=sum(1 for q in questions if Answer.get_by_id(int(submitted_answers.get(f'question_{q.id}', 0))) and Answer.get_by_id(int(submitted_answers.get(f'question_{q.id}',0))).is_correct ),
            total_questions=total_quiz_questions,
        )
        db.session.add(score_record)
        db.session.commit()

        return render_template('main/train_results.html', 
                             quiz=quiz, 
                             score=score_val, 
                             total_questions=total_quiz_questions,
                             submitted_answers=submitted_answers,
                             questions=questions)

    return render_template('main/train_quiz.html', quiz=quiz, questions=questions) 