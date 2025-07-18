from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'chave_secreta_segura'

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///solicitacoes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'SEU_EMAIL@gmail.com'
app.config['MAIL_PASSWORD'] = 'SUA_SENHA_DE_APP'

db = SQLAlchemy(app)
mail = Mail(app)

# Usuário e senha fixos (pode vir de banco depois)
USUARIO = 'admin'
SENHA = '1234'

# Modelo do banco
class Solicitacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(50), nullable=False)
    solicitacao = db.Column(db.Text, nullable=False)
    anotacoes = db.Column(db.Text)

@app.before_first_request
def criar_banco():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == USUARIO and senha == SENHA:
            session['usuario_logado'] = usuario
            return redirect(url_for('formulario'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if 'usuario_logado' not in session:
        flash('Você precisa fazer login primeiro.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form['nome']
        whatsapp = request.form['whatsapp']
        solicitacao = request.form['solicitacao']
        anotacoes = request.form.get('anotacoes', '')

        nova = Solicitacao(nome=nome, whatsapp=whatsapp, solicitacao=solicitacao, anotacoes=anotacoes)
        db.session.add(nova)
        db.session.commit()

        try:
            msg = Message(subject=f"Solicitação de {nome}",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=['leonardosuportepav+khfzgfel5qentrx4lcnj@boards.trello.com'],
                          body=f"""Nome: {nome}
WhatsApp: {whatsapp}
Solicitação: {solicitacao}
Anotações: {anotacoes if anotacoes else 'Nenhuma'}
""")
            mail.send(msg)
            flash("Solicitação enviada com sucesso!", "success")
        except Exception as e:
            print("Erro ao enviar email:", e)
            flash("Erro ao enviar email. Mas a solicitação foi salva.", "warning")

        return redirect(url_for('formulario'))

    return render_template('formulario.html')

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
