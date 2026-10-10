# Каталог инструментов

Основной набор — инструменты, вокруг которых собран этот стек, для Claude Code и Codex. Это не экспорт всех расширений личного аккаунта. Приватные и привязанные к аккаунту интеграции устанавливаются отдельно; полный список Claude-плагинов KISA сюда не входит.

| Инструмент и источник | Тип | Когда использовать | Claude Code | Codex |
|---|---|---|---|---|
| [Context7](https://github.com/upstash/context7) | Hosted MCP + необязательный skill | Документация библиотек, API, миграции версий | `claude mcp add --scope user --transport http context7 …`, вход через `/mcp` | MCP в config.toml; [настройка](docs/INSTALL.md#context7) |
| [Impeccable](https://github.com/pbakaus/impeccable) · [доки](https://impeccable.style/docs/) | Проектный skill + CLI + hooks | Структура интерфейса, визуальная система, UX, доступность | `npx impeccable install --providers=claude --scope=project` | `--providers=codex`, local |
| [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) | Skill + grilling и domain-modeling | Интервью и требования; агент выбирает по обычному запросу | [Локальный старт через stack-start](docs/NEW-PROJECT.md), `.claude/skills/` | То же, `.agents/skills/` |
| [stack-start](skills/stack-start/SKILL.md) | Автоматически выбираемый skill стека | Подготовить локальный набор нового проекта, затем интервью и дизайн по необходимости | `install_config.py --host claude` | `--host codex` |
| [Z.A.E.B.A.L.](https://github.com/howdeploy/Z.A.E.B.A.L) | Обязательный skill + UserPromptSubmit hook | Самопроверка при недовольстве работой агента | [hook `--host claude`](docs/ZAEBAL.md) | hook `--host codex` |
| [Ponytail](https://github.com/DietrichGebert/ponytail) | Плагин: skills + lifecycle hooks | После чтения кода выбрать простейшее корректное решение без лишних абстракций | `/plugin install ponytail@ponytail` | [codex plugin add](docs/INSTALL.md#ponytail) |
| [Хуки Codex Stack](docs/HOOKS.md) | SessionStart, UserPromptSubmit (+ PostCompact в Codex) | Напоминание маршрута проекта и Wiki | `install_config.py --host claude --apply` | `--host codex --apply` |
| [Emil Design Engineering](https://github.com/emilkowalski/skills) | Skills | Анимация, реакции компонентов, жесты, polish | `npx skills@latest add emilkowalski/skills --skill emil-design-eng --agent claude-code --global` | `--agent codex` |
| [gstack](https://github.com/garrytan/gstack) | CLI + skills | План, code review, браузерный QA, выпуск | Клон в `~/.claude/skills/gstack`, `./setup` | Общий каталог Tools; `./setup --host codex` |
| [GSD Core](https://github.com/open-gsd/gsd-core) | CLI + skills + агенты | Большие задачи с этапами и передачей контекста | `npx @opengsd/gsd-core@latest --claude --global` | `--codex --global` |
| [RTK](https://github.com/rtk-ai/rtk) | CLI | Сокращение шумного вывода команд | `rtk init -g` (PreToolUse hook) | `rtk init -g --codex`; читать `RTK.md` явно |
| [Graphify](https://github.com/Graphify-Labs/graphify) | CLI + skill | Связи в коде и поиск затрагиваемых частей | `graphify install` | `graphify install --platform codex` |
| [Agentation](https://github.com/benjitaylor/agentation) · [доки](https://www.agentation.com) | React + MCP | Разбор замечаний к выбранным элементам страницы | `claude mcp add --scope user agentation …` | `codex mcp add agentation …` |
| [ObsidianDataWeave](https://github.com/howdeploy/ObsidianDataWeave) | Python pipeline | Компиляция и поиск в общей LLM Wiki | Tools + venv, `--mode claude` | `--mode codex` |
| [researcher](https://github.com/howdeploy/kisa-stack/tree/main/skills/researcher) | Skill | Исследование с источниками и fallback | `./install.sh researcher --claude` из KISA | `$skill-installer`; Tavily не обязателен |

Пакет Graphify называется `graphifyy`, команда — `graphify`. Подробные команды и проверки — в [INSTALL.md](docs/INSTALL.md).

## Дополнительные модули

| Источник | Когда нужен | Подключение |
|---|---|---|
| [MTGA](https://github.com/howdeploy/MTGA) | Нужен характерный стиль ответов | Плагин Claude Code (`/mtga:on`) или скрипт для Codex; код и документы обычные |
| [Remotion](https://github.com/remotion-dev/remotion) · [доки](https://www.remotion.dev/docs/) | Видео на React | Только в выбранном видеопроекте; сверить лицензию для своего использования |
| [Anthropic skills](https://github.com/anthropics/skills) · [OpenAI skills](https://github.com/openai/skills) | Документы, таблицы, PDF и специальные задачи | Встроенные skills своего хоста; не дублировать встроенное |

## Выбор инструмента агентом

- Начни с конкретной задачи, не загружай все skills.
- API и версия библиотеки → Context7: resolve → query → сверка с установленной версией.
- Новый UI или пересборка визуального решения → Impeccable. Узкая доработка сохраняет существующий стиль.
- Поведение и движение элемента → `emil-design-eng`. Его рекомендации согласуются с доступностью и контекстом продукта.
- Для большого этапа — GSD; для ревью и QA — соответствующий gstack skill. Не запускай два параллельных процесса планирования одной задачи.
- Для задач с кодом Ponytail помогает сократить реализацию после изучения существующего паттерна. Его подсказки не отменяют явный scope и обязательные проверки.
- Agentation передаёт фидбек; изменение кода и проверка остаются работой агента в согласованном проекте.
- При конфликте рекомендаций решают запрос пользователя, требования продукта и реальные ограничения; skill не расширяет разрешения.
