# Полная установка

Команды ниже — для macOS/Linux или WSL. Выполняйте разделы по очереди, а не одним
блоком. Требуются авторизованный Codex, Git, Node.js LTS, Python 3.11+, uv и Bun.
Claude Code — по желанию: основной хост стека Codex, Claude Code читает те же правила.
Устанавливайте системные prerequisites по документации их поставщиков.
Версии upstream меняются: сверяйте --help и сохраняйте версии в локальном отчёте.

Уже стоит старая версия стека (с gstack)? Начните с [обновления](UPGRADE.md).

## Пути и резервная копия

Выберите общий каталог инструментов и общий Obsidian vault **вне iCloud**.
На macOS iCloud Drive по умолчанию синхронизирует `~/Documents` и `~/Desktop`:
он создаёт конфликтные копии файлов «… 2.md», ломающие Wiki, и выгружает редко
открываемые файлы в облако, после чего скрипты их не находят. Стек по умолчанию
использует `~/tools` и `~/Knowledge`:

```bash
STACK_TOOLS="$HOME/tools"
STACK_VAULT="$HOME/Knowledge"
STACK_CODEX="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$STACK_TOOLS" "$STACK_VAULT" "$STACK_CODEX"
STACK_BACKUP="$STACK_TOOLS/stack-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$STACK_BACKUP"
chmod 700 "$STACK_BACKUP"
for stack_file in AGENTS.md config.toml hooks.json RTK.md PROJECTS.md; do
  if [ -f "$STACK_CODEX/$stack_file" ]; then
    cp -p "$STACK_CODEX/$stack_file" "$STACK_BACKUP/"
  fi
done
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
  cp -p "$HOME/.claude/CLAUDE.md" "$STACK_BACKUP/CLAUDE.md"
fi
```

Все дальнейшие shell-примеры предполагают эти переменные в том же терминале.
Backup приватный, вне checkout. При повторном запуске не клонируйте поверх
существующих каталогов: сначала проверьте remote и локальные изменения.
Если Wiki не нужна на других устройствах, вместо облачной копии заведите в vault
локальный git: `git -C "$STACK_VAULT" init`.

## Глобальные правила

Из корня этого checkout выполните dry run, затем применение:

```bash
python3 scripts/install_config.py --codex-home "$STACK_CODEX" --tools-root "$STACK_TOOLS" --wiki-root "$STACK_VAULT/LLM Wiki"
python3 scripts/install_config.py --codex-home "$STACK_CODEX" --tools-root "$STACK_TOOLS" --wiki-root "$STACK_VAULT/LLM Wiki" --apply
```

Если используете и Claude Code, добавьте к обеим командам `--claude-home "$HOME/.claude"`.

Старый глобальный AGENTS.md полностью заменяется [шаблоном](../global-config/AGENTS.md),
а не объединяется с ним. Блок стиля MTGA (между `<!-- MTGA:BEGIN -->` и
`<!-- MTGA:END -->`) установщик переносит в новый файл. Скрипт подставляет пути,
сохраняет приватную резервную копию, ставит skill stack-start и добавляет свои
хуки с сохранением чужих. config.toml и PROJECTS.md не изменяются.
AGENTS.override.md требует отдельного рассмотрения, поскольку затеняет AGENTS.md.
[Состав хуков, доверие и откат](HOOKS.md).

С `--claude-home` скрипт дописывает в `~/.claude/CLAUDE.md` одну строку
`@~/.codex/AGENTS.md` (если её ещё нет; остальное содержимое файла сохраняется)
и копирует stack-start в `~/.claude/skills/`. Так Claude Code читает те же правила;
соответствия команд описаны в конце шаблона. [Импорт в CLAUDE.md](https://code.claude.com/docs/en/memory).

[PROJECTS.example.md](../global-config/PROJECTS.example.md) — образец для нового
приватного реестра. Существующий PROJECTS.md не заменяйте. [Правила Codex](https://developers.openai.com/codex/guides/agents-md/).

## GSD Core

Источник: [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core),
[установка по средам](https://github.com/open-gsd/gsd-core/blob/main/docs/how-to/install-on-your-runtime.md).
GSD — единый процесс разработки стека: интервью, требования, дорожная карта, фазы,
ревью и приёмка.

```bash
npx @opengsd/gsd-core@latest --codex --global
```

Для Claude Code — тот же установщик с `--claude --global`. После обновления GSD
в одной среде обновите и другую. Перезапустите Codex. Skills появляются в
`~/.codex/skills/gsd-*`, агенты — в `~/.codex/agents/gsd-*.toml`, runtime — в
`~/.codex/gsd-core` (для Claude Code — `~/.claude/gsd-core`); точные пути смотрите
в отчёте установщика. Проверьте `$gsd-help` (Claude Code: `/gsd-help`).
Удаление — тот же установщик с `--uninstall`.

**Настройка скорости.** Планы до 5 задач выполняются в самой сессии, без отдельного
агента-исполнителя. Для новых проектов создайте или дополните `~/.gsd/defaults.json`
(сохраните прежние ключи, если файл уже есть):

```json
{
  "workflow": {
    "inline_plan_threshold": 5
  }
}
```

GSD читает этот файл только при `gsd-new-project`. В уже существующем проекте
GSD выполните из его корня:

```bash
node ~/.codex/gsd-core/bin/gsd-tools.cjs config-set workflow.inline_plan_threshold 5
```

Остальные правила скорости (тяжёлые проверки в конце плана, матрица экранов
в конце фазы, без повторной проверки после точечной правки плана) настройками GSD
не управляются: они записаны в [шаблоне AGENTS.md](../global-config/AGENTS.md#разработка-через-gsd).

Как начинать работу: [шпаргалка](USAGE.md).

## Ponytail

Источник: [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail).
Ставьте только из этого репозитория или npm-пакета `@dietrichgebert/ponytail`.
Ponytail — плагин, который работает **через хуки**: на SessionStart и UserPromptSubmit
он подаёт агенту правило «минимум нового кода после чтения существующего», на
SubagentStart — то же правило субагентам. Хуки запускаются Node.js и требуют
доверия. Перед установкой проверьте исходники и текущий тег.

Codex:

```bash
codex plugin marketplace add DietrichGebert/ponytail --ref v5.2.0
codex plugin add ponytail@ponytail
codex plugin list
```

Claude Code (две отдельные команды в чате):

```text
/plugin marketplace add DietrichGebert/ponytail
/plugin install ponytail@ponytail
```

Держите одну версию в обеих средах (проверено на 5.2.0). В Codex откройте `/hooks`,
просмотрите команды Ponytail и подтвердите доверие, затем перезапустите Codex
и откройте новую задачу. По умолчанию режим `full`; смена режима —
`/ponytail lite|full|ultra|off`. `ponytail-review` и `ponytail-audit` запускаются
только по просьбе. Не переносите его правила целиком в AGENTS.md: явный запрос,
безопасность и нужные проверки остаются приоритетными. Если плагин мешает,
откатите только его: `codex plugin remove ponytail`.

## MTGA

Источник: [howdeploy/MTGA](https://github.com/howdeploy/MTGA). Стиль ответов в чате;
в этом стеке **включён по умолчанию** (русский). Код, файлы, документы и коммиты
остаются обычными, а сводки в точках подтверждения GSD агент пишет обычным языком.

Codex:

```bash
git clone https://github.com/howdeploy/MTGA.git "$STACK_TOOLS/MTGA"
bash "$STACK_TOOLS/MTGA/scripts/mtga-codex.sh" on ru
bash "$STACK_TOOLS/MTGA/scripts/mtga-codex.sh" status
```

Скрипт вставляет блок стиля в `~/.codex/AGENTS.md` и ставит skill `$mtga`.
Запускайте его **после** установки глобальных правил; при повторной установке
правил блок сохраняется. Выключение: `$mtga off` в Codex или тот же скрипт с `off`.

Claude Code:

```text
/plugin marketplace add howdeploy/MTGA
/plugin install mtga@mtga
/mtga:on
```

Стиль включается после `/clear` или в новой сессии. Выключение — `/mtga:off`.

## Context7

Источник: [upstash/context7](https://github.com/upstash/context7).

Сначала проверьте, нет ли уже рабочей записи `context7`. Выберите **один** вариант.

**OAuth:** добавьте hosted MCP и выполните вход:

```bash
codex mcp add context7 --url https://mcp.context7.com/mcp
codex mcp login context7
```

Браузерный вход делает владелец. Если конкретный клиент не поддерживает этот
способ, используйте API key. Проверяйте синтаксис через `codex mcp --help`.

**API key:** создайте собственный ключ в Context7 и передайте его процессу Codex
через переменную `CONTEXT7_API_KEY`. Добавьте фрагмент в config.toml:

```toml
[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
bearer_token_env_var = "CONTEXT7_API_KEY"
```

Не вставляйте реальный ключ в публичный TOML, команду, issue или чат. Переменная
терминала может быть недоступна desktop-приложению; перезапустите его с нужным
окружением либо используйте OAuth. Не включайте одновременно две записи сервера.
Поля конфигурации: [официальная документация MCP](https://developers.openai.com/codex/mcp/).

Альтернатива — официальный мастер `npx ctx7 setup`: выберите Codex и MCP;
проверьте его изменения. Он может также установить skill и правило использования.
Не запускайте мастер поверх уже рабочего подключения ради дублирующей записи.

Проверка в новом сеансе: попросите найти Context7 ID React и вернуть документацию
по cleanup в useEffect. Должны выполниться resolve-library-id и query-docs.

## Дизайн: Refero (рекомендуется) и Impeccable

### Refero — по желанию

Источник: [referodesign/refero_skill](https://github.com/referodesign/refero_skill),
[документация](https://refero.design/mcp). Refero — база реальных экранов, сценариев
и стилей приложений и сайтов: агент находит образцы, показывает их вам и выбирает
направление дизайна вместе с вами. **Рекомендуется, но не обязателен.** Живой поиск
требует платного тарифа Refero; без него работайте через Impeccable — он закрывает
весь дизайн-процесс сам.

Плагин включает MCP и skill refero-design. Codex:

```bash
codex plugin marketplace add referodesign/refero_skill
codex plugin add refero@refero
```

Claude Code:

```text
/plugin marketplace add referodesign/refero_skill
/plugin install refero@refero
```

Перезапустите приложение. При первом подключении Refero откроет браузер для входа
в ваш аккаунт; ключи в конфиг не пишутся. Если MCP `https://api.refero.design/mcp`
уже подключён вручную, достаточно skill:
`npx skills add https://github.com/referodesign/refero_skill --skill refero-design`.
Не держите две записи одного сервера.

### Impeccable

Источник: [pbakaus/impeccable](https://github.com/pbakaus/impeccable), [доки](https://impeccable.style/docs/).

```bash
npx impeccable install
```

Impeccable входит в локальный набор **каждого нового проекта**, до интервью
и выбора UI. Это автоматически делает stack-start перед `gsd-new-project`.
Для ручной установки запускайте команду **из папки проекта**, выберите
**Codex** (или Claude Code) и **local/project**: ожидаемый путь —
`.agents/skills/impeccable/SKILL.md` (Claude Code: `.claude/skills/impeccable/`).
Глобально Impeccable в этом стеке не устанавливается. Если глобальная копия уже
существует, проверьте конфликт обнаружения и согласуйте её отключение отдельно.

В проекте вызовите `$impeccable hooks on`, затем `$impeccable hooks status`.
Проверьте `.codex/hooks.json`: локальные PostToolUse и Stop, сохранность чужих
обработчиков. Подтвердите доверие через Settings → Hooks или `/hooks`.
Установленное без trust не считается исполняемым.
[Документация hooks](https://impeccable.style/docs/hooks/).
`init` создаёт PRODUCT.md; DESIGN.md фиксируется по завершении реализации
согласно playbook. Обновление из того же проекта: `npx impeccable update`.

## Emil Design Engineering

Источник: [emilkowalski/skills](https://github.com/emilkowalski/skills).

```bash
npx skills@latest add emilkowalski/skills
```

В установщике выберите **emil-design-eng**, **Codex**, **global**. Дополнительный
`review-animations` выбирайте при необходимости. Не ставьте все skills автоматически:
в разных наборах могут совпадать имена, например animate.
Проверьте, что есть SKILL.md и агент видит `$emil-design-eng`.
Вариант для установки агентом — `$skill-installer` с URL:
https://github.com/emilkowalski/skills/tree/main/skills/emil-design-eng

## Z.A.E.B.A.L.

Установите [обязательный Z.A.E.B.A.L.](ZAEBAL.md). Один skill без UserPromptSubmit
hook не завершает его настройку. Стековые хуки уже поставлены шагом глобальных
правил; доверие и реальный запуск проверяются отдельно.

Интервью перед работой ведёт GSD. Для задач мимо GSD можно дополнительно поставить
[grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs);
стек его не требует.

## RTK

Источник: [rtk-ai/rtk](https://github.com/rtk-ai/rtk).

macOS с Homebrew:

```bash
brew install rtk
rtk --version
rtk init -g --codex
```

На Linux используйте официальный способ из README RTK для вашей ОС.
Проверьте diff AGENTS.md после init, сохраните прежние правила. Явное чтение
RTK.md и правило в AGENTS.md надёжнее предположения, что `@...` разворачивается.
Проверка в Git-репозитории: `rtk git status`, затем `rtk gain`.

## Graphify

Источник: [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)
(ранее safishamsi/graphify).

```bash
uv tool install graphifyy
graphify --help
graphify install --platform codex
```

Для Claude Code — `graphify install --platform claude`. Если graphifyy уже
установлен, не обновляйте без причины. Проверяйте созданный skill и выполняйте
первый анализ на маленьком тестовом проекте по текущему SKILL.md. Граф строится
отдельно для проекта. Не индексируйте весь home. Платные semantic backends
не включаются одной установкой CLI.

## ObsidianDataWeave и общая Wiki

Источник: [howdeploy/ObsidianDataWeave](https://github.com/howdeploy/ObsidianDataWeave).

```bash
git clone https://github.com/howdeploy/ObsidianDataWeave.git "$STACK_TOOLS/ObsidianDataWeave"
cd "$STACK_TOOLS/ObsidianDataWeave"
python3 -m venv .venv
```

Прочитайте AGENTS.md и install.sh. Затем:

```bash
PATH="$PWD/.venv/bin:$PATH" bash install.sh --mode codex --vault-path "$STACK_VAULT"
.venv/bin/python scripts/doctor.py
```

Создание Wiki — отдельная явная часть настройки знания. Если пользователь её
разрешил, создайте space и проверьте на публичном небольшом входном документе:

```bash
.venv/bin/python scripts/wiki_init.py codex --mode project --title "Codex Stack" --lang ru
.venv/bin/python scripts/wiki_ingest.py codex /absolute/path/to/public-input.md --kind docs
.venv/bin/python scripts/wiki_compile.py codex --backend codex
.venv/bin/python scripts/wiki_lint.py codex --strict
```

Подставьте существующий public-input.md. Из Claude Code компилируйте с
`--backend claude`: компилятор вызывает CLI этой среды, и он должен быть
авторизован. Читайте --help установленной версии при расхождении флагов.
Компиляция вызывает LLM backend: используйте разрешённые данные.
Не перезаписывайте существующий space; дальнейшие обновления проходят через
штатный writer. Google Drive и NotebookLM — опциональны и требуют личного входа.
Отсутствие их авторизации не равно неработающей локальной Wiki.

Напоминание о Wiki входит в [поставляемые хуки Codex](HOOKS.md). SessionStart и
UserPromptSubmit передают контекст агенту; PostCompact показывает уведомление,
но не обещает вставку текста в контекст модели. Сами хуки не пишут в Wiki.

## researcher

Попросите встроенный `$skill-installer` установить:
https://github.com/howdeploy/kisa-stack/tree/main/skills/researcher

В новый сеанс должен попасть `$researcher`. Пусть агент проверит доступные
web-инструменты; наличие Tavily не предполагается. Первый smoke-test — краткий
ответ по публичному источнику со ссылкой, а не генерация без поиска.

## Agentation

Источник: [benjitaylor/agentation](https://github.com/benjitaylor/agentation).
Глобальное подключение MCP:

```bash
codex mcp add agentation -- npx -y agentation-mcp@1.2.0 server
```

Версия 1.2.0 — проверенная исходная версия этой сборки, не утверждение о latest.
Если desktop не видит Node/npx, укажите абсолютные пути. Для медленного первого
запуска установите startup_timeout_sec = 30, как в образце TOML.
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

В браузере создайте тестовую аннотацию. В Codex прочитайте её через MCP, проверьте
текст и селектор. Обрабатывайте только сессию выбранного проекта. Постоянное
наблюдение запускается отдельным запросом и не возникает само от установки MCP.

## Remotion — по желанию

[Официальный quickstart](https://www.remotion.dev/docs/). Устанавливайте
в отдельный выбранный видеопроект, не глобально во все репозитории. Проверка —
рендер короткой композиции. В этой сборке Remotion не включён в обязательный smoke-test.

## gstack больше не используется

gstack выведен из стека: процесс, ревью и приёмку ведёт GSD. gstack занимал
много места на диске и добавлял в AGENTS.md и CLAUDE.md свои объёмные разделы.
Не устанавливайте его. Если он уже стоит — удалите по [UPGRADE.md](UPGRADE.md).

## Обновление и восстановление

Сначала backup и фиксация версий, затем один компонент, затем его проверка.
Не обновляйте весь стек одновременно с продуктовой задачей. При сбое сравните
изменения с backup и отмените только изменения этого обновления. Не восстанавливайте
весь старый config поверх появившихся пользовательских настроек.

Следующий шаг: [что делать после установки](AFTER-INSTALL.md) — входы, доверие
к hooks и проектная настройка Agentation. Полная проверка: [VERIFY.md](VERIFY.md).
