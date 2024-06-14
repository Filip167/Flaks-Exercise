from flask import Flask, render_template, redirect, url_for, session, flash, request
from models import db, User, Feedback, bcrypt
from forms import RegisterForm, LoginForm, FeedbackForm
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecretkey'
db.init_app(app)
bcrypt.init_app(app)
Bootstrap(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data,
                        first_name=form.first_name.data, last_name=form.last_name.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            session['username'] = user.username
            return redirect(url_for('user_detail', username=user.username))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account: {}'.format(e), 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['username'] = user.username
            return redirect(url_for('user_detail', username=user.username))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/users/<username>')
def user_detail(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    user = User.query.get_or_404(username)
    return render_template('user_detail.html', user=user)

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(title=form.title.data, content=form.content.data, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('user_detail', username=username))
    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if 'username' not in session or session['username'] != feedback.username:
        return redirect(url_for('login'))
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(url_for('user_detail', username=feedback.username))
    return render_template('edit_feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if 'username' not in session or session['username'] != feedback.username:
        return redirect(url_for('login'))
    db.session.delete(feedback)
    db.session.commit()
    return redirect(url_for('user_detail', username=feedback.username))

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username', None)
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
