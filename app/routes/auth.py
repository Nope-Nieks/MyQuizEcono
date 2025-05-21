from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('Tous les champs sont obligatoires.', 'error')
        elif password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
        elif User.get_by_username(username):
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
        elif User.get_by_email(email):
            flash('Cet email est déjà utilisé.', 'error')
        else:
            try:
                User.create_user(username, email, password)
                flash('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                # Log l'erreur e pour le debug
                current_app.logger.error(f"Erreur lors de l'inscription : {e}")
                flash('Une erreur est survenue lors de l\'inscription.', 'error')
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on' # 'on' si la case est cochée
        
        if not all([username, password]):
            flash('Veuillez remplir tous les champs.', 'error')
        else:
            user = User.get_by_username(username)
            if user and user.check_password(password):
                login_user(user, remember=remember)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.index'))
            else:
                flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index')) 