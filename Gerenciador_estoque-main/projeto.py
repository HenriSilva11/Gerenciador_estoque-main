import flask
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "uma_chave_secreta_muito_forte_e_aleatoria"

app.config['SQLALCHEMY_DATABASE_URI'] = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD = 'mysql+mysqlconnector',
        usuario = 'root',
        senha = '59380131',
        servidor = 'localhost',
        database = 'db_estoque'
    )

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Produto(db.Model):
    __tablename__ = "tabela_estoque"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nm_produto = db.Column(db.String(200), nullable=False)
    qtd_produto = db.Column(db.Integer, nullable=False)
    ds_categoria = db.Column(db.String(200), nullable=False)
    ds_marca = db.Column (db.String(200), nullable=False)
    vl_produto = db.Column (db.Numeric(10,2), nullable=False)

    def __repr__(self):
        return "<Produto %r>" % self.nm_produto

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="comum") 

@app.route('/ola')
def mostrar():
    return "<h1>Iniciando aplicação flask</h1>"

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = generate_password_hash(request.form["senha"])
        role = request.form.get("role", "comum")

        novo_usuario = Usuario(nome=nome, email=email, senha=senha, role=role)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("registrar.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            return redirect(url_for("lista_produtos"))
        flash("Credenciais inválidas", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/cadastrar")
@login_required
def cadastrar_produto():
    return render_template("cadastrar.html")

@app.route("/adicionar", methods=["GET", "POST"])
@login_required
def adicionar_produto():
    if request.method == "POST":
        nm_produto = request.form['txtNome']
        qtd_produto = request.form['txtQuantidade']
        ds_categoria = request.form['txtCategoria']
        ds_marca = request.form['txtMarca']
        vl_produto = float(request.form['txtValor'].replace(",", "."))

        novo_produto = Produto(
            nm_produto=nm_produto,
            qtd_produto=qtd_produto,
            ds_categoria=ds_categoria,
            ds_marca=ds_marca,
            vl_produto=vl_produto
        )
        db.session.add(novo_produto)
        db.session.commit()
        return redirect(url_for("lista_produtos"))

    return render_template("cadastrar.html")

@app.route('/lista')
@login_required
def lista_produtos():
    lista = Produto.query.order_by(Produto.id)
    return render_template('lista.html', titulo="Lista de Produtos", todos_produtos=lista)

@app.route('/excluir/<int:id>')
@login_required
def excluir_produto(id):
    if current_user.role != "admin":
        flash("Acesso negado! Apenas administradores podem excluir produtos.", "danger")
        return redirect(url_for("lista_produtos"))

    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído com sucesso!', 'success')
    return redirect(url_for('lista_produtos'))

if __name__ == "__main__":
    app.run(debug=True)
