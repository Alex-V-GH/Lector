import win32com.client
import sys

def leer(texto, temp_wav):
    modo_archivo_exitoso = False
    loq = win32com.client.Dispatch("LTTS7.LoqTTSCtrl.1")
    loq.Voice = "Jorge"
        #---------------------------------------------------------
    for prop in ["AudioDestination", "OutputFileName", "AudioFileName"]:
        try:
            setattr(loq, prop, temp_wav)
            modo_archivo_exitoso = True
            break
        except: continue
    if modo_archivo_exitoso: loq.Read(texto)
    else:
        try: loq.Record(texto, temp_wav)
        except: loq.ReadFile(texto, temp_wav)

        
if __name__=="__main__":
    if len(sys.argv) > 2:
        txt_file_path = sys.argv[1] 
        temp_wav_path = sys.argv[2] 
        with open(txt_file_path, "r", encoding="utf-8") as f: contenido = f.read()
        leer (contenido, temp_wav_path)