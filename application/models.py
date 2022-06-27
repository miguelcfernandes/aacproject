from application import db # Importing the database instance

# PreUser Table
class PreUser(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False)
    kids = db.relationship('Kid', backref='user')

# Kid Table
class Kid(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    image_path = db.Column(db.String(200), nullable = False)
    card_size = db.Column(db.Integer(), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    decks = db.relationship('Deck', backref = 'kid')

# Deck Table
class Deck(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    image_path = db.Column(db.String(200), nullable = False)
    cards = db.relationship('Card', backref = 'deck')
    kid_id = db.Column(db.Integer, db.ForeignKey('kid.id'))

# Card Table
class Card(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    image_path = db.Column(db.String(200), nullable = False)
    audio_path = db.Column(db.String(200), nullable = False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))