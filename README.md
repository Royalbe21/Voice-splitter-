# Easy Voice Splitter (Windows 11)

This app is intentionally simple:

1. Click **Choose Audio File**.
2. Click **Choose Output Folder**.
3. Click **Start**.

The app will:
- separate **vocals** and **instrumental**
- create speaker clips from vocals for different voices

## Download and run locally

### 1) Download this repo to your PC

**Option A: Git (recommended)**
```powershell
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

**Option B: ZIP download**
1. Open your GitHub repo in a browser.
2. Click **Code** → **Download ZIP**.
3. Extract the ZIP.
4. Open PowerShell in the extracted folder.

### 2) Install Python dependencies

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Install FFmpeg

```powershell
winget install --id Gyan.FFmpeg -e
```

### 4) Login to Hugging Face once

```powershell
huggingface-cli login
```

Also make sure your account has accepted access for:
- `pyannote/speaker-diarization-3.1`

## Run

```powershell
python app.py
```

## Output

- `stems/htdemucs/<input>/vocals.wav`
- `stems/htdemucs/<input>/no_vocals.wav`
- `speaker_segments/<input>_SPEAKER_XX_YYY.wav`
