from flask import Flask, render_template
from flask import request
from flask import jsonify
from flask import send_from_directory
import random
import os
import sys
import json
import spacy
import csv
from process_data import ascii


def serve(train, cnn, text_field, label_field, cuda):
    with open('data/unique-questions.csv', 'r') as outf:
        questions = list(csv.reader(outf, delimiter=',', quotechar='"'))

    nlp = spacy.load('../fasttext/spacy-fasttext-sr')

    app = Flask(__name__, template_folder='static')

    @app.route('/<path:filename>', methods=['GET', 'POST'])
    def index(filename):
        if request.method == 'GET':
            return send_from_directory('static', filename)

        return jsonify(request.data)

    @app.route('/model')
    def model():
        return sys.argv[2]

    @app.route('/ram')
    def ram():
        tot_m, used_m, free_m = map(int, os.popen('free -t -m').readlines()[-1]
                    .split()[1:])
        return str(used_m) + '/' + str(tot_m) + 'MB'

    @app.route('/cpu')
    def cpu():
        cpuu = str(round(float(os.popen('''grep 'cpu ' /proc/stat |
    awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()), 2))
        return cpuu + '%'

    @app.route('/gpu')
    def gpu():
        return str(os.popen('nvidia-smi | grep MiB').read())[33:55]

    @app.route('/ask', methods=['POST'])
    def ask():
        question = ascii(request.form['question'], nlp)
        answer = ascii(request.form['answer'], nlp)

        if len(answer.strip()) == 0 or answer.strip() == '-' or len(answer.split()) < 3:
            grade = '0.00'
        else:
            grade = train.predict(question + '<pad>' + answer, cnn, text_field, label_field, cuda)

        return json.dumps({'q': question, 'a': answer, 'g': grade})

    @app.route('/randomq')
    def randomq():
        return random.choice(questions)[0]

    @app.route('/allq')
    def allq():
        return json.dumps(questions)

    @app.route('/version')
    def version():
        return str(os.popen('git rev-parse --short HEAD').read())

    @app.route('/')
    def home():
        return render_template('index.html', version=version(), questions=questions)

    @app.route('/test')
    def test():
        return render_template('test.html', questions=enumerate(random.choices(questions, k=5)), version=version())

    app.run(host='0.0.0.0', port=39250)
