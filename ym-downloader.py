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
VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".config" / SCRIPT_NAME
CONFIG_FILE = CONFIG_DIR / "config.json"
VENV_DIR = Path.home() / ".local" / "share" / SCRIPT_NAME / "venv"
DEFAULT_QUALITY = "2"
DEFAULT_DIR = "yandex-music-download"

# Шаблон для справки
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
        self.venv_pip = VENV_DIR / "bin" / "pip"
        
    def setup_venv(self):
        """Создает виртуальное окружение и устанавливает пакет"""
        if not VENV_DIR.exists():
            print("🔧 Создание виртуального окружения...")
            venv.create(VENV_DIR, with_pip=True)
            print("✅ Виртуальное окружение создано")
        
        # Проверяем, установлен ли пакет
        try:
            result = subprocess.run(
                [str(self.venv_python), "-c", "import ymd; print('ok')"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.install_package()
        except:
            self.install_package()
    
    def install_package(self):
        """Устанавливает yandex-music-downloader"""
        print("📦 Установка yandex-music-downloader...")
        subprocess.run([
            str(self.venv_pip), "install", "-U",
            "https://github.com/llistochek/yandex-music-downloader/archive/main.zip"
        ], check=True)
        print("✅ Пакет установлен")
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
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
        """Сохраняет конфигурацию в файл"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✅ Настройки сохранены в {CONFIG_FILE}")
    
    def configure(self):
        """Интерактивная настройка параметров"""
        print("\n=== Настройка Yandex Music Downloader ===\n")
        
        # Токен
        current_token = self.config.get("token", "")
        print("🔑 Токен авторизации (получить можно на https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)")
        if current_token:
            masked = current_token[:10] + "..." + current_token[-5:] if len(current_token) > 15 else "***"
            print(f"Текущий: {masked}")
        
        token = input("Введите токен (или Enter для сохранения текущего): ").strip()
        if token:
            self.config["token"] = token
        
        # Качество
        print("\n🎵 Качество треков:")
        print("  0 - Низкое (AAC 64kbps)")
        print("  1 - Оптимальное (AAC 192kbps)")
        print("  2 - Лучшее (FLAC)")
        current_quality = self.config.get("quality", DEFAULT_QUALITY)
        quality = input(f"Качество (0/1/2) [текущее: {current_quality}]: ").strip()
        if quality in ["0", "1", "2"]:
            self.config["quality"] = quality
        
        # Директория
        print("\n📁 Директория для загрузки")
        current_dir = self.config.get("dir", DEFAULT_DIR)
        dir_path = input(f"Путь [текущий: {current_dir}]: ").strip()
        if dir_path:
            # Преобразуем ~ в домашнюю директорию
            dir_path = os.path.expanduser(dir_path)
            self.config["dir"] = dir_path
        
        # Дополнительные параметры
        print("\n⚙️ Дополнительные параметры (будут добавляться к каждой команде)")
        print("Например: --skip-existing --embed-cover --lyrics-format lrc")
        current_params = " ".join(self.config.get("additional_params", []))
        params = input(f"Параметры [текущие: {current_params}]: ").strip()
        if params:
            self.config["additional_params"] = params.split()
        
        self.save_config()
        print("\n✅ Настройка завершена!")
    
    def extract_id_from_url(self, url):
        """Извлекает ID из ссылки Яндекс.Музыки"""
        patterns = {
            'track': r'/track/(\d+)',
            'album': r'/album/(\d+)',
            'artist': r'/artist/(\d+)',
            'playlist_user': r'/users/([^/]+)/playlists/(\d+)',
            'playlist': r'/playlists/([^/?]+)'
        }
        
        for content_type, pattern in patterns.items():
            match = re.search(pattern, url)
            if match:
                if content_type == 'playlist_user':
                    user, playlist_id = match.groups()
                    return content_type, f"{user}/{playlist_id}"
                elif content_type == 'playlist':
                    return content_type, match.group(1)
                else:
                    return content_type, match.group(1)
        
        return None, None
    
    def get_command_for_type(self, content_type, content_id):
        """Возвращает команду для соответствующего типа контента"""
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
        """Запускает загрузчик с параметрами"""
        if not self.config.get("token"):
            print("❌ Токен не настроен. Запустите с флагом --config для настройки.")
            return False
        
        # Извлекаем ID из ссылки
        content_type, content_id = self.extract_id_from_url(url)
        
        if not content_id:
            print(f"❌ Не удалось извлечь ID из ссылки: {url}")
            return False
        
        print(f"✅ Тип: {content_type}, ID: {content_id}")
        
        # Формируем команду
        cmd = [
            str(self.venv_python), "-m", "ymd.cli",
            "--token", self.config["token"],
            "--quality", self.config.get("quality", DEFAULT_QUALITY),
            "--dir", self.config.get("dir", DEFAULT_DIR)
        ]
        
        # Добавляем параметры для типа контента
        type_params = self.get_command_for_type(content_type, content_id)
        if type_params:
            cmd.extend(type_params)
        else:
            print(f"❌ Неподдерживаемый тип контента")
            return False
        
        # Добавляем дополнительные параметры из конфига
        if self.config.get("additional_params"):
            cmd.extend(self.config["additional_params"])
        
        # Добавляем параметры из командной строки (они переопределяют конфиг)
        if cli_args:
            # Фильтруем аргументы, которые уже обработаны оболочкой
            skip_args = ['-y', '--yes', '-c', '--config', '--reset-config', '--reinstall']
            for i, arg in enumerate(cli_args):
                if arg in skip_args:
                    continue
                if arg in ['-u', '--url', '-t', '--token', '-q', '--quality', '-d', '--dir']:
                    # Пропускаем сам флаг и его значение
                    if i + 1 < len(cli_args) and not cli_args[i+1].startswith('-'):
                        continue
                else:
                    cmd.append(arg)
        
        print(f"📋 Команда: {' '.join(cmd)}\n")
        
        # Запрашиваем подтверждение если не auto_confirm
        if not auto_confirm:
            confirm = input("Запустить загрузку? (Y/n): ").strip().lower()
            if confirm not in ['y', 'yes', '']:
                print("⏭️ Загрузка отменена")
                return False
        
        # Запускаем процесс
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                      text=True, bufsize=1, universal_newlines=True)
            
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
        """Сбрасывает настройки и удаляет виртуальное окружение"""
        print("⚠️  Сброс настроек...")
        
        # Удаляем конфиг
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            print("✅ Конфигурация удалена")
        
        # Удаляем виртуальное окружение
        if VENV_DIR.exists():
            shutil.rmtree(VENV_DIR)
            print("✅ Виртуальное окружение удалено")
        
        print("✅ Сброс завершен")
    
    def reinstall(self):
        """Переустанавливает пакет"""
        if VENV_DIR.exists():
            print("🔄 Переустановка пакета...")
            self.install_package()
        else:
            self.setup_venv()

def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help='Показать справку')
    parser.add_argument('-v', '--version', action='store_true', help='Показать версию')
    parser.add_argument('-y', '--yes', action='store_true', help='Автоматически подтверждать загрузку')
    parser.add_argument('-c', '--config', action='store_true', help='Настроить параметры')
    parser.add_argument('-u', '--url', type=str, help='Ссылка для загрузки')
    parser.add_argument('-t', '--token', type=str, help='Токен (временно)')
    parser.add_argument('-q', '--quality', type=str, choices=['0','1','2'], help='Качество (временно)')
    parser.add_argument('-d', '--dir', type=str, help='Директория загрузки (временно)')
    parser.add_argument('--reset-config', action='store_true', help='Сбросить настройки')
    parser.add_argument('--reinstall', action='store_true', help='Переустановить пакет')
    
    # Остальные аргументы будут переданы в yandex-music-downloader
    args, unknown = parser.parse_known_args()
    
    # Инициализируем оболочку
    wrapper = YandexMusicWrapper()
    
    # Обработка специальных флагов
    if args.help:
        print(HELP_TEXT)
        # Показываем справку оригинального загрузчика
        print("\n=== Справка yandex-music-downloader ===\n")
        subprocess.run(["yandex-music-downloader", "--help"] if shutil.which("yandex-music-downloader") 
                      else [str(wrapper.venv_python), "-m", "ymd.cli", "--help"])
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
    
    # Настраиваем виртуальное окружение
    wrapper.setup_venv()
    
    # Если нет ссылки, запрашиваем в интерактивном режиме
    if not args.url:
        print(f"{SCRIPT_NAME} v{VERSION} - Загрузчик Яндекс.Музыки")
        print("Используйте -h для справки\n")
        
        # Применяем временные параметры если есть
        if args.token:
            wrapper.config["token"] = args.token
        if args.quality:
            wrapper.config["quality"] = args.quality
        if args.dir:
            wrapper.config["dir"] = args.dir
        
        # Интерактивный режим
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
        # Режим командной строки с одной ссылкой
        # Применяем временные параметры
        if args.token:
            wrapper.config["token"] = args.token
        if args.quality:
            wrapper.config["quality"] = args.quality
        if args.dir:
            wrapper.config["dir"] = args.dir
        
        success = wrapper.run_downloader(args.url, auto_confirm=args.yes, cli_args=unknown)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
