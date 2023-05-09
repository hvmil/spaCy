import fasttext
from flask import Flask, request, render_template


app = Flask(__name__)
model = fasttext.load_model("model.bin")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
   
    prediction = model.predict(list(request.form.values())[0])[0][0]
    match prediction:
        case "__label__raymond":
            prediction = "Raymond Ransome."

        case "__label__brendan":
            prediction = "Brendan Gannon."
        case "__label__paul":
           prediction = "Paul Chauvet."

        case "__label__kevin":
            prediction = "Kevin Saunders."
        case _:
            prediction = "Unknown"

    return render_template('index.html', prediction_text = "This should be assigned to " + prediction)


if __name__ == "__main__":
    app.run()
# label, probability = model.predict("I cant print")
# print("Label:", label[0])
# print("Probability:", probability[0])
# print(model.predict("I cant print"))