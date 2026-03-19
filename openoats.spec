# openoats.spec
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = [
    "pyaudiowpatch",
    "sounddevice",
    "keyring.backends.Windows",
    "qasync",
    "silero_vad",
]

for pkg in ["ctranslate2", "faster_whisper", "silero_vad"]:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="OpenOats",
    console=False,
    icon=None,
)
