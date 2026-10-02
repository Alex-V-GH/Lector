import os
import subprocess
import PyPDF2
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from mus import MusicMixerApp
import tkinter as tk


FFMPEG_PATH = r"C:/ffmpeg/bin/ffmpeg.exe"
FFMPEG_FOLDER = r"C:/ffmpeg/bin"
PYTHON_X86_PATH = r"C:\Python313x86\python.exe"
BOOK_DIR = r"Libros"
TEMP_DIR = r"Temp"
AUDIO_DIR = r"Audio"
MUSIC_DIR = r"Musica"

# ----------------- FUNCIONES DE EXTRACCIÓN DE TEXTO -----------------
def extraer_texto_pdf(pdf_path):
    texto_total = ""
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texto_total += page_text + "\n"
    return texto_total


def extraer_texto_epub(epub_path):
    book = epub.read_epub(epub_path)
    texto_total = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        texto_total.append(soup.get_text())
    return "\n".join(texto_total)



def unir_lineas(texto):
    lineas = texto.splitlines()
    resultado = []
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            resultado.append("")
            continue
        if resultado and resultado[-1]:
            anterior = resultado[-1]
            # Si la línea anterior no termina como una oración
            # y la actual parece continuarla, las unimos.
            if not re.search(r'[.!?:;]$', anterior) and not re.match(r'^[A-ZTÁÉÍÓÚÑ¿¡0-9]', linea): 
                resultado[-1] += " " + linea
                continue

        resultado.append(linea)
    return "\n".join(resultado)


def obtener_texto_libro(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    print (f"{file_path} -> {(file_path)[1]} -> {(file_path)[1].lower()};\n{ext} -> {os.path.splitext(file_path)[1]} -> {os.path.splitext(file_path)}")
    if ext == ".pdf":
        texto = extraer_texto_pdf(file_path)
    elif ext == ".epub":
        texto = extraer_texto_epub(file_path)
    else:
        raise ValueError(f"Formato no soportado: {ext}")
    return unir_lineas(texto)


# ----------------- Traduccion -----------------
def traducir(textos: list[str]) -> list[str]:

    HF_TOKEN = #PUT YOUR TOKEN HERE!
    model_name = "google/translategemma-4b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN,use_fast=False)
    print(f"[+] Cargando {model_name}")
    model = AutoModelForCausalLM.from_pretrained(model_name, token=HF_TOKEN, torch_dtype="auto", device_map="auto")
    print("[+] Modelo cargado.")

    resultados = []

    for i, texto in enumerate(textos, 1):
        print(f"[TRADUCIENDO] {i:04d}/{len(textos):04d}", end="\r")

        messages = [{"role": "user", "content": [{"type": "text", "source_lang_code": "en","target_lang_code": "es", "text": texto}]}]

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=4096, do_sample=False,pad_token_id=tokenizer.eos_token_id)

        generated = output[0][inputs["input_ids"].shape[1]:]
        resultados.append(tokenizer.decode(generated, skip_special_tokens=True).strip())

    print()
    return resultados


# ----------------- DIVISIÓN DE TEXTO EN BLOQUES -----------------
def dividir_texto(texto, max_caracteres=20000):
    parrafos = [p for p in texto.split("\n") if p.strip()]
    bloques = []
    actual = []
    len_actual = 0
    for p in parrafos:
        len_p = len(p)
        separador = 1 if actual else 0          # el "\n" que se agregaría al unir
        nuevo_len = len_actual + separador + len_p
        if nuevo_len > max_caracteres and actual:
            bloques.append("\n".join(actual))    # cierra el bloque sin este párrafo
            actual = [p]                          # el párrafo "sobrante" arranca el siguiente
            len_actual = len_p
        else:
            actual.append(p)
            len_actual = nuevo_len
    if actual:
        bloques.append("\n".join(actual))
    return bloques

def wav_a_mp3(archivo_wav, archivo_mp3):
    try:
        cmd = [
            FFMPEG_PATH,
            "-y",
            "-i", archivo_wav,
            "-acodec", "libmp3lame",
            "-ab", "128k",
            archivo_mp3
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

#---------------------------------------------------------
def texto_a_mp3_por_partes(texto, audio_folder, filename):
    bloques = dividir_texto(texto)
    total_bloques = len(bloques)
    folder_path = f"{audio_folder}/{filename}"
    os.makedirs(folder_path, exist_ok=True)
    os.makedirs(os.path.join(f"{folder_path}/temp"), exist_ok=True)
    musica = False
    musica_inicializado = False
    if input(f"Agregamos música de fondo? Y/N\n").lower() == "y":
        if musica_inicializado:
            agregador_de_musica.check_config()
            print("1")
            root.wait_variable(agregador_de_musica.config_done)
            print("2")
        else:
            root = tk.Tk()
            print("3")
            agregador_de_musica = MusicMixerApp(root, MUSIC_DIR)
            print("4")
            root.mainloop()
            print("6")
            musica = True
            print("7")
            musica_inicializado = True
            print("8")
    for i, bloque in enumerate(bloques, 1):
        mp3_name = f"{filename} {i:03d}.mp3"
        output_mp3 = f"{folder_path}/{mp3_name}"
        temp_wav = f"{TEMP_DIR}/{filename}.temp{i}.wav"
        temp_txt = f"{TEMP_DIR}/{filename}.temp{i}.txt"
        print(f"Generando Audio Parte {i:03d}/{total_bloques:03d}", end="\r", flush=True)
        with open(temp_txt,"w", encoding = "utf-8") as f:
            f.write(bloque)
        cmd_tdb =[PYTHON_X86_PATH, r"Scripts\tdb.py", temp_txt, temp_wav]
        subprocess.run(cmd_tdb, check = True)
        if musica:
            temp_wav = agregador_de_musica.process_audio(temp_wav,TEMP_DIR)
        wav_a_mp3(temp_wav,output_mp3)


    print(f"\n¡Éxito! Todas las {total_bloques} partes se guardaron en:\n{folder_path}")



# ----------------- EJECUCIÓN -----------------
if __name__ == "__main__":
    print("======================================")
    print("======Convertidor a Audiolibros!======")
    print("=Formatos admitidos: PDF | EPUB ======")
    print("=Idioma de entrada -> Ingles/Español==")
    print("=Idioma de salida -> Español==========\n")
    for file in os.listdir(BOOK_DIR):
        if file.endswith(".pdf") or file.endswith(".epub"):
            book_name = file.split(".")[0]
            print (book_name)
            if input(f"Procesamos {book_name}? Y/N\n").lower() == "y":
                book_path = f"{BOOK_DIR}/{file}"
                print(book_path)
                trad_path = f"{TEMP_DIR}/{book_name}_traducido.txt"
                extracted_path = f"{TEMP_DIR}/{book_name}_resultante.txt"
                result_folder = f"{AUDIO_DIR}/{book_name}"
                if not os.path.exists(result_folder):
                    if not os.path.exists(trad_path):
                        texto = obtener_texto_libro(book_path).strip()
                        if input(f"{book_name} está en inglés? (Y/N)\n").lower() == "y":
                            with open(extracted_path, "w", encoding="utf-8") as f:
                                f.write(texto)
                            parrafos = [p for p in texto.split("\n") if p.strip()]
                            texto = "\n".join(traducir(parrafos)).replace("<end_of_turn>","")
                        with open(trad_path, "w", encoding="utf-8") as f:
                            f.write(texto)
                    with open(trad_path, "r", encoding="utf-8") as trad_file:
                        texto = trad_file.read().replace("<end_of_turn>","")#redundante pero aparentemente necesario.
                    texto_a_mp3_por_partes(texto, result_folder, book_name)