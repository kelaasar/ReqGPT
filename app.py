from flask import Flask, render_template, url_for, request, redirect, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired, ValidationError
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/input'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

class JSONFileValidator(object):
    def __call__(self, form, field):
        if field.data:
            filename = field.data.filename
            if not filename.lower().endswith('.json'):
                raise ValidationError('You must upload a JSON file.')

class FileUploadForm(FlaskForm):
    file = FileField('Upload File', validators=[InputRequired()])
    submit = SubmitField('Upload')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        form = FileUploadForm()
        return render_template('index.html', tasks=tasks, form=form)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)

@app.route('/upload', methods=['POST'])
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Run script.py using subprocess
        script_path = os.path.join(os.path.dirname(__file__), 'script.py')
        subprocess.run(['python', script_path, file_path])  # Pass the uploaded file path to the script

        return redirect('/')
    else:
        # If the form doesn't validate, show the error message
        flash('You must upload a file.', 'error')
        return redirect('/')
    
if __name__ == "__main__":
    app.run(debug=True)