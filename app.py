from flask import Flask, render_template, url_for, request, redirect, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired, ValidationError
import subprocess
import csv

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
    
@app.route('/append_to_table', methods=['POST'])
def append_to_table():
    # Read the CSV file generated by script.py
    output_file_path = os.path.join('static', 'output', 'output.csv')
    with open(output_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        data_to_append = list(csv_reader)

    # Add the data to the database table
    for reqid, rationale in data_to_append:
        content = f'Reqid: {reqid}' + "--------" + f'Rationale: {rationale}'
        new_task = Todo(content=content)
        try:
            db.session.add(new_task)
            db.session.commit()
        except:
            return 'There was an issue appending data to the table'

    return redirect('/')

@app.route('/clear_table', methods=['POST'])
def clear_table():
    try:
        # Clear the entire table
        Todo.query.delete()
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue clearing the table'

@app.route('/export_table', methods=['POST'])
def export_table():
    # Query all tasks from the database
    tasks = Todo.query.all()

    # Create a list to store the CSV data
    csv_data = [['Requirement', 'Date']]

    # Add each task to the CSV data
    for task in tasks:
        csv_data.append([task.content, task.date_created.date()])

    # Save the CSV data to a file on the server
    csv_file_path = os.path.join('static', 'export', 'table_data.csv')
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    # Set the appropriate headers to trigger the download in the browser
    response = send_from_directory('static/export', 'table_data.csv', as_attachment=True)

    return response

    
if __name__ == "__main__":
    app.run(debug=True)