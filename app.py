import fasttext
import json
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
model = fasttext.load_model("model.bin")


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100))
    text = db.Column(db.String(1000))

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
        prediction = "Networking."
    else:
        prediction = "Unknown"

    new_prediction = Prediction(label=prediction, text=text)
    db.session.add(new_prediction)
    db.session.commit()



    return render_template('updatedpage.html', prediction_text = "This ticket should go to " + prediction)

@app.route('/view_database')
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
