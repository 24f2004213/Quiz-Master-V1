from main import app
from flask import render_template, request, session, flash, redirect, url_for, jsonify
from controller.database import db
from controller.models import *
from datetime import datetime, timedelta
from flask_login import LoginManager,UserMixin, login_required, current_user, login_user, logout_user
from sqlalchemy import func

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    subjects = Subject.query.options(db.joinedload(Subject.chapters)).all()
    return render_template('home.html', subjects=subjects)
@app.route('/user_dashboard')
def user_dashboard():
    question_count_subquery = db.session.query(
    Question.quiz_id, func.count(Question.id).label("question_count")
).group_by(Question.quiz_id).subquery()

# Main query to fetch quiz details along with the question count
    quizzes = db.session.query(
        Quiz.id,
        Quiz.title,
        Chapter.name.label("chapter_name"),
        Subject.name.label("subject_name"),
        Quiz.date_of_quiz,
        Quiz.time_duration,
        func.coalesce(question_count_subquery.c.question_count, 0).label("question_count")  # Ensure 0 for empty quizzes
    ).join(Chapter, Quiz.chapter_id == Chapter.id) \
    .join(Subject, Chapter.subject_id == Subject.id) \
    .outerjoin(question_count_subquery, Quiz.id == question_count_subquery.c.quiz_id) \
    .all()
    return render_template('user_dashboard.html', quizzes=quizzes, user = current_user)
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
        time_start = request.form.get('time_start')
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        # Validate required fields
        if not title or not chapter_id or not date_of_quiz or not time_start or not time_duration:
            flash("All fields except remarks are required.", "error")
            return redirect(url_for('add_quiz'))

        # Convert date_of_quiz to datetime.date format
        try:
            date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "error")
            return redirect(url_for('add_quiz'))

        # Convert time_start to datetime.time format
        try:
            time_start = datetime.strptime(time_start, "%H:%M").time()
        except ValueError:
            flash("Invalid time format. Use HH:MM.", "error")
            return redirect(url_for('add_quiz'))

        # Create a new quiz object
        try:
            new_quiz = Quiz(
                title=title,
                chapter_id=chapter_id,
                date_of_quiz=date_of_quiz,
                time_start=time_start,
                time_duration=int(time_duration),  # Ensure time_duration is an integer
                remarks=remarks
            )

            # Save to the database
            db.session.add(new_quiz)
            db.session.commit()

            flash("Quiz added successfully!", "success")
            return redirect(url_for('quiz_list'))  # Redirect to the quiz list
        except Exception as e:
            flash(f"An error occurred while adding the quiz: {str(e)}", "error")
            db.session.rollback()
            return redirect(url_for('add_quiz'))

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

@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quiz(quiz_id):
    if not current_user.is_authenticated:
        flash("You need to sign in first!", "warning")
        return redirect(url_for('login'))  # This should NOT happen if the user is signed in

    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if not quiz:
        return {"status": "error", "message": "Quiz not found."}

    current_time = datetime.now()
    quiz_start = datetime.combine(quiz.date_of_quiz, quiz.time_start)
    quiz_end = quiz_start + timedelta(minutes=int(quiz.time_duration))

    if current_time < quiz_start:
        return redirect(url_for('user_dashboard', status='not_started', quiz_time=quiz.time_start.strftime('%H:%M')))
    if current_time > quiz_end:
        return redirect(url_for('user_dashboard', status='ended'))
    if current_time > quiz_start and current_time < quiz_end:
        return redirect(url_for('user_quiz',status='active', quiz_id=quiz_id))

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.form.get(f'question-{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1

        attempt = Score(
            user_id=current_user.user_id,
            quiz_id=quiz_id,
            total_scored=score,
            time_stamp_of_attempt=current_time
        )

        db.session.add(attempt)
        db.session.commit()

        return render_template('result.html', score=score, total=len(questions), quiz=quiz)


    return render_template('user_quiz.html', quiz=quiz, questions=questions)

@app.route('/scores')
@login_required
def scores():
    user_scores = Score.query.filter_by(user_id=current_user.user_id).all()
    return render_template('scores.html', scores=user_scores)

@app.route('/result/<int:quiz_id>')
@login_required
def view_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user_score = Score.query.filter_by(user_id=current_user.user_id, quiz_id=quiz_id).first()

    if not user_score:
        flash("You haven't attempted this quiz yet.", "danger")
        return redirect(url_for('scores'))

    return render_template('result.html', quiz=quiz, score=user_score)

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip().lower()
    filter_type = request.args.get('filter', '')

    results = []

    # Admin Search: Users, Subjects, Quizzes, Questions
    if current_user.roles == "admin":
        if filter_type == "users":
            results = User.query.filter(User.name.ilike(f"%{query}%")).all()
        elif filter_type == "subjects":
            results = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        elif filter_type == "quizzes":
            results = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
        elif filter_type == "questions":
            results = Question.query.filter(Question.question_statement.ilike(f"%{query}%")).all()
    
    # User Search: Only Subjects & Quizzes
    else:
        if filter_type == "subjects":
            results = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        elif filter_type == "quizzes":
            results = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

    return render_template('search.html', query=query, filter_type=filter_type, results=results)

@app.route('/quiz/details/<int:quiz_id>')
def quiz_details(quiz_id):
    quiz = db.session.query(
        Quiz.id,
        Quiz.title,
        Chapter.name.label("chapter_name"),
        Subject.name.label("subject_name"),
        Quiz.date_of_quiz,
        Quiz.time_duration
    ).join(Chapter, Quiz.chapter_id == Chapter.id) \
     .join(Subject, Chapter.subject_id == Subject.id) \
     .filter(Quiz.id == quiz_id) \
     .first()

    if not quiz:
        return "Quiz not found", 404

    return render_template('quiz_details.html', quiz=quiz)

@app.route('/api/subjects', methods=['GET'])
def api_get_subjects():
    subjects = Subject.query.all()
    return jsonify([{"id": subject.id, "name": subject.name} for subject in subjects])

@app.route('/api/chapters', methods=['GET'])
def api_get_chapters():
    subject_id = request.args.get('subject_id')
    if subject_id:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    else:
        chapters = Chapter.query.all()
    return jsonify([
        {"id": chapter.id, "name": chapter.name, "subject_id": chapter.subject_id} 
        for chapter in chapters
    ])

@app.route('/api/quizzes', methods=['GET'])
def api_get_quizzes():
    chapter_id = request.args.get('chapter_id')
    if chapter_id:
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    else:
        quizzes = Quiz.query.all()
    return jsonify([
        {
            "id": quiz.id,
            "title": quiz.title,
            "chapter_id": quiz.chapter_id,
            "date_of_quiz": quiz.date_of_quiz.strftime('%Y-%m-%d'),
            "time_start": quiz.time_start.strftime('%H:%M'),
            "time_duration": quiz.time_duration
        }
        for quiz in quizzes
    ])

@app.route('/api/scores', methods=['GET'])
def api_get_scores():
    user_id = request.args.get('user_id')
    if user_id:
        scores = Score.query.filter_by(user_id=user_id).all()
    else:
        scores = Score.query.all()
    return jsonify([
        {
            "id": score.id,
            "user_id": score.user_id,
            "quiz_id": score.quiz_id,
            "total_scored": score.total_scored,
            "time_stamp_of_attempt": score.time_stamp_of_attempt.strftime('%Y-%m-%d %H:%M:%S')
        }
        for score in scores
    ])
