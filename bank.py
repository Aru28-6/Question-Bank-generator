from flask import Flask, request, send_file, render_template
from pymongo import MongoClient
from fpdf import FPDF
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['question_db']
collection = db['questions']

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('question.html')


@app.route('/submit_question', methods=['POST'])
def submit_question():
    text_question = request.form.get('textQuestion')
    image_file = request.files.get('imageQuestion')

    if image_file:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
    else:
        image_path = None

    question = {
        'text_question': text_question,
        'image_path': image_path
    }
    collection.insert_one(question)

    return 'Question submitted successfully!', 200


@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    questions = list(collection.find({}))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for question in questions:
        if question['text_question']:
            pdf.multi_cell(0, 10, question['text_question'])

        if question['image_path']:
            pdf.image(question['image_path'], x=10, y=pdf.get_y(), w=100)
            pdf.ln(10)

    pdf_output_path = os.path.join(UPLOAD_FOLDER, "questions.pdf")
    pdf.output(pdf_output_path)
    return send_file(pdf_output_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
