from waitress import serve
from flask   import Flask, render_template, request, redirect
import json
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import shutil

app = Flask(__name__)
DATA_FILE = 'data/messages.json'


def load_messages():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []


def save_message(text, filename=None):
    messages = load_messages()
    messages.append({"text": text, "filename": filename})
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def get_all_files():
    if not os.path.exists(UPLOAD_FOLDER):
        return []
    return os.listdir(UPLOAD_FOLDER)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('message')
        file = request.files.get('file')

        filename = None
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if text or filename:
            save_message(text, filename)
        return redirect('/')

    return render_template('index.html',
                           messages=load_messages(),
                           files=get_all_files())


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/clear', methods=['POST'])
def clear_messages():
    # 1. Очищаем JSON с сообщениями
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

    # 2. Удаляем все файлы из папки uploads
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.is_link(file_path):
                    os.unlink(file_path)  # Удаляем файл или ссылку
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Удаляем подпапку, если она вдруг там есть
            except Exception as e:
                print(f'Ошибка при удалении {file_path}: {e}')

    return redirect('/')

UPLOAD_FOLDER = '/data/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}

# Создаем папку, если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    # Пытаемся взять порт из переменной окружения, иначе ставим 80
    port = int(os.environ.get("PORT", 80))
    print(f"Приложение запускается на порту {port}")
    serve(app, host='0.0.0.0', port=port)