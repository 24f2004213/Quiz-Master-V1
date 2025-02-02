# Quiz-Master-V1

Quiz-Master-V1 is a multi-user application that serves as an exam preparation platform for multiple courses. The app is designed with two types of roles: an Admin (Quiz Master) and Users. The Admin manages all subjects, chapters, quizzes, and users, while users can register, log in, choose subjects, and attempt quizzes.

## Features
- **Admin Role**:
  - Full control over users and quiz data.
  - Create subjects, chapters, and quizzes.
  - Add, edit, or delete questions for each quiz.
  - Manage users, track quiz attempts, and view summary charts.
- **User Role**:
  - Register, log in, and access available quizzes.
  - Attempt quizzes from a chosen subject and chapter.
  - View quiz scores and track previous attempts with summary charts.

## Frameworks and Tools
The project is built using the following frameworks:
- **Flask**: Application back-end.
- **Jinja2, HTML, CSS, Bootstrap**: Front-end.
- **SQLite**: Database (no other database is permitted).

## Application Flow
1. **Admin Login**: Admin logs in without the need for registration. The Admin is pre-configured in the database.
2. **User Registration/Login**: Users can register with their details like full name, email, qualification, and DOB.
3. **Quiz Management**: Admin creates subjects, chapters, and quizzes with multiple-choice questions (MCQs).
4. **User Quiz Attempt**: Users can select a subject, choose a chapter, and attempt the quizzes under that chapter.
5. **Quiz Scores**: After completing a quiz, the user's score is stored, and users can view previous attempts.

## Database Design
- **User**: Stores user information such as id, email, password, name, qualification, and DOB.
- **Admin**: Only one admin with full privileges (pre-configured).
- **Subject**: The field of study for which quizzes are created.
- **Chapter**: Subdivisions within a subject, containing quizzes.
- **Quiz**: Contains information about quizzes, including questions and quiz settings (duration, date).
- **Question**: Stores questions with multiple options and correct answers.
- **Score**: Records the results of a user's quiz attempt.

## Recommended Features
- API resources to interact with subjects, chapters, and quizzes.
- External libraries like Chart.js for visualizing quiz data.
- Front-end validation with HTML5 or JavaScript.
- Backend validation for robust form handling.

## Optional Features
- Aesthetic improvements using CSS/Bootstrap for a responsive interface.
- Flask extensions like flask_login or flask_security for authentication.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Quiz-Master-V1.git
2. Navigate to the project directory:
   ```bash
   cd Quiz-Master-V1
3. Set up a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
4. Run the application locally:
   ```bash
   flask run
