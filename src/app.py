# from app import index
from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
# import pygal
from flask_bootstrap import Bootstrap
from flask import Markup

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
# df = pd.read_excel('base/dados_login.xlsx')

contador = 0

@app.before_first_request
def create_tables():
    db.create_all()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(84), nullable=False)
    cpf = db.Column(db.String(84), nullable=False)
    dt_nascimento = db.Column(db.String(84), nullable=False)
    email = db.Column(db.String(84), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_authenticated = db.Column(db.Boolean, default=False)
    profile = db.relationship('Profile', backref='user', uselist=False)

    def __str__(self):
        return self.name

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    # def is_authenticated(self):
    #     """Return True if the user is authenticated."""
    #     return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    
class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Unicode(124), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __str__(self):
        return self.name

@login_manager.user_loader
def current_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":

        user = User()

        user.email = request.form["email"]
        user.name = request.form["username"]
        user.cpf = request.form["cpf"]
        user.is_authenticated = False
        user.dt_nascimento = request.form["birthday"]
        user.password = generate_password_hash(request.form["password"])
        user_password = request.form["password"]
        user_confirmPassword = request.form["confirmPassword"]

        if user_password!=user_confirmPassword:
            flash("Senhas estão divergentes")
        else:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # df = pd.read_excel('base/dados_login.xlsx')
        email = request.form["username"]
        password = request.form["password"]
        if str(email)!='':

            # user = df[df['Email']==email]
            user = User.query.filter_by(email=email).first()

            if not user:
                flash("O e-mail não foi cadastrado. Clique em Criar Conta!")
                return redirect(url_for("index"))
            else: 
                if not check_password_hash(user.password, password):
                    flash("A senha está incorreta!")
                    return redirect(url_for("index"))
                else:
                    login_user(user)
                    return redirect(url_for("home", id=user.id))
        else:
            flash("Digite um e-mail válido!", 'error')
            return redirect(url_for("index"))


@app.route('/home/<int:id>', methods=["GET", "POST"])
# @login_required
def home(id):
    df = pd.read_excel('base/rotas.xlsx', sheet_name='Planilha1')
    df_aux_rota1 = pd.DataFrame()
    df_aux_rota2 = pd.DataFrame()
    valor_total_rota1=0
    valor_total_rota2=0
    tempo_rota1=0
    tempo_rota2=0
    end_ida = ''
    end_volta = ''
    if request.method == "POST":
        
        selecao = request.form.get("selecao")
        if selecao!='Rota':
            df = df[df['origem']==int(selecao)]
            df_aux_rota1 = df[df['rota']==1].iterrows()
            df_aux_rota2 = df[df['rota']==2].iterrows()
            valor_total_rota1 = list(df[df['rota']==1]['valor_total'])[0]
            valor_total_rota2 = list(df[df['rota']==2]['valor_total'])[0]
            tempo_rota1 = list(df[df['rota']==1]['tempo_estimado'])[0]
            tempo_rota2 = list(df[df['rota']==2]['tempo_estimado'])[0]
            end_ida = list(df['end_ida'])[0]
            end_volta = list(df['end_volta'])[0]

    return render_template("home.html", id=id, df=df, df_rota1=df_aux_rota1, df_rota2=df_aux_rota2, valor_total_rota1=valor_total_rota1, valor_total_rota2=valor_total_rota2, tempo_rota1=tempo_rota1, tempo_rota2=tempo_rota2, end_ida=end_ida, end_volta=end_volta)


@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/account/<int:id>", methods=["GET", "POST"])
# @login_required
def account(id):

    user = User.query.filter_by(id=id).first()
    if request.method == "POST":
        
        user.name = request.form["username"]
        user.dt_nascimento = request.form["birthday"]
        print('oi')
        db.session.commit()

    return render_template("account.html", user=user)
    
@app.route("/favorites/<int:id>")
# @login_required
def favorites(id):
    user = User.query.filter_by(id=id).first()
    return render_template("favorites.html", user=user)



if __name__ == "__main__":
    # app.run(debug=True, host = "192.168.0.15")
    app.run(debug=True, port="5001")