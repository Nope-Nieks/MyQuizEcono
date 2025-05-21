import os
import click
from flask.cli import AppGroup
from app import create_app, db
from app.models.user import User
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.utils.pdf_utils import extract_questions_from_pdf

# Crée un groupe de commandes pour la gestion des quiz
quiz_cli = AppGroup('quiz', help='Gérer les quiz.')
user_cli = AppGroup('user', help='Gérer les utilisateurs.')

@quiz_cli.command('import-pdf')
@click.argument('pdf_path')
@click.argument('title')
@click.argument('user_id', type=int)
@click.option('--description', default='', help='Description du quiz.')
@click.option('--category', default='Général', help='Catégorie du quiz.')
@click.option('--difficulty', default='Moyen', help='Difficulté du quiz.')
@click.option('--is-public', is_flag=True, default=False, help='Rendre le quiz public.')
def import_pdf_command(pdf_path, title, user_id, description, category, difficulty, is_public):
    "Importe un quiz depuis un PDF."
    app = create_app() # Crée une instance de l'application pour avoir le contexte
    with app.app_context(): # Pousse un contexte d'application
        user = User.query.get(user_id)
        if not user:
            click.echo(f"Erreur : Utilisateur avec ID {user_id} non trouvé.")
            return

        if not os.path.exists(pdf_path):
            click.echo(f"Erreur : Fichier PDF {pdf_path} non trouvé.")
            return

        click.echo(f"Importation du quiz '{title}' à partir de {pdf_path} pour l'utilisateur {user.username}...")

        try:
            # Créer le quiz
            quiz = Quiz(
                title=title,
                description=description,
                category=category,
                difficulty=difficulty,
                is_public=is_public,
                user_id=user.id
            )
            db.session.add(quiz)
            db.session.flush()  # Pour obtenir l'ID du quiz pour les questions

            # Extraire les questions du PDF
            questions_data = extract_questions_from_pdf(pdf_path)
            

            if not questions_data:
                click.echo("Avertissement : Aucune question n'a été extraite du PDF.")
                # On commite quand même le quiz vide
                db.session.commit()
                click.echo(f'Quiz "{title}" créé sans questions.')
                return
            

            if questions_data:
                click.echo(f"Nombre de questions extraites : {len(questions_data)}")
                

            new_questions_to_add = []
            for q_data in questions_data:
                question = Question(
                    quiz_id=quiz.id,
                    text=q_data['text'],
                    points=q_data.get('points', 1)
                )
                new_questions_to_add.append(question)
            
            if new_questions_to_add:
                db.session.add_all(new_questions_to_add)
                db.session.flush()

            new_answers_to_add = []
            for i, question_obj in enumerate(new_questions_to_add):
                q_data = questions_data[i]
                for ans_data in q_data.get('answers', []):
                    ans_text = ans_data
                    is_correct = False
                    if isinstance(ans_data, dict):
                        ans_text = ans_data.get('text', '')
                        is_correct = ans_data.get('is_correct', False)
                    elif isinstance(ans_data, str):
                        ans_text = ans_data
                    
                    answer = Answer(
                        question_id=question_obj.id,
                        text=ans_text,
                        is_correct=is_correct
                    )
                    new_answers_to_add.append(answer)
            
            if new_answers_to_add:
                db.session.add_all(new_answers_to_add)

            db.session.commit()
            click.echo(f'Quiz "{title}" et {len(new_questions_to_add)} questions importées avec succès !')

        except Exception as e:
            db.session.rollback() # Annuler les changements en cas d'erreur
            click.echo(f"Erreur lors de l'importation du quiz : {e}")
            import traceback
            traceback.print_exc()

@user_cli.command('create-user')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_user_command(username, email, password):
    """Créer un nouvel utilisateur."""
    app = create_app()
    with app.app_context():
        if User.query.filter_by(username=username).first():
            click.echo(f"Erreur : Le nom d'utilisateur '{username}' existe déjà.")
            return
        if User.query.filter_by(email=email).first():
            click.echo(f"Erreur : L'email '{email}' existe déjà.")
            return
        
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            click.echo(f"Utilisateur '{username}' (ID: {new_user.id}) créé avec succès !")
        except Exception as e:
            db.session.rollback()
            click.echo(f"Erreur lors de la création de l'utilisateur : {e}")
            import traceback
            traceback.print_exc()

def register_commands(app):
    app.cli.add_command(quiz_cli)
    app.cli.add_command(user_cli) 