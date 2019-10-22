import os
import requests
import operator
import re
import nltk
import json
from rq import Queue
from rq.job import Job
from worker import conn
from flask import Flask, render_template, request, jsonify
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
q = Queue(connection=conn)

from models import Result  # noqa workaround for circular import


def sanitize_url(url):
    return url if 'http://' in url or 'https://' in url else f'https://{url}'


def count_and_save_words(url):
    errors = []

    try:
        r = requests.get(sanitize_url(url))
    except Exception:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

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
    try:
        result = Result(
            url=url,
            result_all=raw_word_count,
            result_no_stop_words=no_stop_words_count
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except Exception:
        errors.append("Unable to add item to database.")
    return {"error": errors}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    # get url from POST payload
    data = json.loads(request.data.decode())
    url = data["url"]
    # start job
    job = q.enqueue_call(
        func=count_and_save_words, args=(url,), result_ttl=5000
    )
    return job.get_id()


@app.route('/results/<job_key>', methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)
    quantity = request.args.get('quantity', None)
    results_quantity = int(quantity) if quantity else None

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:results_quantity]
        return jsonify(results)
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run()
