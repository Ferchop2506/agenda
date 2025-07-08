from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'agenda_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# MODELOS
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    contactos = db.relationship('Contacto', backref='usuario', lazy=True)

class Contacto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    genero = db.Column(db.String(10))  # Hombre o Mujer
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    contactos = Contacto.query.filter_by(usuario_id=current_user.id).all()
    return render_template('index.html', contactos=contactos, user=current_user)

@app.route('/contacto_add', methods=['GET', 'POST'])
@login_required
def contacto_add():
    if request.method == 'POST':
        nuevo = Contacto(
            nombres=request.form['nombres'],
            apellidos=request.form['apellidos'],
            direccion=request.form['direccion'],
            telefono=request.form['telefono'],
            email=request.form['email'],
            genero=request.form['genero'],
            usuario_id=current_user.id
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('contacto_add.html', user=current_user)

@app.route('/contacto_update/<int:id>', methods=['GET', 'POST'])
@login_required
def contacto_update(id):
    contacto = Contacto.query.get_or_404(id)
    if request.method == 'POST':
        contacto.nombres = request.form['nombres']
        contacto.apellidos = request.form['apellidos']
        contacto.direccion = request.form['direccion']
        contacto.telefono = request.form['telefono']
        contacto.email = request.form['email']
        contacto.genero = request.form['genero']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('contacto_update.html', contacto=contacto, user=current_user)

@app.route('/contacto_delete/<int:id>')
@login_required
def contacto_delete(id):
    contacto = Contacto.query.get_or_404(id)
    db.session.delete(contacto)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Usuario o clave incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = Usuario(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
