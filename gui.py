# coding=utf-8
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sqlite3
import numpy as np
import cv2
import os
import threading

# THOMAS
caminhoDetector = 'venv/lib/python2.7/site-packages/cv2/data/haarcascade_frontalface_default.xml'

# PESSOAS COM AS IMAGENS DE TREINO
# pessoas = []

# ATA DE FREQUENCIA
frequencia = []


# FUNCAO DE DETECCAO DE FACE
def detectarFace(frame):
    face_cascade = cv2.CascadeClassifier(caminhoDetector)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces


def reconhecerRosto(cpf):
    camera = cv2.VideoCapture(0)
    numero = 0
    pastaTreinamento = os.getcwd() + '/cadastros'
    if os.path.exists(pastaTreinamento + '/' + cpf) == False:
        os.mkdir(pastaTreinamento + '/' + cpf)
    while (camera.isOpened()):
        ret, frame = camera.read()
        frameCopia = frame.copy()
        if (ret):
            faces = detectarFace(frame)
            for (x, y, w, h) in faces:
                cv2.rectangle(frameCopia, (x, y), (x + w, y + h), (0, 255, 0), 2)  # MOSTRA A FACE RECONHECIDA
                if len(faces) == 1:
                    caminho = pastaTreinamento + '/' + cpf
                    string = str(numero)  # NUMERO DO ARQUIVO
                    salvar = caminho + '/' + string + '.png'
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    cv2.imwrite(salvar, gray[y:y + w, x:x + h])
                    numero = numero + 1
                # cv2.imshow('camera', frameCopia)

            if numero == 100:
                break

            # if cv2.waitKey(1) & 0xff == ord('q'):
            #    break
    camera.release()
    cv2.destroyAllWindows()


# FUNCAO QUE FAZ A CRIACAO DAS AMOSTRAS, PEGA AS IMAGENS NO DIRETORIO E DETECTA A FACE E COLOCA NO VETOR
# DE TREINO QUE SERA UTILIZADO NO RECONHECIMENTO
def gerarAmostra():
    print('Analisando amostras, aguarde...')
    rostos = []
    labels = []
    caminho = os.getcwd() + '/cadastros'
    ordem = os.listdir(caminho)  # VAI NO DIRETORIO
    for pastaPessoa in ordem:
        caminhoPessoa = caminho + '/' + pastaPessoa
        listaImagens = os.listdir(caminhoPessoa)
        for imagemPessoa in listaImagens:
            caminhoImagem = caminhoPessoa + '/' + imagemPessoa
            rosto = cv2.imread(caminhoImagem)
            rostoGray = cv2.cvtColor(rosto, cv2.COLOR_BGR2GRAY)
            rostos.append(rostoGray)
            labels.append(int(pastaPessoa))
    cv2.destroyAllWindows()
    print('imagens analizadas')
    return rostos, labels


# REALIZA O RECONHECIMENTO, SE A PROCENTAGEM DE ERRO FOR MAIOR DE 50% ENTAO ELE RETORNA
# NAO FOI POSSIVEL RECONHECER
def reconhecer(frame, reconhecimento):
    faces = detectarFace(frame)
    detectado = []
    for (x, y, w, h) in faces:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        label, erro = reconhecimento.predict(gray[y:y + w, x:x + h])
        if (erro > 50):
            print('nao existe no banco de dados')
        else:
            #detectado.append(pessoas[label])
            nome = consultar_cpf(str(label))
            detectado.append(nome[0][0])
            print (nome[0][0])  # INFORMA QUEM E A PESSOA
    return detectado


# INICIO DA CAMERA
def cameraInit(reconhecimento):
    camera = cv2.VideoCapture(0)
    while (camera.isOpened()):
        ret, frame = camera.read()
        res = cv2.waitKey(1)
        if (ret):
            face = detectarFace(frame)
            for (x, y, w, h) in face:  # A CAMERA MOSTRA UM QUADRADO QUANDO DETECTA UM ROSTO
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow('camera', frame)
            resultado = reconhecer(frame, reconhecimento)
            chamada(resultado)  # FAZ A CHAMADA
        if res & 0xff == ord('q'):  # FINALIZA A CAMERA
            break
    camera.release()
    cv2.destroyAllWindows()


# COLOCA O NOME DA PESSOA NA CHAMADA
def chamada(lista):
    for nome in lista:
        for comp in frequencia:
            if nome == comp:
                break
        else:
            frequencia.append(nome)


#def preencherPessoas():
#    pastaPessoa = os.listdir(os.getcwd() + '/cadastros')
#    for nome in pastaPessoa:
#        pessoas.append(nome)


# THOMAS

# Registrar cadastro no banco
def commit_dados(*args):
    connection = sqlite3.connect('cadastro.db')
    connection.text_factory = str
    c = connection.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS dados (_id integer , nome text, cpf integer, curso varchar(30))')
    c.execute('INSERT INTO dados (_id ,nome, cpf, curso) VALUES (?,?,?,?)', (args))
    connection.commit()


def consultar_cpf(*args):
    connection = sqlite3.connect('cadastro.db')
    connection.text_factory = str
    c = connection.cursor()
    c.execute('SELECT nome FROM dados WHERE cpf=?', (args))
    res = c.fetchall()
    connection.commit()
    return res


class JanelaCadastro(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Novo Cadastro")
        Gtk.Window.set_size_request(self, 600, 200)

        self.grid_total = Gtk.Grid()
        self.add(self.grid_total)
        self.grid1 = Gtk.Grid()

        self.grid2 = Gtk.Grid(column_homogeneous=True, column_spacing=0, row_spacing=10)

        # Campo Nome
        self.label_nome = Gtk.Label(label="Nome *")
        self.label_nome.set_halign(Gtk.Align.END)
        self.grid2.attach(self.label_nome, 0, 0, 1, 1)
        self.entry_nome = Gtk.Entry()
        self.entry_nome.set_max_length(150)
        self.entry_nome.set_width_chars(30)
        self.entry_nome.set_halign(Gtk.Align.START)
        self.grid2.attach(self.entry_nome, 1, 0, 1, 1)
        self.entry_nome.connect("changed", self.on_entry_nome_changed)

        # Campo CPF
        self.label_cpf = Gtk.Label(label="CPF *")
        self.label_cpf.set_halign(Gtk.Align.END)
        self.grid2.attach(self.label_cpf, 0, 3, 1, 1)
        self.entry_cpf = Gtk.Entry()
        self.entry_cpf.set_max_length(max=11)
        self.entry_cpf.set_width_chars(11)
        self.entry_cpf.set_halign(Gtk.Align.START)
        self.grid2.attach(self.entry_cpf, 1, 3, 1, 1)

        # Campo Curso
        self.combo2 = Gtk.ComboBoxText()
        self.label_combo2 = Gtk.Label(label="Curso *")
        self.label_combo2.set_halign(Gtk.Align.END)
        self.grid2.attach(self.label_combo2, 0, 8, 1, 1)
        self.combo2.insert(0, "0", "Administracao")
        self.combo2.insert(1, "1", "Sistemas de Informacao")
        self.combo2.set_halign(Gtk.Align.START)
        self.grid2.attach(self.combo2, 1, 8, 1, 1)

        # Botao Gravar
        self.commit = Gtk.Button(label="Gravar")
        self.commit.set_halign(Gtk.Align.CENTER)
        self.grid_total.attach(self.commit, 0, 2, 2, 2)
        self.commit.set_size_request(100, 40)
        self.commit.connect("clicked", self.on_commit_clicked)

        self.grid2.set_row_spacing(10)
        self.grid1.set_row_spacing(10)
        self.box3 = Gtk.Box()

        self.grid_total.set_row_spacing(30)
        self.grid_total.attach(self.grid1, 0, 0, 2, 1)
        self.grid_total.attach(self.grid2, 0, 1, 1, 1)
        self.grid_total.attach(self.box3, 0, 10, 1, 1)

    def on_entry_nome_changed(self, widget):
        nome = widget.get_text()
        nome = nome.upper()
        return widget.set_text(nome)

    # Ao botao Gravar clicado, registrar no banco
    def on_commit_clicked(self, widget):
        nome = self.entry_nome.get_text()
        cpf = self.entry_cpf.get_text()
        curso = self.combo2.get_active_text()

        if nome != None and cpf != None and curso != None:
            commit_dados(None, nome, cpf[:7], curso)
            reconhecerRosto(cpf[:7])
            return
        pass





class JanelaPrincipal(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="")
        self.set_border_width(10)

        hbox = Gtk.Box(spacing=6)
        self.add(hbox)

        # Botao de Cadastro
        button = Gtk.Button.new_with_label("Novo Cadastro")
        button.connect("clicked", self.on_cadastrar_clicked)
        hbox.pack_start(button, True, True, 0)

        # Botao de Monitoramento
        button = Gtk.Button.new_with_label("Monitorar Agora")
        button.connect("clicked", self.on_monitorar_clicked)
        hbox.pack_start(button, True, True, 0)

    # Ao clicar Novo Cadastro, abrir janela de cadastro
    def on_cadastrar_clicked(self, button):
        print("Aberto novo cadastro")
        win = JanelaCadastro()
        win.show_all()

    # Ao clicar Monitorar Agora, iniciar monitoramento
    def on_monitorar_clicked(self, button):
        # THOMAS
        # preencherPessoas()
        rostos, labels = gerarAmostra()
        print(type(np.array(labels)))
        reconhecimento = cv2.face.LBPHFaceRecognizer_create()
        reconhecimento.train(rostos, np.array(labels))
        print("aberto monitoramento")
        threading.Thread(target=cameraInit(reconhecimento)).start()

def print_freq():
    while 0:
        print(frequencia)

# thomas
if os.path.exists(os.getcwd() + '/cadastros') == False:
    os.mkdir(os.getcwd() + '/cadastros')
# Executar Janela Principal
win = JanelaPrincipal()
win.connect("destroy", Gtk.main_quit)
win.show_all()

threading.Thread(target=Gtk.main()).start()