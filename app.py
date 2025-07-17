from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///solicitacoes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'leorsuporte@gmail.com'
app.config['MAIL_PASSWORD'] = 'Ld569647$'

db = SQLAlchemy(app)
mail = Mail(app)

class Solicitacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    whatsapp = db.Column(db.String(50), nullable=False)
    solicitacao = db.Column(db.Text, nullable=False)
    anotacoes = db.Column(db.Text, nullable=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form.get('nome')
        whatsapp = request.form.get('whatsapp')
        solicitacao = request.form.get('solicitacao')
        anotacoes = request.form.get('anotacoes')

        if not nome or not whatsapp or not solicitacao:
            flash('Por favor, preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('index'))

        nova = Solicitacao(nome=nome, whatsapp=whatsapp, solicitacao=solicitacao, anotacoes=anotacoes)
        db.session.add(nova)
        db.session.commit()

        try:
            msg = Message(subject=f"Nova solicitação de {nome}",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=['leonardosuportepav+khfzgfel5qentrx4lcnj@boards.trello.com'])
            corpo = f"""
            Nome: {nome}
            WhatsApp: {whatsapp}
            Solicitação Requerida:
            {solicitacao}

            Anotações:
            {anotacoes or '(sem anotações)'}
            """
            msg.body = corpo
            mail.send(msg)
            flash('Solicitação enviada e salva com sucesso!', 'success')
        except Exception as e:
            print('Erro ao enviar email:', e)
            flash('Erro ao enviar email, mas a solicitação foi salva.', 'warning')

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=10000)
