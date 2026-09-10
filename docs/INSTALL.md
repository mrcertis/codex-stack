# Полная установка

Команды ниже — для macOS/Linux или WSL. Выполняйте разделы по очереди, а не одним
блоком. Требуются авторизованный Codex, Git, Node.js LTS, Python 3.11+, uv и Bun.
Устанавливайте системные prerequisites по документации их поставщиков.
Версии upstream меняются: сверяйте --help и сохраняйте версии в локальном отчёте.

## Пути и резервная копия

Выберите общий каталог инструментов и общий Obsidian vault. Пример:

```bash
STACK_TOOLS="$HOME/Documents/Codex/Tools"
STACK_VAULT="$HOME/Documents/Codex/Knowledge"
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
```

Все дальнейшие shell-примеры предполагают эти переменные в том же терминале.
Backup приватный, вне checkout. При повторном запуске не клонируйте поверх
существующих каталогов: сначала проверьте remote и локальные изменения.

## Глобальные правила

Откройте [global-config/AGENTS.md](../global-config/AGENTS.md). В копии для вашего
компьютера замените `<TOOLS_ROOT>` на абсолютный STACK_TOOLS, а `<WIKI_ROOT>` —
на абсолютный STACK_VAULT/LLM Wiki. Это текстовые подстановки, shell сам их не делает.

Если глобального AGENTS.md нет, сохраните настроенную копию туда. Если есть —
объедините разделы, сохраняя личные правила; не используйте слепое перенаправление
поверх файла. При нестандартном CODEX_HOME замените и упоминания ~/.codex.

[PROJECTS.example.md](../global-config/PROJECTS.example.md) — образец для нового
приватного реестра. Существующий PROJECTS.md не заменяйте. [Правила Codex](https://developers.openai.com/codex/guides/agents-md/).

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

## Impeccable

Источник: [pbakaus/impeccable](https://github.com/pbakaus/impeccable), [доки](https://impeccable.style/docs/).

```bash
npx impeccable install
```

Выберите **Codex** и **глобальную установку** для личного стека. Для командного
репозитория можно выбрать локальную установку отдельно. Установщик размещает
payload для выбранной среды; проверьте фактический путь SKILL.md, а не только
сообщение об успехе. Codex обнаруживает пользовательские skills в ~/.agents/skills,
проектные — в .agents/skills; старые установки могут использовать ~/.codex/skills.
Не создавайте второй экземпляр с тем же именем.

Если выбраны hooks, проверьте сохранность существующего manifest. Откройте
управление hooks в Codex и подтвердите доверие через предусмотренный интерфейс;
если версия среды их не поддерживает, используйте skill без hook и явно отметьте это.
После установки откройте новую задачу, убедитесь, что `$impeccable` доступен.
`init` создаёт контекст продукта в конкретном проекте — не запускайте его во всех
репозиториях при глобальной установке. Обновление: `npx impeccable update`.

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

## gstack

Источник: [garrytan/gstack](https://github.com/garrytan/gstack). Требуется Bun.

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git "$STACK_TOOLS/gstack"
cd "$STACK_TOOLS/gstack"
./setup --host codex
```

Прочитайте setup перед запуском. Он создаёт Codex-версию skills; не копируйте
Claude-набор вручную. Проверьте `$browse` и `$review` в новом сеансе. Браузерный
путь выбирается по текущему SKILL.md: Aside при наличии либо bundled Chromium.
Для Chromium нужны загрузка браузера и разрешения ОС. Само обнаружение skill
не доказывает, что браузер открывается.

## GSD Core

Источник: [open-gsd/gsd-core](https://github.com/open-gsd/gsd-core).

```bash
npx @opengsd/gsd-core@latest --codex --global
```

Сохраните существующую конфигурацию и проверьте diff после установки.
Runtime обычно находится в ~/.codex/gsd-core, агентские определения — в
~/.codex/agents; точные пути смотрите в отчёте установщика. Проверьте `$gsd-help`.
Полный процесс разработки проверяется на отдельной задаче: обнаружение агентов
не доказывает поддержку всех режимов делегирования вашим рантаймом.

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

Подставьте существующий public-input.md. Читайте --help установленной версии при
расхождении флагов. Компиляция вызывает LLM backend: используйте разрешённые данные.
Не перезаписывайте существующий space; дальнейшие обновления проходят через
штатный writer. Google Drive и NotebookLM — опциональны и требуют личного входа.
Отсутствие их авторизации не равно неработающей локальной Wiki.

Wiki-hooks опциональны. Сначала используйте явные ссылки из AGENTS.md. Если нужны
якоря на старте/после сжатия контекста, ориентируйтесь на
[хуки KISA](https://github.com/howdeploy/kisa-stack/tree/main/global-config/hooks),
но адаптируйте к поддерживаемым событиям Codex и проверьте реальное срабатывание.
Не переносите Claude-конфигурацию как есть и не объявляйте hook рабочим до проверки trust.

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

## MTGA и Remotion — по желанию

MTGA:

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

Последний шаг: [VERIFY.md](VERIFY.md) и новая задача Codex.
