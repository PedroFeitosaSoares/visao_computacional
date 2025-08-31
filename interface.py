import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import cv2
import numpy as np

class AppVisaoComputacional(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Interface de Visão Computacional")
        self.geometry("800x600")

        self.caminho_imagem = None
        self.imagem_original = None
        self.imagem_processada = None
        self.imagem_tk = None

        frame_botoes = tk.Frame(self)
        frame_botoes.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        btn_carregar = tk.Button(frame_botoes, text="Carregar Imagem", command=self.carregar_imagem)
        btn_carregar.pack(side=tk.LEFT, padx=5)

        btn_salvar = tk.Button(frame_botoes, text="Salvar Imagem", command=self.salvar_imagem)
        btn_salvar.pack(side=tk.LEFT, padx=5)

        btn_zerar = tk.Button(frame_botoes, text="Zerar Intensidade", command=self.zerar_intensidade)
        btn_zerar.pack(side=tk.LEFT, padx=5)

        btn_restaurar = tk.Button(frame_botoes, text="Restaurar Original", command=self.restaurar_original)
        btn_restaurar.pack(side=tk.LEFT, padx=5)

        self.label_imagem = tk.Label(self)
        self.label_imagem.pack(padx=10, pady=10, expand=True)

    def carregar_imagem(self):
        self.caminho_imagem = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.gif"), ("Todos os arquivos", "*.*")]
        )
        if not self.caminho_imagem:
            return

        self.imagem_original = cv2.imread(self.caminho_imagem)
        self.imagem_processada = self.imagem_original.copy()
        self.exibir_imagem(self.imagem_processada)

    def exibir_imagem(self, img_cv):
        if img_cv is None:
            return

        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        self.imagem_tk = ImageTk.PhotoImage(img_pil)

        self.label_imagem.config(image=self.imagem_tk)
        self.label_imagem.image = self.imagem_tk

    def salvar_imagem(self):
        if self.imagem_processada is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem para salvar.")
            return

        caminho_salvar = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp"), ("Todos os arquivos", "*.*")]
        )
        if not caminho_salvar:
            return

        try:
            cv2.imwrite(caminho_salvar, self.imagem_processada)
            messagebox.showinfo("Sucesso", f"Imagem salva em:\n{caminho_salvar}")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar a imagem.\nErro: {e}")

    def zerar_intensidade(self):
        if self.imagem_processada is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return

        self.imagem_processada = np.zeros_like(self.imagem_processada)
        self.exibir_imagem(self.imagem_processada)

    def restaurar_original(self):
        if self.imagem_original is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem original para restaurar.")
            return

        self.imagem_processada = self.imagem_original.copy()
        self.exibir_imagem(self.imagem_processada)


if __name__ == "__main__":
    app = AppVisaoComputacional()
    app.mainloop()