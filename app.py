from flask import Flask, render_template, request, redirect, send_from_directory, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField, TextAreaField
from wtforms.validators import InputRequired, ValidationError
import subprocess
import csv
from json_to_csv import json_to_csv

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/input'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

class FileUploadForm(FlaskForm):
    file = FileField('Upload File', validators=[InputRequired()])
    submit = SubmitField('Upload')

class TaskUpdateForm(FlaskForm):
    task_id = StringField('ID', validators=[InputRequired()])
    task_requirement = TextAreaField('Requirement', validators=[InputRequired()])
    submit = SubmitField('Update')

class TaskManualForm(FlaskForm):
    task_id = StringField('ID', validators=[InputRequired()])
    task_requirement = TextAreaField('Requirement', validators=[InputRequired()])
    submit = SubmitField('Add Task')

class JsonToCsvForm(FlaskForm):
    json_file = FileField('Upload JSON File', validators=[InputRequired()])
    submit_json_to_csv = SubmitField('Convert JSON to CSV')


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

        # Create a list of project keys from the current elements in the table
        project_keys = set()
        for task in tasks:
            reqid = task.content.split(',')[0].split('-')[0]
            project_keys.add(reqid)

        form = FileUploadForm()
        return render_template('index.html', tasks=tasks, form=form, project_keys=project_keys)

@app.route('/add_task_manual', methods=['POST'])
def add_task_manual():
    form = TaskManualForm()
    if form.validate_on_submit():
        task_id = form.task_id.data
        task_requirement = form.task_requirement.data
        content = f"{task_id}, {task_requirement}"
        new_task = Todo(content=content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        flash('ID and Requirement are required fields.', 'error')
        return redirect('/')

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
    form = TaskUpdateForm(obj=task)

    if request.method == 'POST' and form.validate_on_submit():
        task_id = form.task_id.data
        task_requirement = form.task_requirement.data
        content = f"{task_id}, {task_requirement}"
        task.content = content

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task, form=form)

@app.route('/upload', methods=['POST'])
def upload():
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return redirect('/')
    else:
        # If the form doesn't validate, show the error message
        flash('You must upload a file.', 'error')
        return redirect('/')
    
@app.route('/append_to_table', methods=['POST'])
def append_to_table():
    
    output_file_path = os.path.join('static', 'output', 'output.csv')
    with open(output_file_path, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip the header row
        data_to_append = list(csv_reader)

    # Add the data to the database table
    for row in data_to_append:
        if len(row) >= 2:
            reqid = row[0]
            rationale = row[1]
            content = f"{reqid}, {rationale}"
            new_task = Todo(content=content)

            try:
                db.session.add(new_task)
                db.session.commit()
            except:
                return 'There was an issue appending data to the table'
        else:
            return 'Invalid data in CSV file'

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
    csv_data = [['ID', 'Requirement', 'Date']]

    # Add each task to the CSV data
    for task in tasks:
        task_id, task_requirement = task.content.split(',', 1)  # Split only once to get ID and Requirement
        csv_data.append([task_id, task_requirement, task.date_created.date()])

    # Save the CSV data to a file on the server
    csv_file_path = os.path.join('static', 'export', 'table_data.csv')
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)

    # Set the appropriate headers to trigger the download in the browser
    response = send_from_directory('static/export', 'table_data.csv', as_attachment=True)

    return response

@app.route('/json_to_csv', methods=['POST'])
def json_to_csv_route():
    form = JsonToCsvForm()
    if form.validate_on_submit():
        json_file = form.json_file.data
        json_filename = secure_filename(json_file.filename)
        json_path = os.path.join(app.config['UPLOAD_FOLDER'], json_filename)
        json_file.save(json_path)

        csv_filename = 'output.csv'  # Output CSV filename
        csv_path = os.path.join('static', 'output', csv_filename)

        json_to_csv(json_path, csv_path)

        return redirect('/')
    else:
        flash('You must upload a JSON file.', 'error')
        return redirect('/')

@app.route('/download_csv')
def download_csv():
    csv_filename = 'output.csv'  # Same output CSV filename
    csv_path = os.path.join('static', 'output', csv_filename)
    return send_file(csv_path, as_attachment=True)

    
if __name__ == "__main__":
    app.run(debug=True)