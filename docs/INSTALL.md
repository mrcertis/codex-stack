# Полная установка

Команды ниже — для macOS/Linux или WSL. Выполняйте разделы по очереди, а не одним
блоком. Стек ставится для одного или двух хостов: **Claude Code** (основной
сценарий) и **Codex**. В каждом разделе сначала команды Claude Code, затем Codex.
Ставьте только для того хоста, которым пользуетесь; конфигурации хостов не
взаимозаменяемы.

Требуются авторизованный Claude Code или Codex, Git, Node.js LTS, Python 3.11+, uv
и Bun. Устанавливайте системные prerequisites по документации их поставщиков.
Версии upstream меняются: сверяйте --help и сохраняйте версии в локальном отчёте.

## Пути и резервная копия

Выберите общий каталог инструментов и общий Obsidian vault. Пример:

```bash
STACK_TOOLS="$HOME/Documents/Codex/Tools"
STACK_VAULT="$HOME/Documents/Codex/Knowledge"
STACK_CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
STACK_CODEX="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$STACK_TOOLS" "$STACK_VAULT"
STACK_BACKUP="$STACK_TOOLS/stack-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$STACK_BACKUP/claude" "$STACK_BACKUP/codex"
chmod 700 "$STACK_BACKUP"
for stack_file in CLAUDE.md settings.json PROJECTS.md; do
  if [ -f "$STACK_CLAUDE/$stack_file" ]; then
    cp -p "$STACK_CLAUDE/$stack_file" "$STACK_BACKUP/claude/"
  fi
done
for stack_file in AGENTS.md config.toml hooks.json RTK.md PROJECTS.md; do
  if [ -f "$STACK_CODEX/$stack_file" ]; then
    cp -p "$STACK_CODEX/$stack_file" "$STACK_BACKUP/codex/"
  fi
done
```

Все дальнейшие shell-примеры предполагают эти переменные в том же терминале.
Backup приватный, вне checkout. MCP-серверы Claude Code уровня user хранятся
в `~/.claude.json`; перед ручной правкой этого файла сохраните и его копию.
При повторном запуске не клонируйте поверх существующих каталогов: сначала
проверьте remote и локальные изменения.

## Глобальные правила

Из корня этого checkout выполните dry run, затем применение.

**Claude Code:**

```bash
python3 scripts/install_config.py --host claude --claude-home "$STACK_CLAUDE" --tools-root "$STACK_TOOLS" --wiki-root "$STACK_VAULT/LLM Wiki"
python3 scripts/install_config.py --host claude --claude-home "$STACK_CLAUDE" --tools-root "$STACK_TOOLS" --wiki-root "$STACK_VAULT/LLM Wiki" --apply
```

Скрипт добавляет [шаблон](../global-config/CLAUDE.md) в `~/.claude/CLAUDE.md`
**блоком между маркерами** `<!-- codex-stack:begin -->` и `<!-- codex-stack:end -->`.
Остальное содержимое CLAUDE.md, в том числе блоки других установщиков, сохраняется;
повторный запуск заменяет только этот блок. Хуки добавляются в ключ `hooks`
файла `settings.json`, прочие ключи (permissions, env, model, плагины) не меняются.
[Правила памяти Claude Code](https://code.claude.com/docs/en/memory).

**Codex:**

```bash
python3 scripts/install_config.py --host codex --codex-home "$STACK_CODEX" --tools-root "$STACK_TOOLS" --wiki-root "$STACK_VAULT/LLM Wiki"
python3 scripts/install_config.py --host codex --codex-home "$STACK_CODEX" --tools-root "$STACK_TOOLS" --wiki-root "$STACK_VAULT/LLM Wiki" --apply
```

Старый глобальный AGENTS.md полностью заменяется [шаблоном](../global-config/AGENTS.md),
а не объединяется с ним. config.toml не изменяется. AGENTS.override.md требует
отдельного рассмотрения, поскольку затеняет AGENTS.md.
[Правила Codex](https://developers.openai.com/codex/guides/agents-md/).

Для обоих хостов скрипт подставляет пути, сохраняет приватную резервную копию
и добавляет свои хуки с сохранением чужих. [Состав хуков и откат](HOOKS.md).
[PROJECTS.example.md](../global-config/PROJECTS.example.md) — образец для нового
приватного реестра (`~/.claude/PROJECTS.md` или `~/.codex/PROJECTS.md`).
Существующий PROJECTS.md не заменяйте.

## Context7

Источник: [upstash/context7](https://github.com/upstash/context7).

Сначала проверьте, нет ли уже рабочей записи `context7`. Выберите **один** вариант.

**Claude Code, OAuth:** добавьте hosted MCP на уровне пользователя:

```bash
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp
```

Затем в сеансе Claude Code откройте `/mcp`, выберите context7 и выполните вход.
Браузерный вход делает владелец. Готовый JSON-фрагмент —
[mcp.claude.example.json](../global-config/mcp.claude.example.json).
[MCP в Claude Code](https://code.claude.com/docs/en/mcp).

**Claude Code, API key:** передайте свой ключ из переменной окружения заголовком
Authorization, не вставляя его в публичные файлы:

```bash
claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp --header "Authorization: Bearer $CONTEXT7_API_KEY"
```

**Codex, OAuth:**

```bash
codex mcp add context7 --url https://mcp.context7.com/mcp
codex mcp login context7
```

**Codex, API key:** передайте ключ процессу Codex через переменную
`CONTEXT7_API_KEY` и добавьте фрагмент из [mcp.example.toml](../global-config/mcp.example.toml)
с `bearer_token_env_var`. Поля: [документация MCP Codex](https://developers.openai.com/codex/mcp/).

Не вставляйте реальный ключ в публичный конфиг, issue или чат. Переменная
терминала может быть недоступна desktop-приложению; перезапустите его с нужным
окружением либо используйте OAuth. Не включайте одновременно две записи сервера.

Альтернатива — официальный мастер `npx ctx7 setup` (флаг `--claude` для Claude Code);
проверьте его изменения. Он может также установить skill и правило использования.
Не запускайте мастер поверх уже рабочего подключения ради дублирующей записи.

Проверка в новом сеансе: попросите найти Context7 ID React и вернуть документацию
по cleanup в useEffect. Должны выполниться resolve-library-id и query-docs.

## Impeccable

Источник: [pbakaus/impeccable](https://github.com/pbakaus/impeccable), [доки](https://impeccable.style/docs/).

Impeccable входит в начальный локальный набор **каждого нового проекта**, до
интервью и выбора UI. Это автоматически организует агент через stack-start.
Для адресной ручной установки запускайте команду **из папки проекта**:

```bash
npx impeccable install --providers=claude --scope=project   # Claude Code
npx impeccable install --providers=codex --scope=project    # Codex
```

Ожидаемый путь: `.claude/skills/impeccable/SKILL.md` для Claude Code и
`.agents/skills/impeccable/SKILL.md` для Codex. Глобально Impeccable в этом
стеке не устанавливается (в том числе плагином `/plugin`). Если глобальная копия
уже существует, проверьте конфликт обнаружения и согласуйте её отключение
отдельно; не удаляйте её молча.

Установщик добавляет проектные хуки: в Claude Code — в `.claude/settings.local.json`,
в Codex — в `.codex/hooks.json` (PostToolUse и Stop). Проверьте, что чужие
обработчики сохранились. В Claude Code просмотрите их через `/hooks`; в Codex
подтвердите доверие через Settings → Hooks или `/hooks`. [Документация hooks](https://impeccable.style/docs/hooks/).
При работе агент сам выбирает Impeccable после интервью, если нужен интерфейс;
пользователю не нужно вызывать его команду. `init` создаёт PRODUCT.md; DESIGN.md
фиксируется по завершении реализации согласно playbook. [Процесс](NEW-PROJECT.md).
Обновление из того же проекта: `npx impeccable update`.

## Интервью нового проекта и Z.A.E.B.A.L.

Установите [grill-with-docs и его зависимости](NEW-PROJECT.md), затем
[обязательный Z.A.E.B.A.L.](ZAEBAL.md). Один skill без UserPromptSubmit hook
не завершает настройку Z.A.E.B.A.L. Стековые хуки уже поставлены шагом глобальных
правил; реальный запуск проверяется отдельно.

## Ponytail

Источник: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail).
Плагин выбирает простую реализацию после изучения затронутого кода. Его hooks
требуют Node.js. Перед установкой проверьте исходники и текущий commit репозитория.

**Claude Code** — две отдельные команды в сеансе:

```
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

Проверьте плагин и его hooks через `/plugin` и `/hooks`, затем откройте новый сеанс.
Откат: `/plugin uninstall ponytail@ponytail`.

**Codex:**

```bash
codex plugin marketplace add DietrichGebert/ponytail --ref v4.10.0
codex plugin add ponytail@ponytail
codex plugin list
```

После установки откройте `/hooks`, просмотрите команды Ponytail и подтвердите
доверие к ним. Перезапустите Codex Desktop и откройте новую задачу. Режим меняется
`@ponytail lite` и `@ponytail off`. Откат: `codex plugin remove ponytail`.

Не переносите правила Ponytail целиком в CLAUDE.md или AGENTS.md: явный запрос,
безопасность и нужные проверки остаются приоритетными.

## Emil Design Engineering

Источник: [emilkowalski/skills](https://github.com/emilkowalski/skills).

```bash
npx skills@latest add emilkowalski/skills --skill emil-design-eng --agent claude-code --global   # Claude Code
npx skills@latest add emilkowalski/skills --skill emil-design-eng --agent codex --global         # Codex
```

Дополнительный `review-animations` выбирайте при необходимости. Не ставьте все
skills автоматически: в разных наборах могут совпадать имена, например animate.
Проверьте, что есть SKILL.md и агент видит skill: `/emil-design-eng` в Claude Code,
`$emil-design-eng` в Codex.

## gstack

Источник: [garrytan/gstack](https://github.com/garrytan/gstack). Требуется Bun.

**Claude Code** — путь из README gstack:

```bash
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git "$STACK_CLAUDE/skills/gstack"
cd "$STACK_CLAUDE/skills/gstack"
./setup
```

**Codex:**

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git "$STACK_TOOLS/gstack"
cd "$STACK_TOOLS/gstack"
./setup --host codex
```

Прочитайте setup перед запуском. Для Codex он создаёт отдельную версию skills;
не копируйте Claude-набор вручную. Проверьте browse и review в новом сеансе.
Браузерный путь выбирается по текущему SKILL.md. Для Chromium нужны загрузка
браузера и разрешения ОС. Само обнаружение skill не доказывает, что браузер открывается.

## GSD Core

Источник: [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core).

```bash
npx @opengsd/gsd-core@latest --claude --global   # Claude Code
npx @opengsd/gsd-core@latest --codex --global    # Codex
```

Сохраните существующую конфигурацию и проверьте diff после установки.
Точные пути смотрите в отчёте установщика. Проверьте gsd-help в новом сеансе.
Полный процесс разработки проверяется на отдельной задаче: обнаружение агентов
не доказывает поддержку всех режимов делегирования вашим рантаймом.

## RTK

Источник: [rtk-ai/rtk](https://github.com/rtk-ai/rtk).

macOS с Homebrew:

```bash
brew install rtk
rtk --version
rtk init -g          # Claude Code: PreToolUse hook + RTK.md
rtk init -g --codex  # Codex
```

На Linux используйте официальный способ из README RTK для вашей ОС.
В Claude Code хук переписывает только Bash-команды; Read, Grep и Glob через него
не проходят. Для Codex проверьте diff AGENTS.md после init и сохраните прежние
правила: явное чтение RTK.md надёжнее предположения, что `@...` разворачивается.
Проверка в Git-репозитории: `rtk git status`, затем `rtk gain`.

## Graphify

Источник: [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
(ранее safishamsi/graphify).

```bash
uv tool install graphifyy
graphify --help
graphify install                    # Claude Code
graphify install --platform codex   # Codex
```

Если graphifyy уже установлен, не обновляйте без причины. Проверяйте созданный
skill и выполняйте первый анализ на маленьком тестовом проекте по текущему
SKILL.md. Граф строится отдельно для проекта. Не индексируйте весь home.
Платные semantic backends не включаются одной установкой CLI.

## ObsidianDataWeave и общая Wiki

Источник: [howdeploy/ObsidianDataWeave](https://github.com/howdeploy/ObsidianDataWeave).

```bash
git clone https://github.com/howdeploy/ObsidianDataWeave.git "$STACK_TOOLS/ObsidianDataWeave"
cd "$STACK_TOOLS/ObsidianDataWeave"
python3 -m venv .venv
```

Прочитайте AGENTS.md и install.sh. Затем выберите режим своего хоста:

```bash
PATH="$PWD/.venv/bin:$PATH" bash install.sh --mode claude --vault-path "$STACK_VAULT"   # Claude Code
PATH="$PWD/.venv/bin:$PATH" bash install.sh --mode codex --vault-path "$STACK_VAULT"    # Codex
.venv/bin/python scripts/doctor.py
```

Режим claude регистрирует навык в `~/.claude/skills/` и добавляет свой блок
в `~/.claude/CLAUDE.md`; он не пересекается с блоком Codex Stack.

Создание Wiki — отдельная явная часть настройки знания. Если пользователь её
разрешил, создайте space и проверьте на публичном небольшом входном документе:

```bash
.venv/bin/python scripts/wiki_init.py codex --mode project --title "Codex Stack" --lang ru
.venv/bin/python scripts/wiki_ingest.py codex /absolute/path/to/public-input.md --kind docs
.venv/bin/python scripts/wiki_compile.py codex --backend claude   # или --backend codex
.venv/bin/python scripts/wiki_lint.py codex --strict
```

Space стека называется `codex` для обоих хостов. Подставьте существующий
public-input.md. Читайте --help установленной версии при расхождении флагов.
Компиляция вызывает LLM backend: используйте разрешённые данные.
Не перезаписывайте существующий space; дальнейшие обновления проходят через
штатный writer. Google Drive и NotebookLM — опциональны и требуют личного входа.
Отсутствие их авторизации не равно неработающей локальной Wiki.

Напоминание о Wiki входит в [поставляемые хуки](HOOKS.md). Сами хуки не пишут в Wiki.

## researcher

**Claude Code:** установщик KISA из клона репозитория:

```bash
git clone --depth 1 https://github.com/howdeploy/kisa-stack.git "$STACK_TOOLS/kisa-stack"
cd "$STACK_TOOLS/kisa-stack"
./install.sh researcher --claude
```

**Codex:** попросите встроенный `$skill-installer` установить
https://github.com/howdeploy/kisa-stack/tree/main/skills/researcher

Прочитайте install.sh перед запуском. В новом сеансе должен появиться researcher.
Пусть агент проверит доступные web-инструменты; наличие Tavily не предполагается.
Первый smoke-test — краткий ответ по публичному источнику со ссылкой.

## Agentation

Источник: [benjitaylor/agentation](https://github.com/benjitaylor/agentation).
Глобальное подключение MCP:

```bash
claude mcp add --scope user agentation -- npx -y agentation-mcp@1.2.0 server   # Claude Code
codex mcp add agentation -- npx -y agentation-mcp@1.2.0 server                 # Codex
```

Версия 1.2.0 — проверенная исходная версия этой сборки, не утверждение о latest.
Если desktop не видит Node/npx, укажите абсолютные пути. Для медленного первого
запуска в Codex установите startup_timeout_sec = 30, как в образце TOML.
Проверяйте список сессий через MCP и `http://127.0.0.1:4747/health`.

**Проектная часть:** выберите конкретное React-приложение, используйте его менеджер
пакетов и добавьте пакет `agentation`. Компонент монтируется один раз и только в dev:

```tsx
// Пример client-компонента Next.js. Импортируйте его из layout.
"use client";
import { Agentation } from "agentation";

export function DevFeedback() {
  if (process.env.NODE_ENV !== "development") return null;
  return <Agentation endpoint="http://localhost:4747" />;
}
```

Для Vite используйте import.meta.env.DEV вместо process.env.NODE_ENV. Проверьте
dev-страницу и production build отдельно. Не размещайте MCP/панель на публичном
сервере. Для SSR без React выбирайте подходящую отдельную dev-интеграцию после
проверки стека, не вставляйте JSX в чужой шаблон.

В браузере создайте тестовую аннотацию. В агенте прочитайте её через MCP, проверьте
текст и селектор. Обрабатывайте только сессию выбранного проекта. Постоянное
наблюдение запускается отдельным запросом и не возникает само от установки MCP.

## MTGA и Remotion — по желанию

MTGA в Claude Code — плагин:

```
/plugin marketplace add howdeploy/MTGA
/plugin install mtga@mtga
/mtga:on
```

Выключение: `/mtga:off` до удаления плагина. В Codex:

```bash
git clone https://github.com/howdeploy/MTGA.git "$STACK_TOOLS/MTGA"
bash "$STACK_TOOLS/MTGA/scripts/mtga-codex.sh" on ru
bash "$STACK_TOOLS/MTGA/scripts/mtga-codex.sh" status
```

Выключение: тот же скрипт с `off`. Стиль относится к чату; код и документы обычные.

Remotion: [официальный quickstart](https://www.remotion.dev/docs/). Устанавливайте
в отдельный выбранный видеопроект, не глобально во все репозитории. Проверка —
рендер короткой композиции. В этой сборке Remotion не включён в обязательный smoke-test.

## Обновление и восстановление

Сначала backup и фиксация версий, затем один компонент, затем его проверка.
Не обновляйте весь стек одновременно с продуктовой задачей. При сбое сравните
изменения с backup и отмените только изменения этого обновления. Не восстанавливайте
весь старый config поверх появившихся пользовательских настроек.

Следующий шаг: [что делать после установки](AFTER-INSTALL.md) — входы, проверка
hooks и проектная настройка Agentation. Полная проверка: [VERIFY.md](VERIFY.md).
