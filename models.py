from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)

    meals = db.relationship('Meal')

    favorites = db.relationship('Favorite')

    @classmethod
    def serialize(self):
        """Serialize User instance for JSON"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

    def __repr__(self):
        return f'<User #{self.id}: {self.username}, {self.email}'

    @classmethod
    def register(cls, username, email, password):
        """Register user with hashed password and return here."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        user = User(username=username,
                    email=email,
                    password=hashed_utf8)
        #return instance of user with username and hashed pwd

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists and password is correct. Return user if valid; else return false."""

        u = cls.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

class Ingredient(db.Model):

    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    

    users = db.relationship('User', secondary="meals", backref='ingredients', lazy=True)

    meals = db.relationship('Meal')

    @property
    def ingredient_name(self):
        return f'{self.name}'

    def serialize(self):
        """Return a dict representatio of ingredients which we can turn into JSON."""
        return {
            'id': self.id,
            'name': self.name,
                   }

    def __repr__(self):
        return f'<Ingredient = id:{self.id}, name:{self.name}'

class Meal(db.Model):
    """Create a meal for each user."""

    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id', ondelete='cascade'), primary_key=True)

    def __repr__(self):
        return f'<Meal=user_id:{self.user_id} ingredient_id:{self.ingredient_id}>'

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(
         db.Integer,
         primary_key=True)

    title = db.Column(
            db.String,
            nullable=False)

    image = db.Column(
            db.String,
            nullable=False)

    readyInMinutes = db.Column(
                     db.Integer)

    servings = db.Column(
               db.Integer)

    sourceName = db.Column(
                 db.String)

    sourceUrl = db.Column(
                db.String)

    users = db.relationship('User',
                            secondary='favorites',
                            backref='recipes',
                            lazy=True)

    favorites = db.relationship('Favorite')

    @property
    def recipe_name(self):
       return f'{self.title}'

    def serialize(self):
        """Returns a dict representation of recipes which we can turn into JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'img_url': self.image,
            'prep_time': self.readyInMinutes,
            'serves': self.servings,
            'source_name': self.sourceName,
            'source_url': self.sourceUrl
        }

    def __repr__(self):
        return f'<Recipe = id:{self.id}, title:{self.title}, source_name:{self.sourceName}>'

class Favorite(db.Model):
    """ Many to Many Users to Recipes """
    __tablename__ = "favorites"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'),
                        primary_key=True)
    recipe_id = db.Column(db.Integer,
                          db.ForeignKey('recipes.id', ondelete='cascade'),
                          primary_key=True)

    def __repr__(self):
        return f'<Favorite= user_id:{self.user_id} recipe_id:{self.recipe_id}>'
    
    