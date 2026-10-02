# LECTOR

Aplicación de escritorio desarrollada en Python para convertir libros en **PDF o EPUB** a audiolibros en español.
###⚠️ **Proyecto experimental/personal.** La aplicación depende de software externo, especialmente Loquendo TTS y FFmpeg, por lo que actualmente está orientada principalmente a Windows.

## Flujo completo:

1. Extraer el texto del libro.
2. Limpiar y reorganizar el texto.
3. Traducir el contenido al español mediante un modelo de Hugging Face. Esto se hace únicamente si se especifica que está en inglés.
4. Convertir el texto a voz utilizando **Loquendo TTS**. Más específicamente, la versión 7.
5. Opcionalmente agregar música de fondo.
6. Convertir los archivos WAV resultantes a MP3.
7. Guardar el audiolibro dividido en varias partes con una duración estableida en aproximadamente 20 minutos.

----------------------------------------------------------------------------------------------------------------------------------------------------

## Características

- Soporte para:
  - `.pdf`
  - `.epub`
- Extracción automática del texto.
- Traducción automática **inglés → español**.
- Uso de `google/translategemma-4b-it` para la traducción.
- Conversión de texto a voz mediante Loquendo.
- Voz configurada actualmente como `Jorge`.
- División automática del libro en varias partes.
- Conversión WAV → MP3 mediante FFmpeg.
- Música de fondo opcional.
- Selección de pistas musicales.
- Volumen configurable de la música.
- Fade in / fade out opcional por cada pieza musical.
- Intervalos aleatorios de silencio entre pistas, con max y min configurables.
- Cantidad mínima y máxima de canciones por parte configurable.
- Selección aleatoria o por orden de lista.

----------------------------------------------------------------------------------------------------------------------------------------------------

##  Estructura del proyecto

```text
.
├── l.py
├── tdb.py
├── mus.py
│
├── Libros/
│   ├── libro1.pdf
│   └── libro2.epub
│
├── Temp/
│   └── ...
│
├── Audio/
│   └── Libro A/
│       ├── Libro A 001.mp3
│       ├── Libro A 002.mp3
│       └── ...
│
├── Musica/
│   ├── track1.mp3
│   ├── track2.mp3
│   └── ...
│
├── Lector.bat
├── requirements.txt
└── README.md
```

Los directorios `Libros`, `Temp`, `Audio` y `Musica` deben existir antes de ejecutar el programa.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 💻 Requisitos

### Sistema operativo

Actualmente el proyecto está pensado principalmente para:

- Windows
- Python 3.11+ Y Python x86 3.11+
- Loquendo TTS (7)
- FFmpeg

La utilización de `win32com.client` y del componente COM de Loquendo hace que la parte de síntesis de voz dependa específicamente de Windows.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🔊 Loquendo TTS

La generación de voz se realiza mediante:

```python
win32com.client.Dispatch("LTTS7.LoqTTSCtrl.1")
```

Por lo tanto, es necesario tener instalado y correctamente registrado **Loquendo TTS 7**.

El programa actualmente utiliza:

```python
loq.Voice = "Jorge"
```

Si esa voz no está instalada o el nombre no coincide con la instalación local, la generación de audio no funcionará.

La lógica encargada de comunicarse con Loquendo está en:

```text
tdb.py
```

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🎬 FFmpeg

El programa utiliza FFmpeg para convertir los WAV generados por Loquendo a MP3.

Actualmente la ruta está definida directamente en `l.py`:

```python
FFMPEG_PATH = r"C:/ffmpeg/bin/ffmpeg.exe"
FFMPEG_FOLDER = r"C:/ffmpeg/bin"
```

Si FFmpeg está instalado en otra ubicación, modificar:

```python
FFMPEG_PATH
```

Por ejemplo:

```python
FFMPEG_PATH = r"C:/Program Files/ffmpeg/bin/ffmpeg.exe"
```

También es posible configurar FFmpeg en el `PATH` del sistema y adaptar el código para utilizar simplemente:

```text
ffmpeg
```

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🤖 Traducción

La traducción utiliza:

```text
google/translatgemma-4b-it
```

mediante `transformers`.

El modelo se carga con:

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    token=HF_TOKEN,
    torch_dtype="auto",
    device_map="auto"
)
```

La traducción se realiza por párrafos.

El código utiliza actualmente:

```python
source_lang_code = "en"
target_lang_code = "es"
```

por lo que el flujo está preparado para:

```text
Inglés → Español
```

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🔐 Token de Hugging Face

El modelo de traducción requiere un token de Hugging Face.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 📖 Uso
### 0. Preparación previa:

Usando python 3.11+ x64:
Navegar hasta el directorio raíz del proyecto y ejecutar:
```Python
pip install -r requirements.txt
```

Instalar python 3.11 x86

Instalar ffmpeg

Instalar Loquendo TTS 7

Obtener un token de HuggingFace

Comprobar las rutas a los programas, comprobar el token de HuggingFace

                                --------------------------------------------------------------------------
                                
### 1. Colocar los archivos necesarios:

Copiar los archivos PDF o EPUB dentro de:
```text
Libros/
```

Ejemplo:
```text
Libros/
├── Dracula.pdf
├── Frankenstein.epub
└── The Hobbit.pdf
```

Copiar los archivos de música (mp3, flac, wav, etc) dentro de:
```text
Musica/
```

                                --------------------------------------------------------------------------

### 2. Ejecutar el programa

Ejecutar Lector.bat, alojado en la carpeta raíz.

El programa buscará automáticamente archivos:
```text
.pdf
.epub
```
dentro de `Libros/`.
Además, hará lo propio con los archivos de música llegado el momento.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🌐 Traducción
Los párrafos extraídos se envían al modelo de traducción. El modelo se toma su tiempo en traducir los libros. Es por esto que agregué un checkpoint:
El resultado se guarda como
```Temp/(libro)_traducido.txt```
Si este archivo ya existe, el programa lo reutiliza y evita volver a traducir el libro.
Esto permite interrumpir el proceso y continuar posteriormente sin tener que traducir todo nuevamente.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🔊 Generación del audiolibro

Una vez traducido el libro, el texto se divide en bloques.
Actualmente, por defecto, cada bloque puede tener hasta `20.000 caracteres`, lo cual equivale a groso modo a 20 minutos de audio.
Cada bloque se guarda temporalmente y se envía a `tdb.py` en forma de argumento.

Por ejemplo:
```text
Temp/
├── Dracula.temp1.txt
├── Dracula.temp1.wav
├── Dracula.temp2.txt
├── Dracula.temp2.wav
└── ...
```
Después se convierten a MP3.
El resultado final queda en:
```text
Audio/
└── Dracula/
    ├── Dracula 001.mp3
    ├── Dracula 002.mp3
    ├── Dracula 003.mp3
    └── ...
```

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🎵 Música de fondo

Antes de comenzar a generar las partes del audiolibro, el programa pregunta:
```text
Agregamos música de fondo? Y/N
```
Si se responde `Y` se abre la interfaz gráfica de `mus.py`.
Desde ahí se pueden configurar:

- Volumen.
- Silencio mínimo.
- Silencio máximo.
- Número mínimo de pistas.
- Número máximo de pistas.
- Orden de selección.
- Pistas que pueden utilizarse.
- Fade in.
- Fade out.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🎚️ Configuración de música

Los archivos musicales deben colocarse en `Musica/`.
Se reconocen:
```
.mp3
.wav
.ogg
.flac
.m4a
.aac
```
Cada pista aparece en la interfaz y puede activarse o desactivarse.

### Volumen
El valor predeterminado es `-18 dB`, valor elegido deliberadamente para no tapar la voz.
El rango disponible actualmente es `-40 dB → 0 dB`

### Silencios
Por defecto:
```text
Mínimo: 15 segundos
Máximo: 120 segundos
```
Esto determina aproximadamente cuánto silencio puede haber antes de comenzar una nueva pista musical. Tiempos alternados de silencio y música ayudan a la concentración.

### Número de pistas
Por defecto:
```text
Mínimo: 3
Máximo: 10
```
El programa selecciona aleatoriamente una cantidad dentro de ese rango, limitada por la cantidad de pistas disponibles.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🔄 Flujo general

```text
                 ┌──────────────┐
                 │ PDF / EPUB   │
                 └──────┬───────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Extraer texto   │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Limpiar texto   │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Traducción      │
               │ EN → ES         │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Dividir bloques │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Loquendo TTS    │
               └────────┬────────┘
                        │
                        ▼
                  ┌────────────┐
                  │    WAV     │
                  └─────┬──────┘
                        │
                 ┌──────┴───────┐
                 │              │
              Sin música     Con música
                 │              │
                 │              ▼
                 │       ┌──────────────┐
                 │       │ Pydub Mixer  │
                 │       └──────┬───────┘
                 │              │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │    FFmpeg    │
                 │   WAV → MP3  │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ Audiolibro   │
                 │ dividido     │
                 └──────────────┘
```

----------------------------------------------------------------------------------------------------------------------------------------------------

## ⚙️ Configuración principal

Las rutas principales están actualmente definidas en `l.py`:

```python
FFMPEG_PATH = r"C:/ffmpeg/bin/ffmpeg.exe"
FFMPEG_FOLDER = r"C:/ffmpeg/bin"
PYTHON_X86_PATH = r"C:\Python313x86\python.exe"

BOOK_DIR = r"Libros"
TEMP_DIR = r"Temp"
AUDIO_DIR = r"Audio"
MUSIC_DIR = r"Musica"
```
Es necesario adaptar estas rutas al entorno local.

----------------------------------------------------------------------------------------------------------------------------------------------------

## ¿Por qué se utiliza otro Python?

El proyecto actualmente utiliza un segundo intérprete de Python para ejecutar `tdb.py`. Esto está definido mediante `PYTHON_X86_PATH`. La razón es que la instalación de Loquendo/COM puede requerir compatibilidad con una arquitectura específica.

Por eso el proyecto puede tener:

```text
Python principal
       │
       ├── l.py
       └── mus.py
       
Python secundario
       │
       └── tdb.py
             │
             ▼
        Loquendo TTS
```
La arquitectura exacta requerida dependerá de la instalación de Loquendo utilizada. 
Sin embargo, al instalar una versión x64 de Loquendo TTS, se puede reemplazar la ruta de `python x86` con una `x64`

----------------------------------------------------------------------------------------------------------------------------------------------------

## ⚠️ Limitaciones conocidas

### PDF escaneados
`PyPDF2` extrae texto de PDFs que contienen texto digital.
Si el PDF está compuesto únicamente por imágenes escaneadas, el texto reconocido será nulo.

### Traducción
La calidad de la traducción depende del modelo y del texto original. Gema parece funcionar correctamente, aunque es un modelo quizás demasiado pesado para algunas computadoras. Sin embargo, pruebas con modelos inferiores causaron glitches demasiado grandes e imposibles de ignorar, como la repetición indefinida de ciertas frases sin un motivo aparente.
Además, el programa actualmente asume:
```text
Inglés → Español
```
y no detecta automáticamente el idioma.

## 🧹 Archivos temporales

Durante el procesamiento se generan archivos temporales en:

```text
Temp/
```

Estos pueden incluir:

```text
*.txt
*.wav
```

Una vez comprobado que el audiolibro terminó correctamente, estos archivos pueden eliminarse manualmente. Se recomienda eliminar principalmente los audios, ya que son los archivos más pesados que se generan.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🚀 Posibles mejoras futuras:

- [ ] Detección automática del idioma.
- [ ] Soporte para más idiomas de entrada. *(improbable)*
- [ ] OCR para PDFs escaneados. (improbable)
- [ ] Selección de voz desde la interfaz. *(improbable)*
- [ ] Barra de progreso.
- [ ] Pausar/reanudar conversiones.
- [ ] Reintento automático ante errores.
- [ ] Limpieza automática de archivos temporales.
- [ ] Configuración mediante archivo `.json`.
- [ ] Eliminar rutas absolutas del código.
- [ ] Uso de variables de entorno para tokens y rutas. *(improbable)*
- [ ] Integración de FFmpeg mediante `PATH`.
- [ ] Interfaz gráfica para todo el proceso.
- [ ] Procesamiento paralelo de partes. *Opcional.*
- [ ] Detección de capítulos o secciones principales para cortes mejor hechos y músicas mejor medidas.
- [ ] Generación de metadatos del audiolibro.
- [ ] Creación automática de portada.
- [ ] Unión de las partes en un único audiolibro exportado a M4B. *Opcional.*.

----------------------------------------------------------------------------------------------------------------------------------------------------

## 🛠️ Estado del proyecto

**Experimental / En desarrollo**
El proyecto funciona como un pipeline personal para automatizar la creación de audiolibros, pero todavía contiene configuraciones específicas del entorno de desarrollo. Además, los requisitos son demasiado específicos para el nivel de detalle otorgado por ahora, por lo tanto no se lo considera estable.

Antes de utilizarlo en otra máquina hay que revisar:
- Rutas de Python.
- Instalación de Loquendo.
- Voz disponible.
- FFmpeg.
- Modelo de Hugging Face.
- GPU/RAM disponible.
- Directorios de entrada y salida.
- Versión de sistema operativo.
- 
----------------------------------------------------------------------------------------------------------------------------------------------------
