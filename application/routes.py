# Instances
from application import app  # Import the Flask instance
from application import db  # Import the database instance
from application import bcrypt  # Import the bcrypt instance
from application import serializer  # Import the URLSafeTimedSerializer instance
from application import mail  # Import the mail instance

# Models
from application.models import PreUser # Importing the PreUser table of the database
from application.models import User  # Importing the User table of the database
from application.models import Kid  # Importing the Kid table of the database
from application.models import Deck  # Importing the Deck table of the database
from application.models import Card # Importing the Card table of the database

# Libraries
from flask import redirect, render_template # Importing render_template to render HTML files within the "Templates" folder.
from flask import url_for # Importing 'url_for' to dynamically build URL for a specific function and images.
from flask import request  # Importing 'request' to handle requests.
from flask import flash  # Importing 'flash' to show messages/alerts.
from flask import session  # Importing 'session' to manage user sessions.
from flask import send_file # Importing 'send_files' to send images and files.
from flask import jsonify # Importing 'jsonify' to turn HTML into JSON responses.
from itsdangerous import SignatureExpired # Importing 'SignatureExpired' to catch when the email confirmation is expired.
from flask_mail import Message # Importing 'Message' to send include messages in the email.
from functools import wraps  # Importing 'wraps' to create decorated functions.
import os # Importing 'os' to manage the file system

# Decorated functions

## Restrict access to signin-only pages
def signin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        logged = session.get('logged')
        if not logged:
            flash("Você não está autenticado, faça login para acessar esta página.")
            return redirect(url_for('sign_in'))
        return func(*args, **kwargs)
    return decorated_function

# Helpful functions

## Get the current user
def get_current_user():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    return user

## Generate filename based on the highest number in the directory
def generate_filename(media_path):
    all_files = os.listdir(media_path)
    highest_integer = 0
    for file in all_files:
        dot = file.index('.')
        number = int(file[:dot])
        if number > highest_integer:
            highest_integer = number
    filename = highest_integer + 1
    return filename

## Restrict user access
def user_access(current_user, allowed_username):
    if current_user.username != allowed_username:
        return False
    return True

# DEBUG: Reset the database
@app.route('/drop-all')
def drop_all():
    db.drop_all()
    db.create_all()
    return redirect(url_for('homepage'))

# Securely save files
@app.route('/static/media/<username>/<filename>')
def image(username, filename):
    print(f'Username: {username}')
    print(f'Filename: {filename}')
    current_user = get_current_user()
    if not current_user:
        flash('Não tens accesso a este ficheiro, tenta fazer login.')
        return redirect(url_for('sign_in'))
    if username == current_user.username:
        path = f'static/media/{username}/{filename}'
        return send_file(path, mimetype='image/png')
    return '403 - Access Denied'

# Homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

# Sign Up
@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        # Compare both passwords
        if password != confirm_password:
            flash("As palavras-passes não correspondem, tente novamente.")
            return redirect(url_for('sign_up'))
        # Checking if pre_user already exists - NEEDS IMPROVEMENT!
        pre_user_already_exists_using_email = PreUser.query.filter_by(email=email).first()
        if pre_user_already_exists_using_email:
            hashed_password = bcrypt.generate_password_hash(password)
            pre_user_already_exists_using_email.username = username
            pre_user_already_exists_using_email.email = email
            pre_user_already_exists_using_email.password = hashed_password
            db.session.commit()
            token = serializer.dumps(email, salt='email-confirm')
            #msg = Message('AACProject - Email Confirmation', sender='librarymsoftware@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            #msg.body = f'Hello @{username}, 👋 \n\n Kindly click on the following link to activate your account: {link} \n\n Best regards, \n AACProject Team'
            # mail.send(msg)
            flash(
                f'Sua conta foi criada com sucesso, um e-mail de confirmação foi enviado para {email}. Por favor, confirme antes de continuar. DEBUG: {link}')
            return redirect(url_for('sign_up'))
        
        pre_user_already_exists_using_username = PreUser.query.filter_by(username=username).first()
        if pre_user_already_exists_using_username:
            hashed_password = bcrypt.generate_password_hash(password)
            pre_user_already_exists_using_username.username = username
            pre_user_already_exists_using_username.email = email
            pre_user_already_exists_using_username.password = hashed_password
            db.session.commit()
            token = serializer.dumps(email, salt='email-confirm')
            #msg = Message('AACProject - Email Confirmation', sender='librarymsoftware@gmail.com', recipients=[email])
            link = url_for('confirm_email', token=token, _external=True)
            #msg.body = f'Hello @{username}, 👋 \n\n Kindly click on the following link to activate your account: {link} \n\n Best regards, \n AACProject Team'
            # mail.send(msg)
            flash(
                f'Sua conta foi criada com sucesso, um e-mail de confirmação foi enviado para {email}. Por favor, confirme antes de continuar. DEBUG: {link}')
            return redirect(url_for('sign_up'))
        # Checking if user already exists
        email_is_already_being_used = User.query.filter_by(email=email).first()
        if email_is_already_being_used:
            flash('Este e-mail já está a ser usado, tente usar um diferente.')
            return redirect(url_for('sign_up'))
        
        username_is_already_being_used = User.query.filter_by(username=username).first()
        if username_is_already_being_used:
            flash('Este username já está a ser usado, tente usar um diferente.')
            return redirect(url_for('sign_up'))
        # Database submission
        # Generate a hashed password for security reasons.
        hashed_password = bcrypt.generate_password_hash(password)
        pre_user = PreUser(username=username, email=email,
                           password=hashed_password)
        db.session.add(pre_user)
        db.session.commit()
        # Generating the email confirmation
        token = serializer.dumps(email, salt='email-confirm')
        #msg = Message('AACProject - Email Confirmation', sender='librarymsoftware@gmail.com', recipients=[email])
        link = url_for('confirm_email', token=token, _external=True)
        #msg.body = f'Hello @{username}, 👋 \n\n Kindly click on the following link to activate your account: {link} \n\n Best regards, \n AACProject Team'
        # mail.send(msg)
        flash(
            f'A sua conta foi criada com sucesso, um e-mail de confirmação foi enviado para {email}. Por favor, confirme antes de continuar. DEBUG: {link}')
        return redirect(url_for('sign_up'))
    return render_template('sign-up.html')

# Email confirmation
@app.route('/confirm-email/<token>')
def confirm_email(token):
    # Check if token has expired
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=1800)
    except SignatureExpired:
        flash('Sua confirmação de e-mail já expirou, tente novamente.')
        return redirect(url_for('sign_up'))
    # Adding the pre_user to the User table
    pre_user = PreUser.query.filter_by(email=email).first()
    user = User(username=pre_user.username,
                email=pre_user.email, password=pre_user.password)
    db.session.add(user)
    db.session.commit()
    # Deleting the pre_user
    db.session.delete(pre_user)
    db.session.commit()
    # Creating a directory to store the user's files safely
    os.mkdir(f'application/static/media/{user.username}')
    flash('O seu e-mail foi confirmado com sucesso, agora já pode fazer acessar á sua conta.')
    return redirect(url_for('sign_in'))

# Forgot password
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Form data
        email = request.form.get('email')
        # Check if e-mail is valid
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(
                "O e-mail inserido não corresponde com nenhum utilizador, verifique novamente e tente de novo.")
            return redirect(url_for('forgot_password'))
        # Generate e-mail to recover password
        token = serializer.dumps(email, salt='recover-password')
        #msg = Message('AACProject - Recover Password', sender='librarymsoftware@gmail.com', recipients=[email])
        link = url_for('change_password', token=token, _external=True)
        #msg.body = f'Hello {user.username}, 👋 \n\n Kindly click on the following link to recover your password: {link} \n\n Best regards, \n AACProject Team'
        # mail.send(msg)
        flash(
            f'Um e-mail foi lhe enviado, com mais detalhes para a recuperação da senha. DEBUG: {link}')
        return redirect(url_for('forgot_password'))
    return render_template('forgot-password.html')

# Change password
@app.route('/change-password/<token>', methods=['GET', 'POST'])
def change_password(token):
    if request.method == 'POST':
        # Check if token has expired
        try:
            email = serializer.loads(
                token, salt='recover-password', max_age=1800)
        except SignatureExpired:
            flash('A recuperação da sua senha já expirou, tente novamente.')
            return redirect(url_for('forgot_password'))
        # Form data
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        # Compare both passwords
        if password != confirm_password:
            flash("As palavras-passes não correspondem, tente novamente.")
            return redirect(url_for('change_password', token=token))
        # Change the password
        user = User.query.filter_by(email=email).first()
        # Generate a hashed password for security reasons.
        hashed_password = bcrypt.generate_password_hash(password)
        user.password = hashed_password
        db.session.commit()
        flash('A sua palavra-passe foi alterada com sucesso!')
        return redirect(url_for('sign_in'))
    return render_template('change-password.html')

# Sign In
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        # Form data
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = False
        if request.form.get('rememberMe'):
            remember_me = True
        # Login the user
        user = User.query.filter_by(email=email).first()
        # Check if user does not exist
        if not user:
            flash(f'Nenhum utilizador foi encontrado com o e-mail {email}')
            return redirect(url_for('sign_in'))
        # Checking the password and loginin the user using sessions
        if bcrypt.check_password_hash(user.password, password):
            session.permanent = remember_me
            session['logged'] = True
            session['username'] = user.username
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        flash("O e-mail e a palavra-passe não correspondem, verifique novamente e tente de novo.")
        return redirect(url_for('sign_in'))
    return render_template('sign-in.html')

# Sign Out
@app.route('/sign-out', methods=['GET', 'POST'])
def sign_out():
    # Remove data from session
    keys = []
    for key in session.keys():
        keys.append(key)

    for key in keys:
        session.pop(key, None)
    return redirect(url_for('homepage'))

# Account Configuration
@app.route('/account-configuration/<username>/<action>', methods=['GET', 'POST'])
def account_configuration(username, action):
    # Querying for the current user
    current_user = get_current_user()
    # Section for changing the 'password'
    if action == 'change_password':
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        if password != confirm_password:
            flash('As palavras-passes não correspondem, tente novamente.')
            return redirect(url_for('dashboard'))
        # Generating an hashed password and redinifing it
        hashed_password = bcrypt.generate_password_hash(password)
        current_user.password = hashed_password
        db.session.commit()
        flash('A palavra-passe foi redefinida com successo!')
        return redirect(url_for('dashboard'))
    # Section for chaning the 'e-mail'
    if action == 'change_email':
        email = request.form.get('email')
        # Check if email already exists
        email_already_exists = User.query.filter_by(email=email).first()
        if email_already_exists:
            flash('Esse e-mail já está a ser usado, tente utilizar outro.')
            return redirect(url_for('dashboard'))
        # Generate e-mail to recover password
        token = serializer.dumps(email, salt='change-email')
        #msg = Message('AACProject - Recover Password', sender='librarymsoftware@gmail.com', recipients=[email])
        link = url_for('confirm_change_email', token=token, username = username, _external=True)
        #msg.body = f'Hello {user.username}, 👋 \n\n Kindly click on the following link to recover your password: {link} \n\n Best regards, \n AACProject Team'
        # mail.send(msg)

        # /confirm-email-change/<username>/<new_email_token>
        # Change in other app_route
        flash(f'Um e-mail foi lhe enviado, com mais detalhes para a redefinição do seu email. DEBUG: {link}')
        return redirect(url_for('dashboard'))
    return 'Cool!'

# Confirm Change Email
@app.route('/confirm-email-change/<username>/<token>', methods=['GET', 'POST'])
def confirm_change_email(username, token):
    user = get_current_user()
    # Check if token is already expired
    try:
        new_email = serializer.loads(
            token, salt='change-email', max_age=1800)
    except SignatureExpired:
        flash('A redefinição do seu email já expirou, tente novamente.')
        return redirect(url_for('dashboard'))
    #Redefining the email and updating the session
    user.email = new_email
    db.session.commit()
    session['email'] = new_email
    flash(f'O seu e-mail foi redefinido com successo para {new_email}')
    return redirect(url_for('dashboard'))
    
# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@signin_required
def dashboard():
    user = get_current_user()
    if request.method == 'POST':
        kid_name = request.form.get('kidName')
        kid_image = request.files['kidImage']
        # Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        # Save the image in the user's directory
        media_file = f'{media_path}/{filename}.png'
        kid_image.save(media_file)
        image_path = f'static/media/{user.username}/{filename}.png' # Needs to be slightly changed to be rendered in the HTML
        # Add the kid to the database
        kid = Kid(name = kid_name, image_path = image_path, user = user, card_size = 4)
        db.session.add(kid)
        db.session.commit()
        flash(f'O/a {kid.name} foi adicionado/a com successo!')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', page_name='Painel', user=user)

# Dashboard Actions
@app.route('/dashboard-actions/<action>/<kid_id>', methods=['GET', 'POST'])
@signin_required
def dashboard_actions(action, kid_id):
    user = get_current_user()
    kid = Kid.query.filter_by(id=kid_id).first()
    print(kid.name)
    # Section to change the kid's name
    if action == 'change_name':
        new_name = request.form.get('newName')
        kid.name = new_name
        db.session.commit()
        flash(f'O nome foi alterado com successo para {kid.name}.')
        return redirect(url_for('dashboard'))
    # Section to change the kid's image
    if action == 'change_image':
        new_image = request.files['newImage']
        # Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        # Save the image in the user's directory
        media_file = f'{media_path}/{filename}.png'
        new_image.save(media_file)
        image_path = f'static/media/{user.username}/{filename}.png' # Needs to be slightly changed to be rendered in the HTML
        # Change the image path
        kid.image_path = image_path
        db.session.commit()
        flash(f'A imagem foi alterada com successo.')
        return redirect(url_for('dashboard'))
    # Section to delete the kid's dashboard
    if action == 'delete_kid':
        password = request.form.get('passwordConfirmation')
        # Checking the password and loginin the user using sessions
        if bcrypt.check_password_hash(user.password, password):
            db.session.delete(kid)
            db.session.commit()
            flash(f'O painel de {kid.name} foi eliminado com successo.')
            return redirect(url_for('dashboard'))
        flash(f'A palavra-passe não corresponde, o painel de {kid.name} não foi eliminado.')
        return redirect(url_for('dashboard'))

# Kid's Dashboard
@app.route('/dashboard/<username>/<kid_id>/<action>', methods=['POST', 'GET'])
@signin_required
def kid_dashboard(username, kid_id, action):
    user = get_current_user()
    # Restrict user access
    access = user_access(user, username)
    if not access:
        flash('Não tens accesso a esta página, tenta fazer login.')
        return redirect(url_for('sign_in'))
    # Query for the kid
    kid = Kid.query.filter_by(id=kid_id).first()
    # Section to add a new deck
    if action == 'add_deck':
        # Form data
        deck_name = request.form.get('deckName')
        deck_image = request.files['deckImage']
        # Check if deck already exists
        deck_already_exists = Deck.query.filter_by(name=deck_name, kid_id = kid.id).first()
        if deck_already_exists:
            flash(f'Já existe um baralho com o nome "{deck_name}", tente escolher um nome diferente.')
            return redirect(url_for('kid_dashboard', username = username, kid_id = kid_id, action = 'view'))
        # Storing the image
        ## Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        ## Save the image in the user's directory
        media_file = f'{media_path}/{filename}.png'
        deck_image.save(media_file)
        image_path = f'static/media/{user.username}/{filename}.png' # Needs to be slightly changed to be rendered in the HTML
        # Add the deck
        deck = Deck(name = deck_name, kid = kid, image_path = image_path)
        db.session.add(deck)
        db.session.commit()
        flash(f'O baralho {deck.name} foi adicionado com successo.')
        return redirect(url_for('kid_dashboard', username = username, kid_id = kid.id, action = 'view'))
    # Section to change the card size
    if action == 'change_card_size':
        # Form data
        card_size = request.form.get('cardSize')
        # Update the card size
        kid.card_size = int(card_size)
        db.session.commit()
        flash(f'O tamanho das cartas foi atualizado com successo.')
        return redirect(url_for('kid_dashboard', username = username, kid_id = kid.id, action = 'view'))

    # Section for rendering the page
    if action == 'view':
        return render_template('kid-dashboard.html', kid = kid, page_name=f'Painel de {kid.name}', user = user)

# Kid Dashboard Actions
@app.route('/kid-dashboard-actions/<action>/<kid_id>/<deck_id>', methods=['GET', 'POST'])
@signin_required
def kid_dashboard_actions(action, kid_id, deck_id):
    # Query the user, kid and deck
    user = get_current_user()
    deck = Deck.query.filter_by(id=deck_id).first()
    # Section to change the kid's name
    if action == 'change_name':
        new_name = request.form.get('newName')
        deck.name = new_name
        db.session.commit()
        flash(f'O nome do baralho foi alterado com successo para {deck.name}.')
        return redirect(url_for('kid_dashboard', username = user.username, kid_id = kid_id, action = 'view'))
    # Section to change the kid's image
    if action == 'change_image':
        new_image = request.files['newImage']
        # Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        # Save the image in the user's directory
        media_file = f'{media_path}/{filename}.png'
        new_image.save(media_file)
        image_path = f'static/media/{user.username}/{filename}.png' # Needs to be slightly changed to be rendered in the HTML
        # Change the image path
        deck.image_path = image_path
        db.session.commit()
        flash(f'A imagem foi alterada com successo.')
        return redirect(url_for('kid_dashboard', username = user.username, kid_id = kid_id, action = 'view'))
    # Section to delete the kid's dashboard
    if action == 'delete_deck':
        password = request.form.get('passwordConfirmation')
        # Checking the password and loginin the user using sessions
        if bcrypt.check_password_hash(user.password, password):
            db.session.delete(deck)
            db.session.commit()
            flash(f'O baralho {deck.name} foi eliminado com successo.')
            return redirect(url_for('kid_dashboard', username = user.username, kid_id = kid_id, action = 'view'))
        flash(f'A palavra-passe não corresponde, o baralho {deck.name} não foi eliminado.')
        return redirect(url_for('kid_dashboard', username = user.username, kid_id = kid_id, action = 'view'))

# Deck Dashboard
@app.route('/dashboard/<username>/<kid_id>/<deck_id>/<action>', methods=['POST', 'GET'])
@signin_required
def deck_dashboard(username, kid_id, deck_id, action):
    # Query the user, kid and deck
    user = get_current_user()
    kid = Kid.query.filter_by(id=kid_id).first()
    deck = Deck.query.filter_by(id=deck_id).first()
    # Restrict user access
    access = user_access(user, username)
    if not access:
        flash('Não tens accesso a esta página, tenta fazer login.')
        return redirect(url_for('sign_in'))
    # Section to add the card
    if action == 'add_card':
        # Form data
        card_name = request.form.get('cardName')
        card_image = request.files['cardImage']
        card_audio = request.files['cardAudio']
        # Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        # Save the image in the user's directory
        media_file = f'{media_path}/{filename}.png'
        card_image.save(media_file)
        image_path = f'static/media/{user.username}/{filename}.png' # Needs to be slightly changed to be rendered in the HTML
        # Save the audio in the user's diretory
        media_file = f'{media_path}/{filename+1}.mp3'
        card_audio.save(media_file)
        audio_path = f'static/media/{user.username}/{filename + 1}.mp3'
        # Add the kid to the database
        card = Card(name = card_name, image_path = image_path, audio_path = audio_path, deck = deck)
        db.session.add(card)
        db.session.commit()
        flash(f'A carta {card.name} foi adicionado com successo!')
        return redirect(url_for('deck_dashboard', username = user.username, kid_id = kid_id, deck_id = deck.id, action = 'view'))
    # Section to rendering the page
    if action == 'view':
        return render_template('deck-dashboard.html', page_name = f'Baralho de {deck.name}', user = user, kid = kid, deck = deck)

# Dashboard Actions
@app.route('/deck-dashboard-actions/<action>/<kid_id>/<deck_id>/<card_id>', methods=['GET', 'POST'])
@signin_required
def deck_dashboard_actions(action, kid_id, deck_id, card_id):
    # Query the user, kid and card
    user = get_current_user()
    deck = Deck.query.filter_by(id=deck_id).first()
    card = Card.query.filter_by(id=card_id).first()
    # Section to change the card's name
    if action == 'change_name':
        new_name = request.form.get('newName')
        card.name = new_name
        db.session.commit()
        flash(f'O nome da carta foi alterado com successo para {card.name}.')
        return redirect(url_for('deck_dashboard', username = user.username, kid_id = kid_id, deck_id = deck_id, action = 'view'))
    # Section to change the card's image
    if action == 'change_image':
        new_image = request.files['newImage']
        # Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        # Save the image in the user's directory
        media_file = f'{media_path}/{filename}.png'
        new_image.save(media_file)
        image_path = f'static/media/{user.username}/{filename}.png' # Needs to be slightly changed to be rendered in the HTML
        # Change the image path
        card.image_path = image_path
        db.session.commit()
        flash(f'A imagem foi alterada com successo.')
        return redirect(url_for('deck_dashboard', username = user.username, kid_id = kid_id, deck_id = deck_id, action = 'view'))
    # Section to change the card's audio
    if action == 'change_audio':
        new_audio = request.files['newAudio']
        # Generate a filename by searching for the highest number in the directory
        media_path = f'application/static/media/{user.username}'
        filename = generate_filename(media_path)
        # Save the audio in the user's directory
        media_file = f'{media_path}/{filename}.mp3'
        new_audio.save(media_file)
        audio_path = f'static/media/{user.username}/{filename}.mp3' # Needs to be slightly changed to be rendered in the HTML
        # Change the audio path
        card.audio_path = audio_path
        db.session.commit()
        flash(f'O audio foi alterado com successo.')
        return redirect(url_for('deck_dashboard', username = user.username, kid_id = kid_id, deck_id = deck_id, action = 'view'))
    # Section to delete the kid's dashboard
    if action == 'delete_card':
        password = request.form.get('passwordConfirmation')
        # Checking the password and loginin the user using sessions
        if bcrypt.check_password_hash(user.password, password):
            db.session.delete(card)
            db.session.commit()
            flash(f'A carta {card.name} foi eliminada com successo.')
            return redirect(url_for('deck_dashboard', username = user.username, kid_id = kid_id, deck_id = deck_id, action = 'view'))
        flash(f'A palavra-passe não corresponde, a carta {card.name} não foi eliminada.')
        return redirect(url_for('deck_dashboard', username = user.username, kid_id = kid_id, deck_id = deck_id, action = 'view'))
    
# Kid's Mode - How the kid will view the application
@app.route('/kid-mode/<username>/<kid_id>/', methods=['POST', 'GET'])
@signin_required
def kid_mode(username, kid_id):
    # Query the user and kid
    user = get_current_user()
    kid = Kid.query.filter_by(id=kid_id).first()
    # Restrict user access
    access = user_access(user, username)
    if not access:
        flash('Não tens accesso a esta página, tenta fazer login.')
        return redirect(url_for('sign_in'))
    return render_template('kid-mode.html', user = user, kid = kid)

# Deck API
@app.route('/api/<username>/<kid_id>/<deck_id>', methods=['POST', 'GET'])
@signin_required
def deck_api(username, kid_id, deck_id):
    # Query the user, kid and deck
    user = get_current_user()
    kid = Kid.query.filter_by(id=kid_id).first()
    deck = Deck.query.filter_by(id=deck_id).first()
    # Restrict user access
    access = user_access(user, username)
    if not access:
        flash('Não tens accesso a esta página, tenta fazer login.')
        return redirect(url_for('sign_in'))
    return jsonify('', render_template('deck-model.html', user=user, deck = deck, kid = kid))
