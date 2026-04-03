from flask   import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = 'data/messages.json'


def load_messages():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_message(text):
    messages = load_messages()
    messages.append({"text": text})
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('message')
        if text:
            save_message(text)
        return redirect('/')

    messages = load_messages()
    return render_template('index.html', messages=messages)


if __name__ == '__main__':
    app.run(debug=False)