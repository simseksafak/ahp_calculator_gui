import tkinter as tk
from tkinter import messagebox, Scrollbar, Toplevel
import numpy as np

class AHPApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('AHP Calculator')

        self.kriter_sayisi = tk.IntVar()
        self.alternatif_sayisi = tk.IntVar()
        self.karsilastirma_inputs = []
        self.performans_inputs = []

        self.input_frame = tk.Frame(self.window)
        self.input_frame.pack()

        tk.Label(self.input_frame, text="Kriter sayısını girin: ").pack()
        tk.Entry(self.input_frame, textvariable=self.kriter_sayisi).pack()

        tk.Label(self.input_frame, text="Alternatif sayısını girin: ").pack()
        tk.Entry(self.input_frame, textvariable=self.alternatif_sayisi).pack()

        tk.Button(self.input_frame, text='Onayla', command=self.create_input_fields).pack()

    def create_input_fields(self):
        self.new_window = Toplevel(self.window)
        self.new_window.title("Karşılaştırma ve Performans Skorları")

        self.canvas = tk.Canvas(self.new_window)
        self.canvas.pack(side=tk.LEFT)

        scrollbar = Scrollbar(self.new_window, command=self.canvas.yview)
        scrollbar.pack(side=tk.LEFT, fill='y')

        self.canvas.configure(yscrollcommand = scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

        self.input_frame_scrollable = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.input_frame_scrollable, anchor="nw")
        
        kriter_sayisi = self.kriter_sayisi.get()
        alternatif_sayisi = self.alternatif_sayisi.get()

        tk.Label(self.input_frame_scrollable, text="İkili karşılaştırma skorlarını girin: ").pack()
        for i in range(kriter_sayisi):
            for j in range(i+1, kriter_sayisi):
                input_var = tk.DoubleVar()
                tk.Label(self.input_frame_scrollable, text=f"{i+1}. ve {j+1}. kriter arasındaki skoru girin: ").pack()
                tk.Entry(self.input_frame_scrollable, textvariable=input_var).pack()
                self.karsilastirma_inputs.append(input_var)

        tk.Label(self.input_frame_scrollable, text="Alternatif performans skorlarını girin: ").pack()
        for i in range(alternatif_sayisi):
            for j in range(kriter_sayisi):
                input_var = tk.DoubleVar()
                tk.Label(self.input_frame_scrollable, text=f"{i+1}. alternatifin {j+1}. kriterdeki performansını girin: ").pack()
                tk.Entry(self.input_frame_scrollable, textvariable=input_var).pack()
                self.performans_inputs.append(input_var)

        tk.Button(self.input_frame_scrollable, text='Hesapla', command=self.calculate).pack()
        

    def calculate(self):
        kriter_sayisi = self.kriter_sayisi.get()
        alternatif_sayisi = self.alternatif_sayisi.get()

        # gather comparison scores and check the number of scores
        ikili_karsilastirma_skorlari = [v.get() for v in self.karsilastirma_inputs]
        if len(ikili_karsilastirma_skorlari) != kriter_sayisi * (kriter_sayisi - 1) // 2:
            messagebox.showerror("Error", "Incorrect number of comparison scores.")
            return

        # build comparison matrix
        karsilastirma_matrisi = np.identity(kriter_sayisi)
        skorlar_copy = ikili_karsilastirma_skorlari.copy()  # Copy the list so we don't empty the original one
        for i in range(kriter_sayisi):
            for j in range(i + 1, kriter_sayisi):
                karsilastirma_matrisi[i, j] = skorlar_copy.pop(0)  # Change pop() to pop(0)
                karsilastirma_matrisi[j, i] = 1 / karsilastirma_matrisi[i, j]

        # gather performance scores and reshape them into the right shape
        alternatif_performans_skorlari = np.array([v.get() for v in self.performans_inputs]).reshape(alternatif_sayisi, kriter_sayisi)

        # call ahp function
        kriter_agirliklari, CR, alternatif_siralamasi = self.ahp(kriter_sayisi, karsilastirma_matrisi, alternatif_performans_skorlari)


        print(f'Kriter ağırlıkları: {kriter_agirliklari}')
        print(f'Tutarlılık oranı: {CR}')
        print(f'Alternatif sıralaması: {alternatif_siralamasi}')

        messagebox.showinfo("Results", "Kriter Ağırlıkları: {}\nAlternatif Sıralaması: {}".format(kriter_agirliklari, alternatif_siralamasi))
        
    def ahp(self, kriter_sayisi, karsilastirma_matrisi, alternatif_performans_skorlari):
        # Kriter ağırlıklarını hesapla
        kriter_agirliklari = np.mean(karsilastirma_matrisi / karsilastirma_matrisi.sum(axis=0), axis=1)

        # Alternatif performans skorlarını kullanarak alternatif ağırlıklarını hesapla
        alternatif_agirliklari = np.dot(alternatif_performans_skorlari, kriter_agirliklari)

        # Tutarlılık oranını hesapla
        AW = np.dot(karsilastirma_matrisi, kriter_agirliklari)
        lambda_max = np.mean(AW / kriter_agirliklari)
        CI = (lambda_max - kriter_sayisi) / (kriter_sayisi - 1)
        RI = [0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
        CR = CI / RI[kriter_sayisi - 1]

        # Alternatif sıralamasını oluştur
        alternatif_siralamasi = np.argsort(alternatif_agirliklari)[::-1] + 1

        return kriter_agirliklari, CR, alternatif_siralamasi

        
        print(f'Kriter ağırlıkları: {kriter_agirliklari}')
        print(f'Tutarlılık oranı: {CR}')
        print(f'Alternatif sıralaması: {alternatif_siralamasi}')

        messagebox.showinfo("Results", "Kriter Ağırlıkları: {}\nAlternatif Sıralaması: {}".format(kriter_agirliklari, alternatif_siralamasi))
        
    def run(self):
        self.window.mainloop()

app = AHPApp()
app.run()
