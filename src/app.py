# from app import index
from datetime import timedelta
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pygal
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config["SECRET_KEY"] = 'secret'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager(app)
df = pd.read_excel('base/dados_login.xlsx')

contador = 0

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == "POST":

        df = pd.read_excel('base/dados_login.xlsx')

        user_email = request.form["email"]
        user_name = request.form["username"]
        user_cpf = request.form["cpf"]
        user_datanascimento = request.form["birthday"]
        user_password_code = generate_password_hash(request.form["password"])
        user_password = request.form["password"]
        user_confirmPassword = request.form["confirmPassword"]

        if user_password!=user_confirmPassword:
            flash("Senhas estão divergentes")
        else:
            user_id =  int(df.shape[0]+1)
            dict_a = {
                'ID': [user_id],
                'Email': [user_email],
                'Nome': [user_name],
                'CPF': [user_cpf],
                'Data de Nascimento': [user_datanascimento],
                'Senha': [user_password_code]
                }
            dados = pd.DataFrame(dict_a)
            df = pd.concat([df, dados])
            df.to_excel('base/dados_login.xlsx', index=False)
            return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        df = pd.read_excel('base/dados_login.xlsx')
        email = request.form["username"]
        password = request.form["password"]
        if str(email)!='':

            user = df[df['Email']==email]
            print(user.shape[0])

            if user.shape[0]==0:
                flash("O e-mail não foi cadastrado. Clique em Criar Conta!")
                return redirect(url_for("index"))
            else: 
                print(check_password_hash(list(user.Senha)[0], password))
                if not check_password_hash(list(user.Senha)[0], password):
                    flash("A senha está incorreta!")
                    return redirect(url_for("index"))
                else:
                    contador = 1
                    return render_template("home.html")

        else:
            flash("Digite um e-mail válido!", 'error')
            return redirect(url_for("index"))

@app.route('/home')
def home():
    print(contador)
    if contador>0:
        return render_template("home.html")
    else:
        return redirect(url_for("index"))
@app.route("/logout")
# @login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@login_manager.user_loader
def current_user(user_id):
    return df[df['ID']==user_id]['ID']



if __name__ == "__main__":
    # app.run(debug=True, host = "192.168.0.15")
    app.run(debug=True, port="5001")