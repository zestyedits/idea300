from sessionarchitect import db, login_manager
from flask_login import UserMixin

# Function required by Flask-Login to load a user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# The User table in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    # KEY FIELD FOR SUBSCRIPTION TIERS!
    subscription_tier = db.Column(db.String(20), default='Free') 
    
    # Field to track free generations
    generations_this_month = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"User('{self.email}', '{self.subscription_tier}')"