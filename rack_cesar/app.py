from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

# Obtém o caminho base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meubanco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Aluno(db.Model):
    __tablename__ = 'alunos'
    cpf = db.Column(db.String(14), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    genero = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()


def carregar_questoes(filename):
    # Ajusta para a pasta correta
    caminho_arquivo = os.path.join(BASE_DIR, "data", filename)
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo {caminho_arquivo} não encontrado!")
        return []
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)


# Atualizando o dicionário com caminhos corretos
questoes_por_materia = {
    "portugues": carregar_questoes("q_port.json"),
    "matematica": carregar_questoes("q_mat.json"),
    "javascript": carregar_questoes("q_js.json"),
    "css": carregar_questoes("q_css.json")
}


# Definição de todas as matérias
questoes_por_materia = {
    "portugues": carregar_questoes("q_port.json"),
    "matematica": carregar_questoes("q_mat.json"),
    "javascript": carregar_questoes("q_js.json"),
    "css": carregar_questoes("q_css.json")
}

indices_por_materia = {materia: 0 for materia in questoes_por_materia}
historico_por_materia = {materia: {"acertos": 0, "erros": 0}
                         for materia in questoes_por_materia}


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/cadastro', methods=['GET', 'POST'])
def exibir_cadastro():
    if request.method == 'POST':
        # Criar o usuário
        cpf = request.form.get('cpf')
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        senha = request.form.get('senha')
        genero = request.form.get('genero')
        data_nascimento = request.form.get('data_nascimento')

        # Criar hash da senha antes de armazenar
        senha_hash = generate_password_hash(senha)

        # Verificar se o usuário já existe
        usuario_existente = Aluno.query.filter_by(cpf=cpf).first()
        if usuario_existente:
            return "Erro: CPF já cadastrado!", 400

        # Criar novo usuário e salvar no banco
        novo_usuario = Aluno(cpf=cpf, nome=nome, email=email, telefone=telefone, senha_hash=senha_hash, genero=genero, data_nascimento=data_nascimento)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')


@app.route('/recuperar_senha', methods=['GET'])
def exibir_recuperar_senha():
    return render_template('recup.html')


@app.route('/recuperar_senha', methods=['POST'])
def recuperar_senha():
    cpf = request.form.get('cpf')
    nova_senha = request.form.get('nova_senha')

    if not cpf or not nova_senha:
        return "Erro: CPF e nova senha são obrigatórios", 400

    aluno = Aluno.query.filter_by(cpf=cpf).first()
    if not aluno:
        return "Erro: CPF não encontrado", 404

    aluno.senha_hash = generate_password_hash(nova_senha)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/home')
def home():
    return render_template('home.html', stats=historico_por_materia)


@app.route('/aula')
def aula():
    return render_template('aula.html')


@app.route('/exerc')
def exerc():
    return render_template('exerc.html')


@app.route('/jogo')
def jogo():
    return render_template('jogo.html')


@app.route('/perfil')
def perfil():
    aluno = Aluno.query.first()  # Simulação: Pegue um usuário cadastrado
    return render_template('perfil.html', aluno=aluno)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        aluno = Aluno.query.filter_by(cpf=cpf).first()
        if aluno and check_password_hash(aluno.senha_hash, senha):
            return redirect(url_for('home'))
        else:
            return "Erro: CPF ou senha incorretos!", 400
    return render_template('login.html')


@app.route('/exercicios/<materia>')
def exercicios(materia):
    if materia not in questoes_por_materia:
        return "Erro: Matéria inválida!", 400

    questao_atual_index = indices_por_materia[materia]
    if 0 <= questao_atual_index < len(questoes_por_materia[materia]):
        questao = questoes_por_materia[materia][questao_atual_index]
    else:
        questao = None

    # Mapeando nomes corretos dos arquivos HTML
    templates_materia = {
        "portugues": "port.html",
        "matematica": "mat.html",
        "javascript": "js.html",
        "css": "css.html"
    }

    return render_template(templates_materia[materia], questao=questao)


@app.route('/verificar_resposta', methods=['POST'])
def verificar_resposta():
    materia = request.form.get('materia')

    if materia not in questoes_por_materia:
        return jsonify({'resultado': 'Erro: Matéria não encontrada'}), 400

    questao_atual_index = indices_por_materia[materia]
    resposta_usuario = request.form.get('answer')

    questao = questoes_por_materia[materia][questao_atual_index]

    correta = questao['resposta_correta']
    if resposta_usuario == correta:
        resultado = "✅ Resposta correta!"
        historico_por_materia[materia]["acertos"] += 1
    else:
        resultado = f"❌ Resposta incorreta. A correta é: {correta}"
        historico_por_materia[materia]["erros"] += 1

    return jsonify({'resultado': resultado, 'acertos': historico_por_materia[materia]["acertos"], 'erros': historico_por_materia[materia]["erros"]})


@app.route('/mudar_questao', methods=['POST'])
def mudar_questao():
    materia = request.form.get('materia')
    direcao = request.form.get('direcao')

    if materia not in questoes_por_materia:
        return jsonify({'texto': 'Erro: Matéria inválida'})

    if direcao == "proxima":
        if indices_por_materia[materia] < len(questoes_por_materia[materia]) - 1:
            indices_por_materia[materia] += 1
    elif direcao == "anterior":
        if indices_por_materia[materia] > 0:
            indices_por_materia[materia] -= 1

    questao = questoes_por_materia[materia][indices_por_materia[materia]]
    return jsonify(questao)


@app.route('/reiniciar_historico', methods=['POST'])
def reiniciar_historico():
    materia = request.form.get('materia')

    if materia not in questoes_por_materia:
        return jsonify({'mensagem': 'Erro: Matéria inválida'}), 400

    indices_por_materia[materia] = 0
    historico_por_materia[materia] = {"acertos": 0, "erros": 0}

    return jsonify({'mensagem': 'Histórico reiniciado com sucesso!', 'acertos': 0, 'erros': 0})


if __name__ == '__main__':
    app.run(debug=True)