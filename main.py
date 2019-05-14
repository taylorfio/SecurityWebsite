from flask import Flask, render_template, Response, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import hashlib
from camara import VideoCamera

app = Flask(__name__)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id, "temp")


class User(UserMixin):
    def __init__(self, id, username):
        self.username = username
        self.id = id


@app.route('/')
def gotologin():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    global file_password, file_user
    if request.method == 'POST':

        try:
            file = open("user.txt", "r")
            file_user = file.readlines(1)
            file_password = file.readlines(0)
        except IOError:
            print("can't find password file")

        hasher = hashlib.md5()  # the hasher import is called
        hasher.update(request.form['password'].encode('utf-8'))  # the hasher is hashing the password input from the list
        password = hasher.hexdigest()  # the hashed password is linked to account_password string

        if request.form['username'] != file_user[0].strip() or password != file_password[0].strip():
            error = 'Invalid Credentials. Please try again.'
        else:
            login_user(User(0, 'admin'))
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
@login_required
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/about')
@login_required
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.config["SECRET_KEY"] = 'ITSASECRET'
    app.run(host='0.0.0.0', debug=True)

# use command ./ngrok http 5000
