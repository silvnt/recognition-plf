import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# Registrar cadastro no banco
def commit_dados(*args):
        connection = sqlite3.connect('cadastro.db')
        connection.text_factory = str
        c = connection.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS dados (_id integer , nome text, cpf integer, curso varchar(30))')
        c.execute('INSERT INTO dados (_id ,nome, cpf, cidade) VALUES (?,?,?,?)', (args))
        connection.commit()

class JanelaCadastro(Gtk.Window):
        def __init__(self):

                Gtk.Window.__init__(self, title="Novo Cadastro")
                Gtk.Window.set_size_request(self,600,200)

                self.grid_total = Gtk.Grid()
                self.add(self.grid_total)
                self.grid1 = Gtk.Grid()

                self.grid2 = Gtk.Grid(column_homogeneous=True,column_spacing=0,row_spacing=10)
                
                # Campo Nome
                self.label_nome = Gtk.Label(label="Nome *")
                self.label_nome.set_halign(Gtk.Align.END)              
                self.grid2.attach(self.label_nome,0,0,1,1)
                self.entry_nome = Gtk.Entry()
                self.entry_nome.set_max_length(150)
                self.entry_nome.set_width_chars(30)            
                self.entry_nome.set_halign(Gtk.Align.START)
                self.grid2.attach(self.entry_nome, 1,0,1,1)
                self.entry_nome.connect("changed",self.on_entry_nome_changed)
                
                # Campo CPF
                self.label_cpf = Gtk.Label(label="CPF *")
                self.label_cpf.set_halign(Gtk.Align.END)
                self.grid2.attach(self.label_cpf,0,3,1,1)
                self.entry_cpf = Gtk.Entry()
                self.entry_cpf.set_max_length(max=11)
                self.entry_cpf.set_width_chars(11)
                self.entry_cpf.set_halign(Gtk.Align.START)
                self.grid2.attach(self.entry_cpf,1,3,1,1)
                
                # Campo Curso
                self.combo2 = Gtk.ComboBoxText()
                self.label_combo2 = Gtk.Label(label="Curso *")
                self.label_combo2.set_halign(Gtk.Align.END)
                self.grid2.attach(self.label_combo2,0,8,1,1)
                self.combo2.insert(0,"0","Administracao")
                self.combo2.insert(1,"1","Sistemas de Informacao")
                self.combo2.set_halign(Gtk.Align.START)
                self.grid2.attach(self.combo2,1,8,1,1)
                
                # Botao Gravar
                self.commit = Gtk.Button(label="Gravar")
                self.commit.set_halign(Gtk.Align.CENTER)
                self.grid_total.attach(self.commit,0,2,2,2)
                self.commit.set_size_request(100,40)
                self.commit.connect("clicked", self.on_commit_clicked)
                
                
                
                self.grid2.set_row_spacing(10)
                self.grid1.set_row_spacing(10)
                self.box3 = Gtk.Box()
                
                self.grid_total.set_row_spacing(30)
                self.grid_total.attach(self.grid1, 0,0,2,1)
                self.grid_total.attach(self.grid2, 0,1,1,1)
                self.grid_total.attach(self.box3, 0,10,1,1)
 
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
                        return commit_dados(None,nome,cpf,curso)
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
        button = Gtk.ToggleButton.new_with_label("Monitorar Agora")
        button.connect("toggled", self.on_monitorar_toggled, "monitorar")
        hbox.pack_start(button, True, True, 0)

    # Ao clicar Novo Cadastro, abrir janela de cadastro
    def on_cadastrar_clicked(self, button):
        print("Aberto novo cadastro")
        win = JanelaCadastro()
        win.show_all()

    # Ao clicar Monitorar Agora, iniciar monitoramento
    def on_monitorar_toggled(self, button, name):
        if button.get_active():
            print("aberto monitoramento")
        else:
            print("aberto monitoramento") 

# Executar Janela Principal
win = JanelaPrincipal()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
