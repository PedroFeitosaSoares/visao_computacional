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
        self.imagem_a = None
        self.imagem_b = None
        self.mascara = None
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

        # Botão novo para a funcionalidade de blending
        btn_blending = tk.Button(frame_botoes, text="Realizar Blending", command=self.executar_blending, fg="blue", font=('Helvetica', 8, 'bold'))
        btn_blending.pack(side=tk.LEFT, padx=5)

        self.label_imagem = tk.Label(self)
        self.label_imagem.pack(padx=10, pady=10, expand=True)

    def carregar_imagem(self):
        self.caminho_imagem = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.gif"), ("Todos os arquivos", "*.*")]
        )
        if not self.caminho_imagem:
            return

        self.imagem_original = cv2.imdecode(np.fromfile(self.caminho_imagem, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.imagem_processada = self.imagem_original.copy()
        self.exibir_imagem(self.imagem_processada)

    def exibir_imagem(self, img_cv):
        if img_cv is None:
            return

        img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Redimensiona a imagem para caber na janela, mantendo proporção
        max_w, max_h = 780, 550
        img_pil.thumbnail((max_w, max_h), Image.LANCZOS)

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

    # Novo método que chama as funções de blending
    def executar_blending(self):
        
        messagebox.showinfo("Instrução", "Por favor, selecione a Imagem A (ex: maçã).")
        caminho_a = filedialog.askopenfilename(title="Selecione a Imagem A")
        if not caminho_a: return
        self.imagem_a = cv2.imdecode(np.fromfile(caminho_a, dtype=np.uint8), cv2.IMREAD_COLOR)
        
        messagebox.showinfo("Instrução", "Agora, selecione a Imagem B (ex: laranja).")
        caminho_b = filedialog.askopenfilename(title="Selecione a Imagem B")
        if not caminho_b: return
        self.imagem_b = cv2.imdecode(np.fromfile(caminho_b, dtype=np.uint8), cv2.IMREAD_COLOR)

        messagebox.showinfo("Instrução", "Por fim, selecione a Máscara.")
        caminho_m = filedialog.askopenfilename(title="Selecione a Máscara")
        if not caminho_m: return
        self.mascara   = cv2.imdecode(np.fromfile(caminho_m, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)

        if self.imagem_a is None or self.imagem_b is None or self.mascara is None:
            messagebox.showerror("Erro", "É necessário carregar as duas imagens e a máscara!")
            return

        self.imagem_processada = realizar_blending_com_piramides(self.imagem_a, self.imagem_b, self.mascara)

        
        self.exibir_imagem(self.imagem_processada)
        
        
        self.imagem_original = self.imagem_a.copy()

def realizar_blending_com_piramides(img_a, img_b, mascara, niveis=6):

    h, w = img_a.shape[:2]
    img_b = cv2.resize(img_b, (w, h))
    mascara = cv2.resize(mascara, (w, h))

    G_a = [img_a.copy().astype('float32')]
    G_b = [img_b.copy().astype('float32')]
    for i in range(niveis):
        G_a.append(cv2.pyrDown(G_a[i]))
        G_b.append(cv2.pyrDown(G_b[i]))

    L_a = [G_a[niveis-1]]
    L_b = [G_b[niveis-1]]
    for i in range(niveis-1, 0, -1):
        expand_a = cv2.pyrUp(G_a[i])
        laplacian_a = cv2.subtract(G_a[i-1], expand_a)
        L_a.append(laplacian_a)

        expand_b = cv2.pyrUp(G_b[i])
        laplacian_b = cv2.subtract(G_b[i-1], expand_b)
        L_b.append(laplacian_b)
    L_a.reverse()
    L_b.reverse()

    mascara_float = mascara.astype('float32') / 255.0
    G_m = [mascara_float]
    for i in range(niveis):
        G_m.append(cv2.pyrDown(G_m[i]))

    LS = []
    for i in range(niveis):
        gm = G_m[i]
        gm_3c = np.stack([gm, gm, gm], axis=2)
        
        la_h, la_w, _ = L_a[i].shape
        gm_3c = cv2.resize(gm_3c, (la_w, la_h))

        ls = gm_3c * L_a[i] + (1.0 - gm_3c) * L_b[i]
        LS.append(ls)

    resultado = LS[niveis-1]
    for i in range(niveis-2, -1, -1):
        resultado = cv2.pyrUp(resultado)
        h, w, _ = LS[i].shape
        resultado = cv2.resize(resultado, (w, h))
        resultado = cv2.add(resultado, LS[i])

    resultado = np.clip(resultado, 0, 255)
    return resultado.astype('uint8')


def realizar_justaposicao_direta(img_a, img_b, mascara):
    h, w = img_a.shape[:2]
    img_b = cv2.resize(img_b, (w, h))
    mascara = cv2.resize(mascara, (w, h))

    mascara_float = mascara.astype(float) / 255.0
    mascara_3c = np.stack([mascara_float]*3, axis=-1)

    img_a_float = img_a.astype(float)
    img_b_float = img_b.astype(float)

    resultado = mascara_3c * img_a_float + (1.0 - mascara_3c) * img_b_float
    
    return resultado.astype(np.uint8)


if __name__ == "__main__":
    app = AppVisaoComputacional()
    app.mainloop()


