import fasttext
import json
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
from flask_login import UserMixin, login_required, login_user, LoginManager, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField 
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'key1'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
model = fasttext.load_model("model.bin")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))
    text = db.Column(db.String(1000))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = None

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for('view_database'))
        
        error_message = 'Invalid username or password.'

    return render_template('login.html', form=form, error_message=error_message)



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/add_mock_data')
def add_mock_data():
    json_file = 'mock_data.json'
    with open(json_file, 'r') as f:
        data = json.load(f)

    random.shuffle(data)

    for item in data:
        prediction = Prediction(label=item["label"], text=item["text"])
        db.session.add(prediction)
    db.session.commit()

    return redirect(url_for('view_database'))




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    text = list(request.form.values())[0].strip()
    prediction = model.predict(text)[0][0]

    if prediction == "__label__raymond":
        prediction = "Service Desk."
    elif prediction == "__label__brendan":
        prediction = "Audio Visual."
    elif prediction == "__label__paul":
        prediction = "Security."
    elif prediction == "__label__kevin":
        prediction = "Networking ."
    else:
        prediction = "Unknown"

    new_prediction = Prediction(label=prediction, text=text)
    db.session.add(new_prediction)
    db.session.commit()



    return render_template('updatedpage.html', prediction_text = "This ticket should go to " + prediction)

@app.route('/view_database' , methods=['GET', 'POST'])
@login_required
def view_database():
    # Retrieve all predictions from the database
    predictions = Prediction.query.all()

    return render_template('view_database.html', predictions=predictions)

@app.route('/clear_database')
def clear_database():
    # Delete all records from the Prediction table
    db.session.query(Prediction).delete()
    db.session.commit()

    return redirect(url_for('view_database'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
       

    # Register the clear_database route
    app.add_url_rule('/clear_database', 'clear_database', clear_database)
    app.add_url_rule('/add_mock_data', 'add_mock_data', add_mock_data)

    app.run(port=8000, debug=True)
