# Каталог инструментов

Основной набор — инструменты, вокруг которых собран этот стек. Это не экспорт всех расширений личного аккаунта. Приватные и привязанные к аккаунту интеграции устанавливаются отдельно; список Claude-плагинов KISA не выдаётся за набор этого стека.

| Инструмент и источник | Тип | Когда использовать | Установка / размещение |
|---|---|---|---|
| [Context7](https://github.com/upstash/context7) | Hosted MCP + необязательный skill | Документация библиотек, API, миграции версий | MCP в конфиге Codex; [настройка](docs/INSTALL.md#context7) |
| [Refero](https://github.com/referodesign/refero_skill) · [доки](https://refero.design/mcp) | Плагин: MCP + skill refero-design | Рекомендуется, не обязателен: образцы реальных экранов, сценариев и стилей; живой поиск — платный тариф | [Установка](docs/INSTALL.md#refero--по-желанию) |
| [Impeccable](https://github.com/pbakaus/impeccable) · [доки](https://impeccable.style/docs/) | Проектный skill + CLI + hooks | Структура интерфейса, визуальная система, UX, доступность | `npx impeccable install` в выбранном проекте; Codex, local |
| [stack-start](skills/stack-start/SKILL.md) | Автоматически выбираемый skill стека | Новый проект: поставить Impeccable локально и передать работу в gsd-new-project | Ставится вместе с глобальными правилами и hooks (Codex; Claude Code — с `--claude-home`) |
| [Z.A.E.B.A.L.](https://github.com/howdeploy/Z.A.E.B.A.L) | Обязательный skill + UserPromptSubmit hook | Самопроверка при недовольстве работой агента | [Установка для Codex](docs/ZAEBAL.md) |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Плагин Codex и Claude Code: skills + хуки SessionStart, UserPromptSubmit, SubagentStart | Минимум нового кода после чтения существующего; правило подаётся в сессию и субагентов хуками | [Установка 5.2.0 и доверие хукам](docs/INSTALL.md#ponytail) |
| [Хуки Codex Stack](docs/HOOKS.md) | SessionStart, UserPromptSubmit, PostCompact | Напоминание маршрута проекта и Wiki | `python3 scripts/install_config.py --apply` |
| [Emil Design Engineering](https://github.com/emilkowalski/skills) | Skills | Анимация, реакции компонентов, жесты, polish | Выбрать `emil-design-eng` и Codex в `npx skills@latest add emilkowalski/skills` |
| [GSD Core](https://github.com/open-gsd/gsd-core) | CLI + skills + агенты | Единый процесс разработки: `gsd-next`, `gsd-new-project`, `gsd-onboard`, `gsd-quick --discuss`, `gsd-debug`, ревью и приёмка | `npx @opengsd/gsd-core@latest --codex --global` (Claude Code: `--claude`); [настройка](docs/INSTALL.md#gsd-core) |
| [RTK](https://github.com/rtk-ai/rtk) | CLI | Сокращение шумного вывода команд | `rtk init -g --codex`; читать `RTK.md` явно |
| [Graphify](https://github.com/Graphify-Labs/graphify) | CLI + skill | Связи в коде и поиск затрагиваемых частей | Пакет называется `graphifyy`, команда — `graphify` |
| [Agentation](https://github.com/benjitaylor/agentation) · [доки](https://www.agentation.com) | React + MCP | Разбор замечаний к выбранным элементам страницы | MCP глобально, компонент в конкретном dev-приложении |
| [ObsidianDataWeave](https://github.com/howdeploy/ObsidianDataWeave) | Python pipeline | Компиляция и поиск в общей LLM Wiki | Tools + отдельный venv, режим Codex |
| [researcher](https://github.com/howdeploy/kisa-stack/tree/main/skills/researcher) | Skill | Исследование с источниками и fallback | Из KISA через `$skill-installer`; Tavily не обязателен |

## Дополнительные модули

| Источник | Когда нужен | Подключение |
|---|---|---|
| [MTGA](https://github.com/howdeploy/MTGA) | Стиль ответов в чате; в стеке включён по умолчанию | [Установка](docs/INSTALL.md#mtga); выключение `$mtga off` / `/mtga:off` |
| [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) | Интервью для задач мимо GSD | Необязателен: в проектах на GSD интервью ведёт GSD |
| [Remotion](https://github.com/remotion-dev/remotion) · [доки](https://www.remotion.dev/docs/) | Видео на React | Только в выбранном видеопроекте; сверить лицензию для своего использования |
| [OpenAI skills](https://github.com/openai/skills) | Документы, таблицы, PDF и специальные задачи | Доступные встроенные skills или `$skill-installer`; не дублировать встроенное |

## Выбор инструмента агентом

- Начни с конкретной задачи, не загружай все skills.
- API и версия библиотеки → Context7: resolve → query → сверка с установленной версией.
- Новый UI или пересборка визуального решения → образцы в Refero, если подключён, затем Impeccable. Узкая доработка сохраняет существующий стиль.
- Поведение и движение элемента → `emil-design-eng`. Его рекомендации согласуются с доступностью и контекстом продукта.
- Любая разработка — через GSD: вход `gsd-next`; ревью — `gsd-code-review`, приёмка — `gsd-verify-work` с проверкой страниц в браузере. gstack из стека выведен.
- Ponytail работает через хуки во всех задачах с кодом: сокращает реализацию после изучения существующего паттерна. Его подсказки не отменяют согласованный scope и обязательные проверки.
- Agentation передаёт фидбек; изменение кода и проверка остаются работой агента в согласованном проекте.
- При конфликте рекомендаций решают запрос пользователя, требования продукта и реальные ограничения; skill не расширяет разрешения.
