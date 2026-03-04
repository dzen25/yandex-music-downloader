# Yandex Music Downloader Wrapper 🎵

Универсальная оболочка-обёртка для [yandex-music-downloader](https://github.com/llistochek/yandex-music-downloader) с автоматическим управлением виртуальным окружением, сохранением настроек и удобным интерфейсом.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux/macOS](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey)](https://github.com/yourusername/ym-downloader)

## 🌟 Возможности

- **Автоматическое создание виртуального окружения** — изоляция зависимостей, никакого мусора в системе
- **Сохранение настроек** — токен, качество, директория и параметры сохраняются в конфиг
- **Умное извлечение ID** — просто вставьте ссылку на трек, альбом, плейлист или исполнителя
- **Поддержка всех параметров** оригинального загрузчика
- **Два режима работы**: интерактивный и командная строка
- **Автоподтверждение** (`-y`) для пакетной обработки
- **Временные параметры** — переопределяйте токен, качество или директорию без изменения конфига
- **Кроссплатформенность** — работает на Linux и macOS

## 📦 Установка

### Быстрая установка (рекомендуется)

```bash
# Скачать скрипт
wget https://raw.githubusercontent.com/dzen25/yandex-music-downloader/refs/heads/main/ym-downloader

# Сделать исполняемым и переместить в PATH
chmod +x ym-downloader
sudo mv ym-downloader /usr/local/bin/
```

### Ручная установка

```bash
# Клонировать репозиторий
git clone https://github.com/dzen25/yandex-music-downloader
cd ym-downloader

# Сделать скрипт исполняемым
chmod +x ym-downloader

# Переместить в PATH
sudo ln -s $(pwd)/ym-downloader /usr/local/bin/ym-downloader
```

## 🔧 Первоначальная настройка

При первом запуске выполните настройку:

```bash
ym-downloader --config
```

Скрипт запросит:
1. **Токен авторизации** — получите по [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d)
   - после открытия данной ссылки вам нужно будет авторизоватся если вы этого не сделали, а затем скопировать часть ссылки от `https://music.yandex.ru/#access_token=` и до `&token_type=bearer`. Это и будет вашим токеном вида: `y0__xDxxxxxxxxxxxxxx`
2. **Качество загрузки**:
   - `0` — Низкое (AAC 64kbps)
   - `1` — Оптимальное (AAC 192kbps)
   - `2` — Лучшее (FLAC)
3. **Директорию для загрузки** (по умолчанию: `yandex-music-download`) (указывается полный путь)
4. **Дополнительные параметры** — например: `--skip-existing --embed-cover`

Настройки сохраняются в `~/.config/ym-downloader/config.json`

## 🚀 Использование

### Интерактивный режим

Просто запустите скрипт без аргументов:

```bash
ym-downloader
```

Скрипт будет запрашивать ссылки в цикле. Для выхода введите `exit`.

### Командная строка (одна ссылка)

```bash
ym-downloader -u "https://music.yandex.ru/album/40745982/track/43805777"
```

### С автоподтверждением

```bash
# Интерактивный режим с автоподтверждением
ym-downloader -y

# Командный режим с автоподтверждением
ym-downloader -y -u "https://music.yandex.ru/album/40745982"
```

### Временные параметры

Переопределите настройки без сохранения в конфиг:

```bash
ym-downloader -u "ссылка" -q 2 -d ~/Music -t "ваш_токен"
```

### Дополнительные параметры загрузчика

Все параметры оригинального загрузчика работают напрямую:

```bash
ym-downloader -u "https://music.yandex.ru/album/40745982" \
  --skip-existing \
  --embed-cover \
  --lyrics-format lrc \
  --cover-resolution 600
```

### Поддерживаемые типы ссылок

| Тип | Пример ссылки | Команда |
|------|---------------|---------|
| Трек | `https://music.yandex.ru/album/40745982/track/43805777` | `--track-id 43805777` |
| Альбом | `https://music.yandex.ru/album/40745982` | `--album-id 40745982` |
| Исполнитель | `https://music.yandex.ru/artist/368148` | `--artist-id 368148` |
| Плейлист | `https://music.yandex.ru/playlists/lk.531edaf4-52b5-401c-8651-1327f58e0df5` | `--playlist-id lk/531edaf4...` |

## 📋 Команды оболочки

| Команда | Описание |
|---------|----------|
| `-h, --help` | Показать справку |
| `-v, --version` | Показать версию |
| `-y, --yes` | Автоматически подтверждать загрузку |
| `-c, --config` | Настроить параметры |
| `-u URL, --url URL` | Ссылка для загрузки |
| `-t TOKEN, --token TOKEN` | Использовать указанный токен (временно) |
| `-q {0,1,2}, --quality {0,1,2}` | Качество (временно) |
| `-d DIR, --dir DIR` | Директория для загрузки (временно) |
| `--reset-config` | Сбросить настройки и удалить виртуальное окружение |
| `--reinstall` | Переустановить yandex-music-downloader |

## ⚙️ Конфигурация

Файл конфигурации: `~/.config/ym-downloader/config.json`

Пример:
```json
{
  "token": "y0_xxxxx...",
  "quality": "2",
  "dir": "/home/user/Music/yandex",
  "additional_params": ["--skip-existing", "--embed-cover"]
}
```

## 📁 Структура проекта

```
~/.config/ym-downloader/
  └── config.json          # Настройки пользователя

~/.local/share/ym-downloader/
  └── venv/                 # Виртуальное окружение
      ├── bin/
      ├── lib/
      └── ...
```

## 🐛 Решение проблем

### Ошибка "Токен не настроен"
Запустите `ym-downloader --config` и введите токен.

### Ошибки при установке пакета
Попробуйте переустановить:
```bash
ym-downloader --reinstall
```

### Сброс всех настроек
```bash
ym-downloader --reset-config
```

### Проблемы с правами доступа
Убедитесь, что директория для загрузки доступна для записи:
```bash
mkdir -p ~/yandex-music-download
ym-downloader -d ~/yandex-music-download -u "ссылка"
```

## 🔄 Интеграция с другими скриптами

### Пакетная загрузка из файла со списком ссылок

```bash
#!/bin/bash
while read url; do
  ym-downloader -y -u "$url"
done < links.txt
```

### Загрузка по расписанию (cron)

```bash
# Добавить в crontab (crontab -e)
0 10 * * * /usr/local/bin/ym-downloader -y -u "https://music.yandex.ru/playlists/lk.12345" >> ~/ym-downloader.log 2>&1
```

## 📝 Требования

- Python 3.6 или выше
- pip (устанавливается вместе с Python)
- Поддержка виртуальных окружений (venv)
- 100+ MB свободного места для виртуального окружения

## 🙏 Благодарности

- [llistochek](https://github.com/llistochek) за отличный [yandex-music-downloader](https://github.com/llistochek/yandex-music-downloader)

## ⭐ Поддержка проекта

Если вам понравился проект, поставьте звезду на GitHub — это мотивирует развивать его дальше!

Нашли баг или есть предложение? Создайте [issue](https://github.com/yourusername/ym-downloader/issues) или отправьте pull request.
