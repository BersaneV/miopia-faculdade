"""Prepara ou repara apenas o ambiente de desenvolvimento do jogo."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

RAIZ = Path(__file__).resolve().parents[1]
VENV = RAIZ / ".venv"
BIN = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
TESTE = """
import pygame
from importlib.metadata import version
assert pygame.IS_CE and version("pygame-ce") == "2.5.8"
from pygame import display, event, font, mixer, image, draw, transform
assert all(hasattr(m, a) for m,a in ((display,'set_mode'),(event,'get'),(font,'Font'),
    (mixer,'Sound'),(image,'load'),(draw,'circle'),(transform,'smoothscale')))
"""


def executar(args, verificar=False):
    return subprocess.run(args, cwd=RAIZ, check=verificar, stdout=subprocess.DEVNULL if not verificar else None,
                          stderr=subprocess.DEVNULL if not verificar else None).returncode


def main():
    if not (3, 10) <= sys.version_info[:2] <= (3, 14):
        raise RuntimeError("Use Python 3.10 a 3.14 na pasta de desenvolvimento.")
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")
    os.environ.setdefault("PIP_NO_INPUT", "1")
    teste_python = "import sys; assert sys.prefix != sys.base_prefix and (3,10) <= sys.version_info[:2] <= (3,14)"
    try:
        valido = BIN.is_file() and executar([BIN, "-c", teste_python]) == 0
    except OSError:
        valido = False
    if not valido:
        if VENV.exists() or VENV.is_symlink():
            copia = RAIZ / f".venv-incompleta-{time.time_ns()}"
            VENV.rename(copia)
            print(f"Ambiente anterior guardado em {copia.name}.", flush=True)
        executar([sys.executable, "-m", "venv", VENV], verificar=True)
    if executar([BIN, "-c", TESTE]) != 0:
        if executar([BIN, "-m", "pip", "--version"]) != 0:
            executar([BIN, "-m", "ensurepip", "--upgrade"], verificar=True)
        print("Preparando pygame-ce para o jogo…", flush=True)
        executar([BIN, "-m", "pip", "install", "--only-binary=:all:", "--force-reinstall",
                  "-r", RAIZ / "requirements.txt"], verificar=True)
        executar([BIN, "-c", TESTE], verificar=True)
    # O PID da partida substitui o do lançador em Linux; no Windows manter
    # o processo pai permite que a janela de desenvolvimento aguarde o jogo.
    os.chdir(RAIZ)
    args = [str(BIN), "-m", "src.main", *sys.argv[1:]]
    if os.name == "nt":
        return subprocess.call(args)
    os.execv(str(BIN), args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as erro:
        msg = ("Não foi possível preparar o ambiente de desenvolvimento. Verifique a conexão e o suporte "
               "a venv/pip do seu Python. No Fedora x86_64, o pacote Miopia-Linux abre offline.\n\n" + str(erro))
        print(msg, file=sys.stderr)
        if os.name != "nt" and (os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY")) and shutil.which("zenity"):
            subprocess.run(["zenity", "--error", "--title=Miopia", "--text=" + msg])
        sys.exit(1)
