import subprocess
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pydub import AudioSegment
from pyannote.audio import Pipeline


class SimpleVoiceSplitterApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Easy Voice Splitter")
        self.root.geometry("620x360")
        self.root.resizable(False, False)

        self.input_file = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status_text = tk.StringVar(value="Choose a file and click Start.")

        self._build_ui()

    def _build_ui(self) -> None:
        card = ttk.Frame(self.root, padding=20)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text="Easy Voice Splitter", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(
            card,
            text="Separates vocals from instrumental and creates speaker clips.",
            foreground="#555",
        ).pack(anchor="w", pady=(0, 14))

        ttk.Button(card, text="1) Choose Audio File", command=self.pick_file).pack(fill="x", pady=4)
        ttk.Label(card, textvariable=self.input_file, foreground="#333").pack(anchor="w", pady=(0, 10))

        ttk.Button(card, text="2) Choose Output Folder", command=self.pick_output).pack(fill="x", pady=4)
        ttk.Label(card, textvariable=self.output_folder, foreground="#333").pack(anchor="w", pady=(0, 14))

        self.start_button = ttk.Button(card, text="3) Start", command=self.start)
        self.start_button.pack(fill="x", pady=(0, 10))

        self.progress = ttk.Progressbar(card, mode="indeterminate")
        self.progress.pack(fill="x")

        ttk.Label(card, textvariable=self.status_text, foreground="#1f4e79").pack(anchor="w", pady=(12, 0))

    def pick_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Choose an audio file",
            filetypes=[("Audio", "*.wav *.mp3 *.m4a *.flac *.ogg"), ("All files", "*.*")],
        )
        if file_path:
            self.input_file.set(file_path)

    def pick_output(self) -> None:
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_folder.set(folder)

    def start(self) -> None:
        if not self.input_file.get():
            messagebox.showerror("Missing audio", "Please choose an audio file.")
            return
        if not self.output_folder.get():
            messagebox.showerror("Missing output", "Please choose an output folder.")
            return

        self.start_button.configure(state="disabled")
        self.progress.start(10)
        self.status_text.set("Processing... this may take a few minutes.")

        threading.Thread(target=self.process, daemon=True).start()

    def process(self) -> None:
        try:
            src = Path(self.input_file.get())
            out = Path(self.output_folder.get())
            out.mkdir(parents=True, exist_ok=True)

            stems_dir = out / "stems"
            subprocess.run(
                [
                    "python",
                    "-m",
                    "demucs.separate",
                    "--two-stems",
                    "vocals",
                    "-o",
                    str(stems_dir),
                    str(src),
                ],
                check=True,
            )

            vocals = stems_dir / "htdemucs" / src.stem / "vocals.wav"
            instrumental = stems_dir / "htdemucs" / src.stem / "no_vocals.wav"

            token = subprocess.check_output([
                "python",
                "-c",
                "from huggingface_hub import HfFolder; print(HfFolder.get_token() or '')",
            ], text=True).strip()
            if not token:
                raise RuntimeError(
                    "No Hugging Face login detected. Run: huggingface-cli login"
                )

            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
            diarization = pipeline(str(vocals))
            audio = AudioSegment.from_file(vocals)
            segments_dir = out / "speaker_segments"
            segments_dir.mkdir(exist_ok=True)

            counts: dict[str, int] = {}
            for segment, _, speaker in diarization.itertracks(yield_label=True):
                counts[speaker] = counts.get(speaker, 0) + 1
                clip = audio[int(segment.start * 1000):int(segment.end * 1000)]
                clip.export(segments_dir / f"{src.stem}_{speaker}_{counts[speaker]:03d}.wav", format="wav")

            self.root.after(0, lambda: self.status_text.set(f"Done! Saved files to: {out}"))
            self.root.after(0, lambda: messagebox.showinfo("Finished", f"All done.\n\nVocals: {vocals}\nInstrumental: {instrumental}"))
        except Exception as exc:
            self.root.after(0, lambda: self.status_text.set("Something went wrong."))
            self.root.after(0, lambda: messagebox.showerror("Error", str(exc)))
        finally:
            self.root.after(0, self.finish)

    def finish(self) -> None:
        self.progress.stop()
        self.start_button.configure(state="normal")


if __name__ == "__main__":
    app_root = tk.Tk()
    SimpleVoiceSplitterApp(app_root)
    app_root.mainloop()
