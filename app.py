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


    return render_template('index.html', prediction_text = "This should be assigned to: " + prediction.replace('__label__', '').capitalize())


if __name__ == "__main__":
    app.run()
# label, probability = model.predict("I cant print")
# print("Label:", label[0])
# print("Probability:", probability[0])
# print(model.predict("I cant print"))