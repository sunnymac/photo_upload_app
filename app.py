import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed file types
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_db():
    """Initialize the SQLite database and create table if not exists."""
    conn = sqlite3.connect('photos.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn = sqlite3.connect('photos.db')
            c = conn.cursor()
            c.execute("INSERT INTO photos (filename) VALUES (?)", (filename,))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    
    conn = sqlite3.connect('photos.db')
    c = conn.cursor()
    c.execute("SELECT filename FROM photos ORDER BY id DESC LIMIT 1")
    result = c.fetchone()
    photo = result[0] if result else None
    conn.close()
    
    return render_template('index.html', photo=photo)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
