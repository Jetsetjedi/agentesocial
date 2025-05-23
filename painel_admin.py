from tkinter import Tk, Toplevel, Label, Entry, Button, Listbox, END, SINGLE, messagebox
from negocio import Negocio

class PainelAdmin:
    def __init__(self, master=None):
        self.master = master
        self.negocio = Negocio()
        self.usuario_editando = None  # Para saber se está editando

    def abrir(self):
        self.janela = Toplevel(self.master) if self.master else Tk()
        self.janela.title("Painel de Clientes")
        self.janela.geometry("800x500")
        self.janela.resizable(False, False)

        # Listagem de usuários
        self.listbox = Listbox(self.janela, width=120, selectmode=SINGLE)
        self.listbox.pack(padx=10, pady=10)
        self.listbox.bind('<Double-1>', self.on_double_click)
        self.atualizar_lista()

        # Campos para cadastro/edição
        Label(self.janela, text="Usuário:").pack()
        self.entry_usuario = Entry(self.janela)
        self.entry_usuario.pack()
        Label(self.janela, text="Senha:").pack()
        self.entry_senha = Entry(self.janela, show="*")
        self.entry_senha.pack()
        Label(self.janela, text="Status (L/B):").pack()
        self.entry_status = Entry(self.janela)
        self.entry_status.pack()
        Label(self.janela, text="Data Expiração (YYYY-MM-DD):").pack()
        self.entry_exp = Entry(self.janela)
        self.entry_exp.pack()
        Label(self.janela, text="Plano:").pack()
        self.entry_plano = Entry(self.janela)
        self.entry_plano.pack()

        Button(self.janela, text="Cadastrar", command=self.cadastrar).pack(pady=2)
        Button(self.janela, text="Editar", command=self.editar).pack(pady=2)
        Button(self.janela, text="Excluir", command=self.excluir).pack(pady=2)

        if not self.master:
            self.janela.mainloop()

    def atualizar_lista(self):
        self.listbox.delete(0, END)
        self.usuarios = self.negocio.listar_usuarios()
        for u in self.usuarios:
            self.listbox.insert(END, f"{u['id']} | {u['usuario']} | {u['statuscli']} | {u['data_expiracao']} | {u['plano']}")

    def limpar_campos(self):
        self.entry_usuario.delete(0, END)
        self.entry_senha.delete(0, END)
        self.entry_status.delete(0, END)
        self.entry_exp.delete(0, END)
        self.entry_plano.delete(0, END)
        self.usuario_editando = None

    def validar_campos(self, cadastro=True):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        status = self.entry_status.get().strip().upper()
        data_exp = self.entry_exp.get().strip()
        plano = self.entry_plano.get().strip()
        if not usuario or (cadastro and not senha) or status not in ["L", "B"] or not data_exp or not plano:
            messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos corretamente!\nStatus: L (Liberado) ou B (Bloqueado)")
            return None
        return usuario, senha, status, data_exp, plano

    def cadastrar(self):
        campos = self.validar_campos(cadastro=True)
        if not campos:
            return
        usuario, senha, status, data_exp, plano = campos
        if self.negocio.inserir_usuario(usuario, senha, status, data_exp, plano):
            messagebox.showinfo("Sucesso", "Usuário cadastrado!")
            self.atualizar_lista()
            self.limpar_campos()
        else:
            messagebox.showerror("Erro", "Falha ao cadastrar usuário.")

    def editar(self):
        if self.usuario_editando is None:
            sel = self.listbox.curselection()
            if not sel:
                messagebox.showwarning("Selecione", "Selecione um usuário para editar (ou dê duplo clique).")
                return
            idx = sel[0]
            usuario = self.usuarios[idx]
            self.usuario_editando = usuario["id"]
        else:
            idx = next((i for i, u in enumerate(self.usuarios) if u["id"] == self.usuario_editando), None)
            usuario = self.usuarios[idx] if idx is not None else None

        campos = self.validar_campos(cadastro=False)
        if not campos:
            return
        novo_usuario, _, status, data_exp, plano = campos
        if self.negocio.atualizar_usuario(self.usuario_editando, novo_usuario, status, data_exp, plano):
            messagebox.showinfo("Sucesso", "Usuário atualizado!")
            self.atualizar_lista()
            self.limpar_campos()
        else:
            messagebox.showerror("Erro", "Falha ao atualizar usuário.")

    def excluir(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Selecione", "Selecione um usuário para excluir.")
            return
        idx = sel[0]
        usuario = self.usuarios[idx]
        id_usuario = usuario["id"]
        if messagebox.askyesno("Confirma", "Excluir este usuário?"):
            if self.negocio.excluir_usuario(id_usuario):
                messagebox.showinfo("Sucesso", "Usuário excluído!")
                self.atualizar_lista()
                self.limpar_campos()
            else:
                messagebox.showerror("Erro", "Falha ao excluir usuário.")

    def on_double_click(self, event):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        usuario = self.usuarios[idx]
        self.usuario_editando = usuario["id"]
        self.entry_usuario.delete(0, END)
        self.entry_usuario.insert(0, usuario["usuario"])
        self.entry_senha.delete(0, END)  # Não mostra senha por segurança
        self.entry_status.delete(0, END)
        self.entry_status.insert(0, usuario["statuscli"])
        self.entry_exp.delete(0, END)
        self.entry_exp.insert(0, usuario["data_expiracao"])
        self.entry_plano.delete(0, END)
        self.entry_plano.insert(0, usuario["plano"])

if __name__ == "__main__":
    PainelAdmin().abrir()