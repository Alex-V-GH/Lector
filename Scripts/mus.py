import os
import random
import tkinter as tk
from tkinter import ttk
from pydub import AudioSegment

AUDIO_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac")


class MusicMixerApp:
    def __init__(self, root, music_folder):
        self.root = root
        self.root.title("Mezclador de música de fondo")
        self.root.geometry("950x700")
        self.music_folder = music_folder
        self.volume = tk.DoubleVar(value=-18)
        self.min_silence = tk.DoubleVar(value=15)
        self.max_silence = tk.DoubleVar(value=120)
        self.min_tracks = tk.IntVar(value=3)
        self.max_tracks = tk.IntVar(value=10)
        self.order = tk.StringVar(value="Aleatorio")
        self.config_done = tk.BooleanVar(value=False)



        self.music_files = []
        self.music_vars = {}

        #build_interface============================================================================================

        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        music_frame = ttk.LabelFrame(main, text="Música", padding=10)
        music_frame.pack(fill="both", expand=True, pady=10)

        list_container = ttk.Frame(music_frame)
        list_container.pack(fill="both", expand=True)

        self.music_canvas = tk.Canvas(list_container)
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.music_canvas.yview)
        self.music_inner = ttk.Frame(self.music_canvas)

        self.music_inner.bind("<Configure>", lambda e: self.music_canvas.configure(scrollregion=self.music_canvas.bbox("all")))
        self.music_canvas.create_window((0, 0), window=self.music_inner, anchor="nw")
        self.music_canvas.configure(yscrollcommand=scrollbar.set)

        self.music_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        config = ttk.LabelFrame(main, text="Configuración", padding=10)
        config.pack(fill="x")

        ttk.Label(config, text="Volumen:").grid(row=0, column=0, sticky="w")
        self.volume_label = ttk.Label(config, width=8)
        self.volume_label.grid(row=0, column=2)

        volume_slider = ttk.Scale(config, from_=-40, to=0, variable=self.volume, orient="horizontal", command=self.update_volume_label)
        volume_slider.grid(row=0, column=1, sticky="ew", padx=10)

        ttk.Label(config, text="Silencio mínimo (seg):").grid(row=1, column=0, sticky="w")
        tk.Spinbox(config, from_=0, to=3600, increment=0.5, textvariable=self.min_silence, width=10).grid(row=1, column=1, sticky="w")

        ttk.Label(config, text="Silencio máximo (seg):").grid(row=1, column=2, sticky="w")
        tk.Spinbox(config, from_=0, to=3600, increment=0.5, textvariable=self.max_silence, width=10).grid(row=1, column=3, sticky="w")

        ttk.Label(config, text="Músicas mínimas:").grid(row=2, column=0, sticky="w")
        tk.Spinbox(config, from_=1, to=100, textvariable=self.min_tracks, width=10).grid(row=2, column=1, sticky="w")

        ttk.Label(config, text="Músicas máximas:").grid(row=2, column=2, sticky="w")
        tk.Spinbox(config, from_=1, to=100, textvariable=self.max_tracks, width=10).grid(row=2, column=3, sticky="w")

        ttk.Label(config, text="Orden de selección:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(config, textvariable=self.order, values=["Aleatorio", "Orden de lista"], state="readonly", width=18).grid(row=3, column=1, sticky="w")

        config.columnconfigure(1, weight=1)

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=10)

        ttk.Button(buttons, text="OK! (HIDE FOREVER)", command=self.submit_not_again).pack(side="left", padx=5)
        ttk.Button(buttons, text="OK!", command=self.submit_config).pack(side="right", padx=5)

        self.update_volume_label()


        #load_music=======================================================================================================
        folder = self.music_folder

        for widget in self.music_inner.winfo_children():
            widget.destroy()

        self.music_files.clear()
        self.music_vars.clear()

        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(AUDIO_EXTENSIONS)]
        files.sort()
        self.music_files = files

        for path in files:
            filename = os.path.basename(path)
            selected = tk.BooleanVar(value=True)
            fade_in = tk.BooleanVar(value=True)
            fade_out = tk.BooleanVar(value=True)

            self.music_vars[path] = {"selected": selected, "fade_in": fade_in, "fade_out": fade_out}

            row = ttk.Frame(self.music_inner)
            row.pack(fill="x", pady=3)

            ttk.Checkbutton(row, text=filename, variable=selected).pack(side="left", fill="x", expand=True)
            ttk.Checkbutton(row, text="Fade in", variable=fade_in).pack(side="left", padx=5)
            ttk.Checkbutton(row, text="Fade out", variable=fade_out).pack(side="left", padx=5)

    def update_volume_label(self, *_):
        self.volume_label.config(text=f"{self.volume.get():.1f} dB")

    def submit_config(self):
        self.config_done.set(True)
        self.root.withdraw()
        self.root.quit()

    def submit_not_again(self):
        self.check_available = False
        self.config_done.set(True)
        self.root.withdraw()
        self.root.quit()

    def check_config(self):
        if self.check_available:
            self.config_done.set(False)
            self.root.deiconify()

    def process_audio(self, audio_path, temp_dir):
        original = AudioSegment.from_file(audio_path)
        total_duration = len(original)

        selected_music = [path for path, data in self.music_vars.items() if data["selected"].get()]

        if self.order.get() == "Aleatorio":
            random.shuffle(selected_music)

        desired_count = min(random.randint(self.min_tracks.get(), self.max_tracks.get()), len(selected_music))

        music_data = []

        for path in selected_music:
            try:
                music =  AudioSegment.from_file(path)
                music_data.append({"path": path, "audio": music, "duration": len(music), "fade_in": self.music_vars[path]["fade_in"].get(), "fade_out": self.music_vars[path]["fade_out"].get()})
            except Exception:
                continue

        music_layer = AudioSegment.silent(duration=total_duration)
        current_position = 0
        used_tracks = 0
        remaining = music_data.copy()

        while remaining and used_tracks < desired_count:
            possible = [item for item in remaining if item["duration"] <= total_duration]

            if not possible:
                break

            item = random.choice(possible) if self.order.get() == "Aleatorio" else possible[0]
            music = item["audio"]
            music_duration = item["duration"]
            remaining_time = total_duration - current_position

            if music_duration > remaining_time:
                remaining.remove(item)
                continue

            min_silence_ms = int(self.min_silence.get() * 1000)
            max_silence_ms = int(self.max_silence.get() * 1000)
            max_silence_ms = max(max_silence_ms, min_silence_ms)

            silence = random.randint(min_silence_ms, max_silence_ms)
            position = current_position + silence

            if position + music_duration > total_duration:
                max_position = total_duration - music_duration

                if max_position < current_position:
                    remaining.remove(item)
                    continue

                position = random.randint(current_position, max_position)

            processed_music = music
            fade_length = min(3000, 20000)

            if item["fade_in"] and fade_length > 0:
                processed_music = processed_music.fade_in(fade_length)

            if item["fade_out"] and fade_length > 0:
                processed_music = processed_music.fade_out(fade_length)

            processed_music = processed_music + self.volume.get()
            music_layer = music_layer.overlay(processed_music, position=position)

            current_position = position + music_duration
            used_tracks += 1
            remaining.remove(item)

            if current_position >= total_duration:
                break

        result = original.overlay(music_layer)
        output_path = f"{audio_path.split('.')[0]}_M.wav"

        result.export(output_path, format="wav")
        return output_path


if __name__ == "__main__":
    print("NO ES ASÍ COMO SE USA ESTE SCRIPT!")