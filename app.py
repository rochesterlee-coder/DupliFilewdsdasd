import os, json, shutil, threading, sys
# Ask Windows for per-monitor DPI awareness before creating any Tk windows.
# This helps keep text and controls crisp on high-DPI displays.
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from datetime import datetime

def resource_path(filename):
    # PyInstaller extracts bundled files into _MEIPASS in one-file mode.
    root_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root_dir, filename)

APP_NAME = "DupliFile"
APP_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "DupliFile"
DATA_FILE = APP_DIR / "data.json"
LANGS = ["English", "简体中文", "Bahasa Melayu", "日本語", "Español", "Français"]
TEXT = {
"English":{"tag":"Duplicate your files quickly and easily.","files":"1. Select file(s)","choose_files":"Choose File(s)","destination":"2. Choose destination folder","choose_folder":"Browse","copies":"3. Number of copies (1–30)","start":"Start Duplicating","selected":"Selected files","none":"No files selected yet.","dest_none":"Choose a destination folder","language":"Language","history":"Recent activity","clear":"Clear history","ready":"Ready","working":"Duplicating…","done":"Duplication complete!","error":"Error","select_files":"Please choose at least one file.","select_dest":"Please choose a valid destination folder.","finished":"Finished! Created {count} copies from {files} source file(s).","history_empty":"No duplication history yet.","about":"About","about_text":"DupliFile is an offline file duplicator. Files are copied locally; settings and history stay on this computer.","copy_label":"copies","theme":"Theme","light":"Light","dark":"Dark","colourful":"Colourful"},
"简体中文":{"tag":"快速轻松地复制文件。","files":"1. 选择文件","choose_files":"选择文件","destination":"2. 选择目标文件夹","choose_folder":"浏览","copies":"3. 复制份数（1–30）","start":"开始复制","selected":"已选择的文件","none":"尚未选择文件。","dest_none":"请选择目标文件夹","language":"语言","history":"最近记录","clear":"清除记录","ready":"准备就绪","working":"正在复制…","done":"复制完成！","error":"错误","select_files":"请至少选择一个文件。","select_dest":"请选择有效的目标文件夹。","finished":"完成！已为 {files} 个源文件创建 {count} 份副本。","history_empty":"暂无复制记录。","about":"关于","about_text":"DupliFile 是离线文件复制工具。文件在本地复制；设置和记录保存在此电脑上。","copy_label":"份","theme":"主题","light":"浅色","dark":"深色","colourful":"彩虹"},
"Bahasa Melayu":{"tag":"Gandakan fail dengan cepat dan mudah.","files":"1. Pilih fail","choose_files":"Pilih Fail","destination":"2. Pilih folder destinasi","choose_folder":"Semak imbas","copies":"3. Bilangan salinan (1–30)","start":"Mula Menggandakan","selected":"Fail dipilih","none":"Belum ada fail dipilih.","dest_none":"Pilih folder destinasi","language":"Bahasa","history":"Aktiviti terkini","clear":"Padam sejarah","ready":"Sedia","working":"Sedang menggandakan…","done":"Salinan selesai!","error":"Ralat","select_files":"Sila pilih sekurang-kurangnya satu fail.","select_dest":"Sila pilih folder destinasi yang sah.","finished":"Selesai! {count} salinan dibuat daripada {files} fail.","history_empty":"Belum ada sejarah.","about":"Tentang","about_text":"DupliFile ialah pengganda fail luar talian. Fail disalin secara setempat; tetapan dan sejarah kekal pada komputer ini.","copy_label":"salinan","theme":"Tema","light":"Cerah","dark":"Gelap","colourful":"Warna-warni"},
"日本語":{"tag":"ファイルをすばやく簡単に複製。","files":"1. ファイルを選択","choose_files":"ファイルを選択","destination":"2. 保存先フォルダー","choose_folder":"参照","copies":"3. 複製数（1～30）","start":"複製を開始","selected":"選択したファイル","none":"ファイルが選択されていません。","dest_none":"保存先を選択","language":"言語","history":"最近の履歴","clear":"履歴を消去","ready":"準備完了","working":"複製中…","done":"複製完了！","error":"エラー","select_files":"ファイルを1つ以上選択してください。","select_dest":"有効な保存先を選択してください。","finished":"完了！{files} 個のファイルから {count} 個のコピーを作成しました。","history_empty":"履歴はありません。","about":"情報","about_text":"DupliFile はオフラインのファイル複製ツールです。ファイル、設定、履歴はこのPCに保存されます。","copy_label":"個","theme":"テーマ","light":"ライト","dark":"ダーク","colourful":"カラフル"},
"Español":{"tag":"Duplica tus archivos de forma rápida y sencilla.","files":"1. Seleccionar archivos","choose_files":"Elegir archivos","destination":"2. Elegir carpeta de destino","choose_folder":"Examinar","copies":"3. Número de copias (1–30)","start":"Empezar a duplicar","selected":"Archivos seleccionados","none":"No hay archivos seleccionados.","dest_none":"Elige una carpeta de destino","language":"Idioma","history":"Actividad reciente","clear":"Borrar historial","ready":"Listo","working":"Duplicando…","done":"¡Duplicación completa!","error":"Error","select_files":"Elige al menos un archivo.","select_dest":"Elige una carpeta de destino válida.","finished":"¡Listo! Se crearon {count} copias de {files} archivo(s).","history_empty":"Todavía no hay historial.","about":"Acerca de","about_text":"DupliFile funciona sin conexión. Los archivos, ajustes e historial permanecen en este ordenador.","copy_label":"copias","theme":"Tema","light":"Claro","dark":"Oscuro","colourful":"Colorido"},
"Français":{"tag":"Dupliquez vos fichiers rapidement et facilement.","files":"1. Choisir les fichiers","choose_files":"Choisir les fichiers","destination":"2. Choisir le dossier de destination","choose_folder":"Parcourir","copies":"3. Nombre de copies (1–30)","start":"Lancer la duplication","selected":"Fichiers sélectionnés","none":"Aucun fichier sélectionné.","dest_none":"Choisissez un dossier de destination","language":"Langue","history":"Activité récente","clear":"Effacer l’historique","ready":"Prêt","working":"Duplication…","done":"Duplication terminée !","error":"Erreur","select_files":"Veuillez choisir au moins un fichier.","select_dest":"Choisissez un dossier de destination valide.","finished":"Terminé ! {count} copie(s) créée(s) depuis {files} fichier(s).","history_empty":"Aucun historique.","about":"À propos","about_text":"DupliFile est un outil hors ligne. Les fichiers, paramètres et l’historique restent sur cet ordinateur.","copy_label":"copies","theme":"Thème","light":"Clair","dark":"Sombre","colourful":"Coloré"}
}
APP_DIR.mkdir(parents=True, exist_ok=True)
try: data=json.loads(DATA_FILE.read_text(encoding="utf-8"))
except Exception: data={}
chosen_files=[]; history=data.get("history",[])
root=tk.Tk(); root.title(APP_NAME); root.geometry("900x760"); root.minsize(760,650)
try: root.iconbitmap(resource_path("duplifile.ico"))
except Exception: pass
lang=tk.StringVar(value=data.get("language","English"))
dest=tk.StringVar(value=data.get("destination",""))
num=tk.IntVar(value=max(1,min(30,int(data.get("copies",5) or 5))))
theme=tk.StringVar(value=data.get("theme","Light"))
status=tk.StringVar(value="")
def t(k): return TEXT.get(lang.get(),TEXT["English"]).get(k,TEXT["English"].get(k,k))
def save():
    APP_DIR.mkdir(parents=True,exist_ok=True)
    try: n=max(1,min(30,int(num.get())))
    except: n=1
    DATA_FILE.write_text(json.dumps({"language":lang.get(),"destination":dest.get(),"copies":n,"theme":theme.get(),"history":history[:50]},ensure_ascii=False,indent=2),encoding="utf-8")
def palette():
    if theme.get()=="Dark": return {"bg":"#0b1020","panel":"#131b2d","fg":"#edf3ff","muted":"#aab8d2","border":"#293a59","field":"#0e1728","soft":"#1b2942","accent":"#1677ff","green":"#19a878"}
    if theme.get()=="Colourful": return {"bg":"#21114d","panel":"#211b55","fg":"#ffffff","muted":"#e1d8ff","border":"#7c5bff","field":"#17113c","soft":"#39216c","accent":"#a13dff","green":"#00c99a"}
    return {"bg":"#f2f6ff","panel":"#ffffff","fg":"#14213d","muted":"#586780","border":"#d7e1f2","field":"#ffffff","soft":"#e9effb","accent":"#1677ff","green":"#1b9b69"}
def set_theme():
    p=palette(); root.configure(bg=p["bg"])
    for w in [header,body,topbar,subtitle_row,copyrow,destrow]:
        try: w.configure(bg=p["panel"] if w==header else p["bg"] if w in [body,topbar,subtitle_row] else p["panel"])
        except: pass
    for w in [title,subtitle,files_lbl,selected_title,dest_lbl,copies_lbl,history_title,lang_lbl,status_lbl]:
        try: w.configure(bg=p["panel"] if w not in [lang_lbl,status_lbl] else p["bg"],fg=p["fg"] if w not in [lang_lbl,status_lbl] else p["muted"])
        except: pass
    for w in [filecard,destcard,copycard,histcard]:
        w.configure(bg=p["panel"],highlightbackground=p["border"])
    # Listbox and Text support different Tk options; insertbackground belongs to Text only.
    selected_list.configure(bg=p["field"], fg=p["fg"], selectbackground=p["accent"])
    history_box.configure(bg=p["field"], fg=p["fg"], insertbackground=p["fg"])
    dest_display.configure(bg=p["field"],fg=p["fg"])
    for w in [files_btn,folder_btn,start_btn]:
        w.configure(bg=p["accent"],fg="white",activebackground=p["accent"])
    for w in [about_btn,clear_btn]:
        w.configure(bg=p["soft"],fg=p["fg"],activebackground=p["border"])
    theme_menu.configure(values=[t("light"),t("dark"),t("colourful")])
    theme_menu.set({"Light":t("light"),"Dark":t("dark"),"Colourful":t("colourful")}[theme.get()])
    save()
def refresh_files():
    selected_list.delete(0,tk.END)
    for f in chosen_files: selected_list.insert(tk.END,"▤   "+os.path.basename(f))
    selected_title.config(text=f"{t('selected')} ({len(chosen_files)})")
    if not chosen_files: selected_list.insert(tk.END,t("none"))
def update_texts():
    subtitle.config(text=t("tag")); files_lbl.config(text=t("files")); files_btn.config(text=t("choose_files"))
    dest_lbl.config(text=t("destination")); folder_btn.config(text=t("choose_folder")); copies_lbl.config(text=t("copies"))
    start_btn.config(text="▣   "+t("start")); history_title.config(text=t("history")); clear_btn.config(text=t("clear"))
    lang_lbl.config(text=t("language")); about_btn.config(text=t("about")); dest_display.config(text=dest.get() or t("dest_none"))
    refresh_files()
    if not history:
        history_box.config(state="normal"); history_box.delete("1.0",tk.END); history_box.insert(tk.END,t("history_empty")); history_box.config(state="disabled")
    set_theme()
def pick_files():
    result=filedialog.askopenfilenames(title=t("choose_files"))
    if result: chosen_files[:]=list(result); refresh_files(); save()
def pick_dest():
    result=filedialog.askdirectory(title=t("choose_folder"))
    if result: dest.set(result); dest_display.config(text=result); save()
def add_history(msg):
    history.insert(0,datetime.now().strftime("%Y-%m-%d %H:%M")+" — "+msg); del history[50:]
    history_box.config(state="normal"); history_box.delete("1.0",tk.END); history_box.insert(tk.END,"\n".join(history) if history else t("history_empty")); history_box.config(state="disabled"); save()
def duplicate():
    if not chosen_files: messagebox.showwarning(t("error"),t("select_files")); return
    target_dir=dest.get().strip()
    if not target_dir or not os.path.isdir(target_dir): messagebox.showwarning(t("error"),t("select_dest")); return
    try: copies=max(1,min(30,int(num.get())))
    except: copies=1
    start_btn.config(state="disabled"); status.set(t("working"))
    def worker():
        made=0; errors=[]
        for source in chosen_files:
            src=Path(source)
            for i in range(1,copies+1):
                try:
                    target=Path(target_dir)/f"{src.stem} - Copy {i}{src.suffix}"; j=2
                    while target.exists():
                        target=Path(target_dir)/f"{src.stem} - Copy {i} ({j}){src.suffix}"; j+=1
                    shutil.copy2(src,target); made+=1
                    root.after(0,lambda c=made: status.set(f"{t('working')}  {c}"))
                except Exception as e: errors.append(f"{src.name}: {e}")
        root.after(0,lambda: finish(made,len(chosen_files),target_dir,errors))
    threading.Thread(target=worker,daemon=True).start()
def finish(count,file_count,target_dir,errors):
    msg=t("finished").format(count=count,files=file_count); add_history(msg+" → "+target_dir)
    status.set(t("done") if not errors else t("error")); start_btn.config(state="normal")
    if errors: messagebox.showwarning(t("done"),msg+"\n\n"+"\n".join(errors[:6]))
    else: messagebox.showinfo(t("done"),msg)
def clear_history():
    if messagebox.askyesno(t("clear"),t("clear")+"?"):
        history.clear(); history_box.config(state="normal"); history_box.delete("1.0",tk.END); history_box.insert(tk.END,t("history_empty")); history_box.config(state="disabled"); save()
def about(): messagebox.showinfo(t("about"),t("about_text"))
def on_lang(_=None): update_texts(); save()
def on_theme(_=None):
    selected=theme_menu.get()
    mapping={t("light"):"Light",t("dark"):"Dark",t("colourful"):"Colourful"}
    theme.set(mapping.get(selected,"Light")); set_theme()

header=tk.Frame(root,padx=20,pady=15); header.pack(fill="x")
logo=tk.Label(header,text="▤",font=("Segoe UI",27,"bold"),fg="#35a8ff"); logo.pack(side="left",padx=(0,10))
title=tk.Label(header,text="DupliFile",font=("Segoe UI",22,"bold")); title.pack(side="left")
topbar=tk.Frame(header); topbar.pack(side="right")
lang_lbl=tk.Label(topbar,text=t("language"),font=("Segoe UI",9)); lang_lbl.pack(side="left",padx=5)
lang_menu=ttk.Combobox(topbar,textvariable=lang,values=LANGS,state="readonly",width=16); lang_menu.pack(side="left",padx=4); lang_menu.bind("<<ComboboxSelected>>",on_lang)
theme_menu=ttk.Combobox(topbar,values=["Light","Dark","Colourful"],state="readonly",width=12); theme_menu.pack(side="left",padx=4); theme_menu.bind("<<ComboboxSelected>>",on_theme)
about_btn=tk.Button(topbar,text=t("about"),command=about,relief="flat",padx=9,pady=6); about_btn.pack(side="left",padx=4)
body=tk.Frame(root,padx=22,pady=16); body.pack(fill="both",expand=True)
subtitle_row=tk.Frame(body); subtitle_row.pack(fill="x",pady=(0,12))
subtitle=tk.Label(subtitle_row,text=t("tag"),font=("Segoe UI",11)); subtitle.pack(anchor="w")
filecard=tk.Frame(body,highlightthickness=1,padx=15,pady=12); filecard.pack(fill="both",expand=True,pady=(0,10))
files_lbl=tk.Label(filecard,text=t("files"),font=("Segoe UI",12,"bold")); files_lbl.pack(anchor="w")
files_btn=tk.Button(filecard,text=t("choose_files"),command=pick_files,fg="white",relief="flat",font=("Segoe UI",10,"bold"),padx=14,pady=8); files_btn.pack(anchor="w",pady=8)
selected_title=tk.Label(filecard,text=t("selected"),font=("Segoe UI",9,"bold")); selected_title.pack(anchor="w")
selected_list=tk.Listbox(filecard,height=4,relief="flat",borderwidth=0,font=("Segoe UI",10),activestyle="none"); selected_list.pack(fill="both",expand=True,pady=(4,0))
destcard=tk.Frame(body,highlightthickness=1,padx=15,pady=11); destcard.pack(fill="x",pady=(0,10))
dest_lbl=tk.Label(destcard,text=t("destination"),font=("Segoe UI",12,"bold")); dest_lbl.pack(anchor="w")
destrow=tk.Frame(destcard); destrow.pack(fill="x",pady=7)
dest_display=tk.Label(destrow,text=dest.get() or t("dest_none"),anchor="w",padx=8,pady=7,wraplength=620); dest_display.pack(side="left",fill="x",expand=True)
folder_btn=tk.Button(destrow,text=t("choose_folder"),command=pick_dest,fg="white",relief="flat",padx=14,pady=7); folder_btn.pack(side="right",padx=(8,0))
copycard=tk.Frame(body,highlightthickness=1,padx=15,pady=11); copycard.pack(fill="x",pady=(0,10))
copies_lbl=tk.Label(copycard,text=t("copies"),font=("Segoe UI",12,"bold")); copies_lbl.pack(anchor="w")
copyrow=tk.Frame(copycard); copyrow.pack(anchor="w",pady=(7,0))
spin=ttk.Spinbox(copyrow,from_=1,to=30,textvariable=num,width=7,font=("Segoe UI",12),command=save); spin.pack(side="left")
copy_label=tk.Label(copyrow,text="  "+t("copy_label")+"   (Max: 30)"); copy_label.pack(side="left")
start_btn=tk.Button(body,text="▣   "+t("start"),command=duplicate,fg="white",relief="flat",font=("Segoe UI",12,"bold"),pady=12); start_btn.pack(fill="x",pady=(0,7))
status_lbl=tk.Label(body,textvariable=status,font=("Segoe UI",10,"bold")); status_lbl.pack(anchor="w")
histcard=tk.Frame(body,highlightthickness=1,padx=12,pady=8); histcard.pack(fill="x",pady=(8,0))
history_title=tk.Label(histcard,text=t("history"),font=("Segoe UI",10,"bold")); history_title.pack(anchor="w")
history_box=tk.Text(histcard,height=3,wrap="word",relief="flat",font=("Segoe UI",9)); history_box.pack(fill="x",pady=4); history_box.insert(tk.END,"\n".join(history) if history else t("history_empty")); history_box.config(state="disabled")
clear_btn=tk.Button(histcard,text=t("clear"),command=clear_history,relief="flat",padx=9,pady=4); clear_btn.pack(anchor="e")
status.set(t("ready")); update_texts()
def close():
    try: save()
    except: pass
    root.destroy()
root.protocol("WM_DELETE_WINDOW",close)
root.mainloop()
