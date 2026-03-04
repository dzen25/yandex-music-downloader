#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Yandex Music Downloader Wrapper
Универсальная оболочка для yandex-music-downloader с автоматическим управлением
виртуальным окружением и сохранением настроек.
"""

import os
import sys
import json
import re
import subprocess
import argparse
import venv
from pathlib import Path
import shutil

# Константы
SCRIPT_NAME = "ym-downloader"
VERSION = "1.0.1"
CONFIG_DIR = Path.home() / ".config" / SCRIPT_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
VENV_DIR = Path.home() / ".local" / "share" / SCRIPT_NAME / "venv"
DEFAULT_QUALITY = "2"
DEFAULT_DIR = "yandex-music-download"

# Справка
HELP_TEXT = f"""
{SCRIPT_NAME} v{VERSION} - Оболочка для yandex-music-downloader

Использование:
  {SCRIPT_NAME} [ОПЦИИ] [ССЫЛКА]
  {SCRIPT_NAME} -u ССЫЛКА [ОПЦИИ]
  {SCRIPT_NAME} --config
  {SCRIPT_NAME} -h

Опции оболочки:
  -h, --help            Показать эту справку
  -v, --version         Показать версию
  -y, --yes             Автоматически подтверждать загрузку (без запроса)
  -c, --config          Настроить параметры (токен, качество, директорию)
  -u URL, --url URL     Ссылка на трек/альбом/плейлист для загрузки
  -t TOKEN, --token TOKEN  Использовать указанный токен (временно)
  -q QUALITY, --quality QUALITY  Качество (0,1,2) (временно)
  -d DIR, --dir DIR     Директория для загрузки (временно)
  --reset-config        Сбросить настройки и удалить виртуальное окружение
  --reinstall           Переустановить yandex-music-downloader

Параметры передаваемые в yandex-music-downloader:
  Любые параметры, поддерживаемые yandex-music-downloader, можно передавать
  напрямую. Например: --skip-existing --embed-cover --lyrics-format lrc

Примеры:
  {SCRIPT_NAME} -u "https://music.yandex.ru/album/40745982/track/43805777"
  {SCRIPT_NAME} -y -u "https://music.yandex.ru/album/40745982"
  {SCRIPT_NAME} --skip-existing --embed-cover -u "https://music.yandex.ru/playlists/lk.12345"
  {SCRIPT_NAME} --config
"""

class YandexMusicWrapper:
    def __init__(self):
        self.config = self.load_config()
        self.venv_python = VENV_DIR / "bin" / "python"
        self.venv_bin = VENV_DIR / "bin" / "yandex-music-downloader"
        self.venv_pip = VENV_DIR / "bin" / "pip"

    def setup_venv(self):
        if not VENV_DIR.exists():
            print("🔧 Создание виртуального окружения...")
            venv.create(VENV_DIR, with_pip=True)
            print("✅ Виртуальное окружение создано")
        try:
            result = subprocess.run(
                [str(self.venv_python), "-c", "import ymd"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.install_package()
        except:
            self.install_package()

    def install_package(self):
        print("📦 Установка yandex-music-downloader...")
        subprocess.run([
            str(self.venv_pip), "install", "-U",
            "https://github.com/llistochek/yandex-music-downloader/archive/main.zip"
        ], check=True)
        print("✅ Пакет установлен")

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "token": None,
            "quality": DEFAULT_QUALITY,
            "dir": DEFAULT_DIR,
            "additional_params": []
        }

    def save_config(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✅ Настройки сохранены в {CONFIG_FILE}")

    def configure(self):
        print("\n=== Настройка Yandex Music Downloader ===\n")
        current_token = self.config.get("token", "")
        print("🔑 Токен авторизации (получить можно на https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)")
        if current_token:
            masked = current_token[:10] + "..." + current_token[-5:] if len(current_token) > 15 else "***"
            print(f"Текущий: {masked}")
        token = input("Введите токен (или Enter для сохранения текущего): ").strip()
        if token:
            self.config["token"] = token

        print("\n🎵 Качество треков: 0 - низкое, 1 - оптимальное, 2 - лучшее")
        current_quality = self.config.get("quality", DEFAULT_QUALITY)
        quality = input(f"Качество (0/1/2) [текущее: {current_quality}]: ").strip()
        if quality in ["0", "1", "2"]:
            self.config["quality"] = quality

        print("\n📁 Директория для загрузки")
        current_dir = self.config.get("dir", DEFAULT_DIR)
        dir_path = input(f"Путь [текущий: {current_dir}]: ").strip()
        if dir_path:
            self.config["dir"] = os.path.expanduser(dir_path)

        print("\n⚙️ Доп. параметры (например: --skip-existing --embed-cover)")
        current_params = " ".join(self.config.get("additional_params", []))
        params = input(f"Параметры [текущие: {current_params}]: ").strip()
        if params:
            self.config["additional_params"] = params.split()

        self.save_config()
        print("\n✅ Настройка завершена!")

    def extract_id_from_url(self, url):
        patterns = {
            'track': r'/track/(\d+)',
            'album': r'/album/(\d+)',
            'artist': r'/artist/(\d+)',
            'playlist_user': r'/users/([^/]+)/playlists/(\d+)',
            'playlist': r'/playlists/([^/?]+)'
        }
        for ctype, pattern in patterns.items():
            match = re.search(pattern, url)
            if match:
                if ctype == 'playlist_user':
                    user, pid = match.groups()
                    return ctype, f"{user}/{pid}"
                elif ctype == 'playlist':
                    return ctype, match.group(1)
                else:
                    return ctype, match.group(1)
        return None, None

    def get_command_for_type(self, content_type, content_id):
        if content_type == 'track':
            return ["--track-id", content_id]
        elif content_type == 'album':
            return ["--album-id", content_id]
        elif content_type == 'artist':
            return ["--artist-id", content_id]
        elif content_type in ['playlist', 'playlist_user']:
            return ["--playlist-id", content_id]
        else:
            return None

    def run_downloader(self, url, auto_confirm=False, cli_args=None):
        if not self.config.get("token"):
            print("❌ Токен не настроен. Запустите с --config.")
            return False
        content_type, content_id = self.extract_id_from_url(url)
        if not content_id:
            print(f"❌ Не удалось извлечь ID из ссылки: {url}")
            return False
        print(f"✅ Тип: {content_type}, ID: {content_id}")

        cmd = [
            str(self.venv_bin),
            "--token", self.config["token"],
            "--quality", self.config.get("quality", DEFAULT_QUALITY),
            "--dir", self.config.get("dir", DEFAULT_DIR)
        ]

        type_params = self.get_command_for_type(content_type, content_id)
        if type_params:
            cmd.extend(type_params)
        else:
            print("❌ Неподдерживаемый тип контента")
            return False

        if self.config.get("additional_params"):
            cmd.extend(self.config["additional_params"])

        if cli_args:
            skip_args = ['-y', '--yes', '-c', '--config', '--reset-config', '--reinstall']
            for i, arg in enumerate(cli_args):
                if arg in skip_args:
                    continue
                if arg in ['-u', '--url', '-t', '--token', '-q', '--quality', '-d', '--dir']:
                    if i + 1 < len(cli_args) and not cli_args[i+1].startswith('-'):
                        continue
                else:
                    cmd.append(arg)

        print(f"📋 Команда: {' '.join(cmd)}\n")
        if not auto_confirm:
            confirm = input("Запустить загрузку? (Y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '']:
                print("⏭️ Загрузка отменена")
                return False

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, bufsize=1)
            for line in process.stdout:
                print(line, end='')
            process.wait()
            if process.returncode == 0:
                print("\n✅ Загрузка завершена успешно!")
                return True
            else:
                print(f"\n❌ Ошибка при загрузке (код: {process.returncode})")
                return False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

    def reset_config(self):
        print("⚠️  Сброс настроек...")
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            print("✅ Конфигурация удалена")
        if VENV_DIR.exists():
            shutil.rmtree(VENV_DIR)
            print("✅ Виртуальное окружение удалено")
        print("✅ Сброс завершен")

    def reinstall(self):
        if VENV_DIR.exists():
            print("🔄 Переустановка пакета...")
            self.install_package()
        else:
            self.setup_venv()


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h','--help', action='store_true')
    parser.add_argument('-v','--version', action='store_true')
    parser.add_argument('-y','--yes', action='store_true')
    parser.add_argument('-c','--config', action='store_true')
    parser.add_argument('-u','--url', type=str)
    parser.add_argument('-t','--token', type=str)
    parser.add_argument('-q','--quality', type=str, choices=['0','1','2'])
    parser.add_argument('-d','--dir', type=str)
    parser.add_argument('--reset-config', action='store_true')
    parser.add_argument('--reinstall', action='store_true')
    args, unknown = parser.parse_known_args()

    wrapper = YandexMusicWrapper()

    if args.help:
        print(HELP_TEXT)
        subprocess.run([str(wrapper.venv_bin), "--help"] if wrapper.venv_bin.exists() else ["yandex-music-downloader", "--help"])
        return
    if args.version:
        print(f"{SCRIPT_NAME} v{VERSION}")
        return
    if args.reset_config:
        wrapper.reset_config()
        return
    if args.reinstall:
        wrapper.reinstall()
        return
    if args.config:
        wrapper.configure()
        return

    wrapper.setup_venv()

    # Применяем временные параметры
    if args.token:
        wrapper.config["token"] = args.token
    if args.quality:
        wrapper.config["quality"] = args.quality
    if args.dir:
        wrapper.config["dir"] = args.dir

    if not args.url:
        print(f"{SCRIPT_NAME} v{VERSION} - Загрузчик Яндекс.Музыки")
        print("Используйте -h для справки\n")
        while True:
            url = input("🔗 Введите ссылку (или 'exit'): ").strip()
            if url.lower() == 'exit':
                print("👋 До свидания!")
                break
            if not url:
                continue
            wrapper.run_downloader(url, auto_confirm=args.yes, cli_args=unknown)
            print()
    else:
        success = wrapper.run_downloader(args.url, auto_confirm=args.yes, cli_args=unknown)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
