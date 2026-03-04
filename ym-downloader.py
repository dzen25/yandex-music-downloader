#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import re
import subprocess
import argparse
import venv
import shutil
from pathlib import Path

SCRIPT_NAME = "ym-downloader"
VERSION = "2.0.0"

CONFIG_DIR = Path.home() / ".config" / SCRIPT_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
VENV_DIR = Path.home() / ".local" / "share" / SCRIPT_NAME / "venv"

DEFAULT_QUALITY = "2"
DEFAULT_DIR = str(Path.home() / "yandex-music-download")


class YandexMusicWrapper:
    def __init__(self):
        self.config = self.load_config()
        self.venv_python = VENV_DIR / "bin" / "python"
        self.venv_pip = VENV_DIR / "bin" / "pip"
        self.cli_binary = VENV_DIR / "bin" / "yandex-music-downloader"

    # ------------------ VENV ------------------

    def setup_venv(self):
        if not VENV_DIR.exists():
            print("🔧 Создание виртуального окружения...")
            venv.create(VENV_DIR, with_pip=True)

        if not self.cli_binary.exists():
            self.install_package()

    def install_package(self):
        print("📦 Установка yandex-music-downloader...")
        subprocess.run([
            str(self.venv_pip),
            "install",
            "-U",
            "git+https://github.com/llistochek/yandex-music-downloader.git"
        ], check=True)
        print("✅ Пакет установлен")

    # ------------------ CONFIG ------------------

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "token": None,
            "quality": DEFAULT_QUALITY,
            "dir": DEFAULT_DIR
        }

    def save_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2)
        print("✅ Настройки сохранены")

    def configure(self):
        print("\n=== Настройка ===\n")

        token = input("🔑 Токен: ").strip()
        if token:
            self.config["token"] = token

        quality = input("🎵 Качество (0/1/2): ").strip()
        if quality in ["0", "1", "2"]:
            self.config["quality"] = quality

        directory = input(f"📁 Папка загрузки [{self.config['dir']}]: ").strip()
        if directory:
            self.config["dir"] = os.path.expanduser(directory)

        self.save_config()

    # ------------------ URL PARSING ------------------

    def extract_id(self, url):
        patterns = {
            "track": r"/track/(\d+)",
            "album": r"/album/(\d+)",
            "artist": r"/artist/(\d+)",
            "playlist": r"/playlists/([^/?]+)",
        }

        for t, pattern in patterns.items():
            m = re.search(pattern, url)
            if m:
                return t, m.group(1)

        return None, None

    # ------------------ RUN ------------------

    def run(self, url, auto_confirm=False):
        if not self.config.get("token"):
            print("❌ Сначала настрой токен через --config")
            return False

        content_type, content_id = self.extract_id(url)
        if not content_id:
            print("❌ Не удалось определить тип ссылки")
            return False

        cmd = [
            str(self.cli_binary),
            "--token", self.config["token"],
            "--quality", self.config["quality"],
            "--dir", self.config["dir"]
        ]

        if content_type == "track":
            cmd += ["--track-id", content_id]
        elif content_type == "album":
            cmd += ["--album-id", content_id]
        elif content_type == "artist":
            cmd += ["--artist-id", content_id]
        elif content_type == "playlist":
            cmd += ["--playlist-id", content_id]

        print("\n📋 Команда:")
        print(" ".join(cmd))
        print()

        if not auto_confirm:
            confirm = input("Запустить? (Y/n): ").lower()
            if confirm not in ["y", "yes", ""]:
                return False

        subprocess.run(cmd)
        return True


# ------------------ MAIN ------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url")
    parser.add_argument("-c", "--config", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    wrapper = YandexMusicWrapper()

    if args.reset:
        if VENV_DIR.exists():
            shutil.rmtree(VENV_DIR)
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        print("✅ Всё удалено")
        return

    if args.config:
        wrapper.configure()
        return

    wrapper.setup_venv()

    if args.url:
        wrapper.run(args.url, auto_confirm=args.yes)
    else:
        while True:
            url = input("\n🔗 Ссылка (или exit): ").strip()
            if url == "exit":
                break
            wrapper.run(url)


if __name__ == "__main__":
    main()
