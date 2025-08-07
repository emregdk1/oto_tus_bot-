import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import time
import threading
import json
import os

running = False
start_time = None
timer_running = False
CONFIG_FILE = "config.json"
PROFILES_FILE = "profiles.json"

# === PROFIL ISLEMLERI ===
def load_profiles():
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_profile(name, keys, speed):
    profiles = load_profiles()
    profiles[name] = {"keys": keys, "speed": speed}
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f)
    refresh_profile_menu()

def delete_profile_action():
    name = combo_profiles.get()
    if not name:
        messagebox.showwarning("Uyarı", "Silinecek bir profil seçmelisiniz.")
        return
    confirm = messagebox.askyesno("Onay", f"'{name}' adlı profili silmek istediğine emin misin?")
    if confirm:
        profiles = load_profiles()
        if name in profiles:
            del profiles[name]
            with open(PROFILES_FILE, "w") as f:
                json.dump(profiles, f)
            refresh_profile_menu()
            combo_profiles.set("")
            messagebox.showinfo("Başarılı", f"'{name}' profili silindi.")

def apply_profile(name):
    profiles = load_profiles()
    if name in profiles:
        entry_keys.config(state="normal")
        entry_keys.delete(0, tk.END)
        entry_keys.insert(0, profiles[name]["keys"])
        combo_speed.set(profiles[name]["speed"])
        entry_keys.config(state="readonly")

def refresh_profile_menu():
    profiles = list(load_profiles().keys())
    combo_profiles["values"] = profiles

# === AYAR DOSYASI ===
def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Ayar dosyası bozuk.")
    return {}

def save_settings(keys, speed):
    data = {"keys": keys, "speed": speed}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def parse_macro_keys(raw_input):
    keys = []
    parts = raw_input.split(',')
    for part in parts:
        part = part.strip()
        if 'x' in part:
            try:
                key, count = part.split('x')
                keys.extend([key.strip()] * int(count))
            except:
                keys.append(part)  # hatalı format varsa direkt ekle
        else:
            keys.extend(list(part.strip()))
    return keys

def update_timer():
    global timer_running
    while timer_running:
        if start_time:
            elapsed = time.time() - start_time
            mins, secs = divmod(int(elapsed), 60)
            timer_label.config(text=f"Kronometre: {mins:02d}:{secs:02d}")
        time.sleep(1)

def run_bot():
    global running
    while True:
        if running:
            update_status("Durum: ÇALIŞIYOR", "green")
            write_log("Makro çalışmaya başladı.")
            raw_input = entry_keys.get().strip()
            if not raw_input:
                write_log("Tuş dizisi boş! Lütfen bir tuş dizisi girin.")
                running = False
                update_status("Durum: DURDU", "red")
                continue
            keys = parse_macro_keys(raw_input)
            delay = 0.005 if combo_speed.get() == "Hızlı" else 0.03 if combo_speed.get() == "Orta" else 0.15
            for key in keys:
                if not running:
                    break
                try:
                    if key.isalnum():
                        keyboard.press_and_release(key)
                        write_log(f"Tetiklenen tuş: {key}")
                    else:
                        write_log(f"Desteklenmeyen tuş: {key}")
                    time.sleep(delay)
                except Exception as e:
                    write_log(f"Hatalı tuş: '{key}' — {e}")
            write_log("Makro döngüsü tamamlandı.")
        time.sleep(0.05)

def toggle_bot():
    global running, start_time, timer_running
    running = not running
    if running:
        entry_keys.config(state="readonly")
        save_settings(entry_keys.get(), combo_speed.get())
        update_status("Durum: ÇALIŞIYOR", "green")
        start_time = time.time()
        timer_running = True
        threading.Thread(target=update_timer, daemon=True).start()
    else:
        update_status("Durum: DURDU", "red")
        entry_keys.config(state="normal")
        start_time = None
        timer_running = False
        timer_label.config(text="Kronometre: 00:00")

def update_status(text, color):
    status_label.config(text=text, fg=color)

def hotkey_listener():
    keyboard.add_hotkey("F1", toggle_bot)
    keyboard.wait()

def disable_entry_on_focus_out(event):
    if entry_keys.cget("state") == "normal":
        entry_keys.config(state="readonly")

def show_help():
    messagebox.showinfo(
        "Yardım",
        "Tuş Dizisi: Tuşları aralarına virgül koyarak veya bitişik yazabilirsiniz.\n"
        "Makro: 1x3,2x1 gibi yazarsanız, 1 tuşu 3 kez, 2 tuşu 1 kez basılır.\n"
        "Profil: Ayarlarınızı kaydedip hızlıca yükleyebilirsiniz.\n"
        "Log: Botun yaptığı işlemler burada listelenir.\n"
        "Koyu Tema: Göz yormayan koyu arayüz için etkinleştirin."
    )

def export_log():
    logs = log_text.get("1.0", "end").strip()
    if logs:
        with open("bot_log.txt", "w", encoding="utf-8") as f:
            f.write(logs)
        messagebox.showinfo("Log Kaydedildi", "Loglar bot_log.txt dosyasına kaydedildi.")
    else:
        messagebox.showwarning("Log Boş", "Kaydedilecek bir log bulunamadı.")

def toggle_dark_mode():
    bg = "#222"
    fg = "#eee"
    root.configure(bg=bg)
    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("TButton", background="#333", foreground=fg)
    style.configure("TEntry", fieldbackground="#333", foreground=fg)
    frame.configure(bg=bg)
    profile_frame.configure(bg=bg)
    options_frame.configure(bg=bg)
    bottom_row.configure(bg=bg)
    log_frame.configure(bg=bg)
    right_frame.configure(bg=bg)
    status_label.configure(bg=bg, fg="#ff5555")
    timer_label.configure(bg=bg, fg=fg)
    log_text.configure(bg="#333", fg=fg)

def set_light_mode():
    bg = "#f7f7f7"
    fg = "#333"
    root.configure(bg=bg)
    style.configure("TLabel", background=bg, foreground=fg)
    style.configure("TButton", background=bg, foreground=fg)
    style.configure("TEntry", fieldbackground="#fff", foreground=fg)
    frame.configure(bg=bg)
    profile_frame.configure(bg=bg)
    options_frame.configure(bg=bg)
    bottom_row.configure(bg=bg)
    log_frame.configure(bg=bg)
    right_frame.configure(bg=bg)
    status_label.configure(bg=bg, fg="red")
    timer_label.configure(bg=bg, fg=fg)
    log_text.configure(bg=bg, fg=fg)

def show_loading_screen():
    """Yükleme ekranını gösterir."""
    loading_root = tk.Toplevel()
    loading_root.title("Yükleniyor...")
    loading_root.geometry("400x200")
    loading_root.configure(bg="#f7f7f7")

    # Yükleme ekranı içeriği
    tk.Label(loading_root, text="OTO TUŞ BOTU", font=("Calibri", 24, "bold"), bg="#f7f7f7", fg="#333").pack(pady=(40, 10))
    tk.Label(loading_root, text="Yükleniyor, lütfen bekleyin...", font=("Segoe UI", 12), bg="#f7f7f7", fg="#666").pack(pady=(0, 20))

    # Yükleme ekranını birkaç saniye sonra kapat
    loading_root.after(3000, lambda: loading_root.destroy())  # 3 saniye sonra kapanır

    # Ana pencereyi başlat
    loading_root.after(3000, start_gui)

def start_gui():
    global root, style, entry_keys, combo_speed, entry_profile, combo_profiles
    global status_label, timer_label, log_text
    global frame, profile_frame, options_frame, bottom_row, log_frame, right_frame

    root = tk.Tk()
    root.title("Oto Tuş Botu v2")

    # Uygulama simgesini ayarla
    try:
        root.iconbitmap("icon.ico")  # .ico dosyasını kullan
    except:
        print("Simgesi yüklenemedi. Lütfen 'icon.ico' dosyasını kontrol edin.")

    # Pencere boyutunu ayarla
    window_width = 800
    window_height = 750
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.configure(bg="#f7f7f7")

    # Modern tema ve stil
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 11), padding=6)
    style.configure("TLabel", font=("Segoe UI", 11), background="#f7f7f7")
    style.configure("TEntry", font=("Segoe UI", 11))

    # Başlık kısmı
    header_frame = tk.Frame(root, bg="#f7f7f7")
    header_frame.pack(fill="x", pady=(10, 20))

    # Yeni logo ekleme
    try:
        logo = tk.PhotoImage(file="new_logo.png")  # new_logo.png dosyasını proje klasörüne ekleyin
        tk.Label(header_frame, image=logo, bg="#f7f7f7").pack(side="left", padx=10)
    except:
        tk.Label(header_frame, text="🎮", font=("Calibri", 30), bg="#f7f7f7", fg="#333").pack(side="left", padx=10)

    tk.Label(header_frame, text="OTO TUŞ BOTU", font=("Calibri", 24, "bold"), bg="#f7f7f7", fg="#333").pack(side="left", padx=10)
    tk.Label(header_frame, text="v2.0", font=("Segoe UI", 12), bg="#f7f7f7", fg="#666").pack(side="left", padx=5)

    # Alt bilgi
    tk.Label(root, text="Geliştirici: TesterX | © 2025", font=("Segoe UI", 10), bg="#f7f7f7", fg="#999").pack(side="bottom", pady=10)

    # Üstteki ayar ve profil alanlarını yatayda yan yana grupla
    top_row = tk.Frame(root, bg="#f7f7f7")
    top_row.pack(fill="x", padx=12)

    frame = tk.LabelFrame(top_row, text="Tuş Ayarları", font=("Segoe UI", 12, "bold"), bg="#f7f7f7", fg="#333", padx=8, pady=8)
    frame.pack(side="left", fill="y", padx=(0,8), pady=4)

    tk.Label(frame, text="Tuş Dizisi (1,2,3 veya 123)", bg="#f7f7f7").grid(row=0, column=0, sticky="w", pady=2)
    entry_keys = tk.Entry(frame, width=22, font=("Segoe UI", 11))
    entry_keys.grid(row=1, column=0, pady=2)
    entry_keys.bind("<FocusOut>", disable_entry_on_focus_out)

    tk.Label(frame, text="Hız Seçimi", bg="#f7f7f7").grid(row=2, column=0, sticky="w", pady=2)
    combo_speed = ttk.Combobox(frame, values=["Hızlı", "Orta", "Yavaş"], width=20, state="readonly", font=("Segoe UI", 11))
    combo_speed.grid(row=3, column=0)
    combo_speed.current(0)

    profile_frame = tk.LabelFrame(top_row, text="Profil Yönetimi", font=("Segoe UI", 12, "bold"), bg="#f7f7f7", fg="#333", padx=8, pady=8)
    profile_frame.pack(side="left", fill="y", padx=(0,8), pady=4)

    tk.Label(profile_frame, text="Profil Adı", bg="#f7f7f7").pack(pady=(2, 1))
    entry_profile = tk.Entry(profile_frame, width=22, font=("Segoe UI", 11))
    entry_profile.pack()
    btn_frame = tk.Frame(profile_frame, bg="#f7f7f7")
    btn_frame.pack(pady=2)
    ttk.Button(btn_frame, text="Kaydet", command=save_profile_action).pack(side="left", padx=3)
    ttk.Button(btn_frame, text="Yükle", command=load_profile_action).pack(side="left", padx=3)
    ttk.Button(btn_frame, text="Sil", command=delete_profile_action).pack(side="left", padx=3)
    combo_profiles = ttk.Combobox(profile_frame, state="readonly", width=20, font=("Segoe UI", 11))
    combo_profiles.pack(pady=2)
    refresh_profile_menu()

    # Seçenekler kısmını diğer alanlarla hizalı yap
    options_frame = tk.LabelFrame(root, text="Seçenekler", font=("Segoe UI", 12, "bold"), bg="#f7f7f7", fg="#333", padx=8, pady=8)
    options_frame.pack(fill="x", padx=12, pady=4)

    theme_var = tk.StringVar(value="light")
    tk.Label(options_frame, text="Tema Seçimi:", bg="#f7f7f7", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8,0))
    tk.Radiobutton(options_frame, text="☀ Açık Tema", variable=theme_var, value="light", command=set_light_mode, bg="#f7f7f7", font=("Segoe UI", 11)).pack(anchor="w")
    tk.Radiobutton(options_frame, text="🌙 Koyu Tema", variable=theme_var, value="dark", command=toggle_dark_mode, bg="#f7f7f7", font=("Segoe UI", 11)).pack(anchor="w")

    # ALT KISIM: LOG VE BAŞLAT/DURDUR YAN YANA
    bottom_row = tk.Frame(root, bg="#f7f7f7")
    bottom_row.pack(pady=8, fill="x", padx=12)

    # LOG ALANI SOLDA (daha büyük)
    log_frame = tk.LabelFrame(bottom_row, text="Bot Logları", font=("Segoe UI", 11, "bold"), bg="#f7f7f7", fg="#333", padx=6, pady=6)
    log_frame.pack(side="left", fill="y", padx=(0,10))
    log_text = tk.Text(log_frame, height=14, width=40, font=("Consolas", 9), bg="#f7f7f7", state="disabled")
    log_text.pack(fill="both", expand=True)
    ttk.Button(log_frame, text="Logu Kaydet", command=export_log).pack(pady=(4,0))

    # SAĞDA BAŞLAT/DURDUR, DURUM, KRONOMETRE
    right_frame = tk.Frame(bottom_row, bg="#f7f7f7")
    right_frame.pack(side="left", fill="both", expand=True)

    ttk.Button(right_frame, text="▶ Başlat / Durdur (F1)", command=toggle_bot).pack(pady=5, anchor="e")
    status_label = tk.Label(right_frame, text="Durum: DURDU", fg="red", bg="#f7f7f7", font=("Segoe UI", 12, "bold"))
    status_label.pack(pady=3, anchor="e")
    timer_label = tk.Label(right_frame, text="Sayaç: 00:00", font=("Segoe UI", 11), bg="#f7f7f7")
    timer_label.pack(pady=(0, 6), anchor="e")

    settings = load_settings()
    if "keys" in settings:
        entry_keys.insert(0, settings["keys"])
    if "speed" in settings and settings["speed"] in combo_speed["values"]:
        combo_speed.set(settings["speed"])

    try:
        threading.Thread(target=run_bot, daemon=True).start()
        threading.Thread(target=hotkey_listener, daemon=True).start()
    except Exception as e:
        print(f"Thread başlatma hatası: {e}")

    root.mainloop()

# LOG YAZMA FONKSİYONU
def write_log(msg):
    log_text.config(state="normal")
    log_text.insert("end", msg + "\n")
    log_text.see("end")
    log_text.config(state="disabled")

def save_profile_action():
    name = entry_profile.get().strip()
    if not name:
        messagebox.showwarning("Uyarı", "Profil adı giriniz.")
        return
    keys = entry_keys.get().strip()
    speed = combo_speed.get()
    save_profile(name, keys, speed)
    messagebox.showinfo("Başarılı", f"'{name}' profili kaydedildi.")

def load_profile_action():
    name = combo_profiles.get()
    if not name:
        messagebox.showwarning("Uyarı", "Yüklenecek bir profil seçmelisiniz.")
        return
    apply_profile(name)
    messagebox.showinfo("Başarılı", f"'{name}' profili yüklendi.")

if __name__ == "__main__":
    start_gui()
    show_loading_screen()  # Yükleme ekranı varsa bunu çağır
    # Eğer yükleme ekranı istemiyorsanız, doğrudan ana arayüzü başlatabilirsiniz:
    # start_gui()
    
