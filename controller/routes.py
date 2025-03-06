from main import app
from flask import render_template, request, session, flash, redirect, url_for
from controller.database import db
from controller.models import *
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    subjects = Subject.query.options(db.joinedload(Subject.chapters)).all()
    return render_template('home.html', subjects=subjects)
@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')
@app.route('/subject', methods=['GET', 'POST'])
def subject():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        if not name:
            flash("Subject name is required")
            return render_template('subject.html')
        if not description:
            flash("Description is required")
            return render_template('subject.html')
        
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash("Subject added successfully")
        return redirect(url_for('home'))
        
    return render_template('subject.html')

@app.route('/chapter/<int:subject_id>', methods=['GET', 'POST']) 
def chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name or not subject_id:
            flash("Chapter name and subject are required")
            return redirect(url_for('chapter', subject_id=subject_id))
        
        new_chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()

        flash("Chapter added successfully")
        return redirect(url_for('home'))

    return render_template('chapter.html', subject=subject)

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)  

    if request.method == 'POST':
        chapter.name = request.form.get('name')
        chapter.description = request.form.get('description')
        db.session.commit()
        flash("Chapter updated successfully!", "success")
        return redirect(url_for('home'))

    return render_template('edit_chapter.html', chapter=chapter) 

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)  # Fetch the chapter
    
    db.session.delete(chapter)  # Delete from database
    db.session.commit()  # Save changes
    
    flash("Chapter deleted successfully!", "success")  # Optional success message
    return redirect(url_for('home'))  # Redirect to home page


@app.route('/quiz-list', methods=['GET', 'POST'])
def quiz_list():
    quizzes = Quiz.query.all()
    questions = Question.query.all()
        
    return render_template('quiz.html', quizzes=quizzes, questions=questions)

@app.route('/add-quiz', methods=['GET', 'POST'])
def add_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        chapter_id = request.form.get('chapter_id')
        date_of_quiz = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        # Validate required fields
        if not title or not chapter_id or not date_of_quiz or not time_duration:
            flash("All fields except remarks are required.", "error")
            return redirect(url_for('add_quiz'))

        # Convert date_of_quiz to datetime format
        try:
            date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('add_quiz'))

        # Create a new quiz object
        new_quiz = Quiz(
            title=title,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=int(time_duration),
            remarks=remarks
        )

        # Save to database
        db.session.add(new_quiz)
        db.session.commit()

        flash("Quiz added successfully!", "success")
        return redirect(url_for('quiz_list'))  # Redirect to quiz list

    # Fetch available chapters to display in the form
    chapters = Chapter.query.all()
    return render_template('add_quiz.html', chapters=chapters)


@app.route('/add-question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question_page(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        title = request.form.get('title')
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')

        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            flash("All fields are required!", "danger")
            return redirect(url_for('add_question_page', quiz_id=quiz_id))

        new_question = Question(
            title=title,
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )

        db.session.add(new_question)
        db.session.commit()
        flash("Question added successfully!", "success")
        return redirect(url_for('quiz_list'))  # Redirect to quiz list

    return render_template('add_question.html', quiz=quiz)

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)  # Fetch question or return 404 if not found

    if request.method == 'POST':
        question.title = request.form['title']
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = request.form['correct_option']

        db.session.commit()  # Save changes to database
        flash('Question updated successfully!', 'success')
        return redirect(url_for('quiz_list'))  # Redirect to quiz list page

    return render_template('edit_question.html', question=question)

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)  # Fetch question or return 404 if not found

    db.session.delete(question)  # Delete question from database
    db.session.commit()  # Commit changes
    flash('Question deleted successfully!', 'success')

    return redirect(url_for('quiz_list'))  # Redirect to quiz list page
