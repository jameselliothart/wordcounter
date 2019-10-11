import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Result  # noqa workaround for circular import


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    r = None
    if request.method == "POST":
        try:
            url = request.form.get('url')
            r = requests.get(url)
        except Exception:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors)
    if r:
        # process text
        soup = BeautifulSoup(r.text, 'html.parser')
        for script in soup(['script', 'style']):
            script.decompose()  # remove scripts and styles
        raw = soup.get_text()
        nltk.data.path.append('./nltk_data/')  # set path
        text = nltk.tokenize.word_tokenize(raw)
        # remove punctuation and count raw words
        nonPunct = re.compile('.*[A-Za-z].*')
        raw_words = [w for w in text if nonPunct.match(w)]
        raw_word_count = Counter(raw_words)
        # stop words
        no_stop_words = [w for w in raw_words if w.lower() not in stops]
        no_stop_words_count = Counter(no_stop_words)
        # save results
        results = sorted(
            no_stop_words_count.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        try:
            result = Result(
                url=url,
                result_all=raw_word_count,
                result_no_stop_words=no_stop_words_count
            )
            db.session.add(result)
            db.session.commit()
        except Exception:
            errors.append("Unable to add item to database.")
    return render_template('index.html', errors=errors, results=results)


if __name__ == '__main__':
    app.run(port=5001)
