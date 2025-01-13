import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import threading
import queue
import time

# Global değişkenler
output_queue = queue.Queue()
found_panels = []
stop_event = threading.Event()
panel_found = threading.Event()

def brute_force_panel(url, wordlist_path, output_text, output_file):
    with open(wordlist_path, 'r') as file:
        wordlist = file.readlines()

    for word in wordlist:
        if stop_event.is_set() or panel_found.is_set():
            break

        word = word.strip()
        full_url = f"{url}/{word}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                output_queue.put(f"[+] Olası panel bulundu: {full_url}\n")
                found_panels.append(full_url)
                panel_found.set()
            else:
                output_queue.put(f"[-] {full_url} - {response.status_code}\n")
        except requests.exceptions.RequestException as e:
            output_queue.put(f"[!] Hata: {e}\n")
        time.sleep(0.1)  # Hız sınırlaması

    # Bulunan panelleri dosyaya kaydet
    if found_panels:
        with open(output_file, 'w') as file:
            for panel in found_panels:
                file.write(f"{panel}\n")

    if panel_found.is_set():
        output_queue.put("Admin paneli bulundu, işlem durduruldu.\n")
    else:
        output_queue.put("İşlem tamamlandı.\n")

def update_output():
    try:
        while True:
            msg = output_queue.get(block=False)
            output_text.insert(tk.END, msg)
            output_text.see(tk.END)
    except queue.Empty:
        pass
    root.after(100, update_output)

def start_brute_force():
    target_url = url_entry.get()
    wordlist_path = wordlist_entry.get()
    output_file = output_file_entry.get()

    if not target_url or not wordlist_path or not output_file:
        messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
        return

    output_text.delete(1.0, tk.END)
    stop_event.clear()
    panel_found.clear()
    threading.Thread(target=brute_force_panel, args=(target_url, wordlist_path, output_text, output_file)).start()

def stop_brute_force():
    stop_event.set()
    output_queue.put("İşlem durduruldu.\n")

def browse_wordlist():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    wordlist_entry.delete(0, tk.END)
    wordlist_entry.insert(0, file_path)

def browse_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file_path)

# Tkinter penceresi oluştur
root = tk.Tk()
root.title("Admin Panel Bulma Aracı")
root.configure(bg='black')

# URL girişi
url_label = tk.Label(root, text="Hedef URL:", bg='black', fg='green')
url_label.grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50, bg='black', fg='green', insertbackground='green')
url_entry.grid(row=0, column=1, padx=10, pady=10)

# Wordlist girişi
wordlist_label = tk.Label(root, text="Wordlist Dosyası:", bg='black', fg='green')
wordlist_label.grid(row=1, column=0, padx=10, pady=10)
wordlist_entry = tk.Entry(root, width=50, bg='black', fg='green', insertbackground='green')
wordlist_entry.grid(row=1, column=1, padx=10, pady=10)
browse_wordlist_button = tk.Button(root, text="Gözat", command=browse_wordlist, bg='black', fg='green')
browse_wordlist_button.grid(row=1, column=2, padx=10, pady=10)

# Çıktı dosyası girişi
output_file_label = tk.Label(root, text="Çıktı Dosyası:", bg='black', fg='green')
output_file_label.grid(row=2, column=0, padx=10, pady=10)
output_file_entry = tk.Entry(root, width=50, bg='black', fg='green', insertbackground='green')
output_file_entry.grid(row=2, column=1, padx=10, pady=10)
browse_output_file_button = tk.Button(root, text="Gözat", command=browse_output_file, bg='black', fg='green')
browse_output_file_button.grid(row=2, column=2, padx=10, pady=10)

# Başlat ve Durdur butonları
start_button = tk.Button(root, text="Başlat", command=start_brute_force, bg='black', fg='green')
start_button.grid(row=3, column=0, padx=10, pady=10)
stop_button = tk.Button(root, text="Durdur", command=stop_brute_force, bg='black', fg='green')
stop_button.grid(row=3, column=1, padx=10, pady=10)

# Çıktı alanı
output_text = tk.Text(root, height=15, width=70, bg='black', fg='green')
output_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Çıktıyı güncelle
root.after(100, update_output)

# Pencereyi çalıştır
root.mainloop()
