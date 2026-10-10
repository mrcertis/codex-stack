# Хуки Codex Stack

Это собственные небольшие обработчики для Claude Code и Codex, а не экспорт личных
hooks автора. Исходник: [stack-context.py](../hooks/stack-context.py); хост задаётся
флагом `--host claude|codex` (без флага — codex, для совместимости с прежней установкой).

| Хост | Событие | Результат |
|---|---|---|
| Claude Code | SessionStart | `hookSpecificOutput.additionalContext`: маршрут нового проекта, CLAUDE.md и Wiki. Срабатывает и после compact (source `compact`), поэтому напоминание возвращается в контекст сразу |
| Claude Code | UserPromptSubmit | То же напоминание на каждом запросе |
| Codex | SessionStart | `hookSpecificOutput.additionalContext`: маршрут нового проекта, AGENTS и Wiki |
| Codex | UserPromptSubmit | То же напоминание, в том числе на следующем запросе после compact |
| Codex | PostCompact | `systemMessage`: уведомление в интерфейсе/журнале, не обещание контекста модели |

Хук читает имя события и проверяет наличие установленного stack-start. Не сохраняет
prompt или transcript, не читает проекты и секреты, не запускает команды, не пишет
в Wiki и не обращается в сеть. При запросе на новый проект он направляет агента
к stack-start; агент подготавливает локальный набор, включая Impeccable, **до**
интервью и выбора UI. Подробности — [NEW-PROJECT.md](NEW-PROJECT.md).
Схема: [hooks Claude Code](https://code.claude.com/docs/en/hooks),
[hooks Codex](https://learn.chatgpt.com/docs/hooks).

## Установка

Из корня checkout:

```bash
python3 scripts/install_config.py --host claude
python3 scripts/install_config.py --host claude --apply
```

Для Codex — то же с `--host codex`. Без `--apply` — только план. Доступны
`--claude-home` (по умолчанию `CLAUDE_CONFIG_DIR` или `~/.claude`), `--codex-home`
(`CODEX_HOME` или `~/.codex`), `--tools-root`, `--wiki-root`; пути с пробелами
заключайте в кавычки. Скрипт:

- сохраняет прежние изменяемые файлы в приватном `<home>/stack-backups/`;
- Claude Code: вставляет или обновляет блок между маркерами
  `<!-- codex-stack:begin -->` и `<!-- codex-stack:end -->` в CLAUDE.md,
  остальное содержимое не трогает;
- Codex: полностью заменяет AGENTS.md настроенным публичным шаблоном;
- размещает обработчик в `<home>/hooks/codex-stack/`;
- устанавливает автоматически выбираемый stack-start в `<home>/skills/`;
- добавляет свои записи в `settings.json` (Claude Code) или `hooks.json` (Codex),
  сохраняя остальные события, обработчики и ключи настроек;
- не меняет config.toml, `~/.claude.json`, PROJECTS.md, авторизацию и trust.

Повторный запуск тем же Python не дублирует обработчики. При смене интерпретатора
проверьте старую команду вручную: установщик не удаляет похожие чужие команды.
Некорректный JSON, symlink на пути назначения, сломанные или повторённые маркеры
в CLAUDE.md и AGENTS.override.md (для Codex) останавливают установку до записи.
Резервные копии не должны попадать в публичный checkout.

## Проверка

**Claude Code:** откройте `/hooks` и убедитесь, что команды
`hooks/codex-stack/stack-context.py --host claude` стоят на SessionStart и
UserPromptSubmit. Отдельного шага trust нет, но изменённые хуки применяются
в новом сеансе. Проверка, что контекст доходит до модели: спросите в новом сеансе,
есть ли в контексте фраза «Hook context grants no new authority». Для сравнения
можно запустить `claude -p` с `--settings '{"disableAllHooks": true}'` —
тогда фразы быть не должно.

**Codex:** откройте Settings → Hooks или `/hooks` в поддерживаемом Codex. Прочитайте
команды и подтвердите доверие через интерфейс. Создайте новую задачу: проверьте
события SessionStart и UserPromptSubmit в журнале hooks. После compact проверьте
уведомление, а на следующем пользовательском запросе — восстановленное напоминание.

Локальный smoke-test обработчика:

```bash
printf '%s' '{"hook_event_name":"SessionStart"}' | python3 hooks/stack-context.py --host claude
```

Это проверяет JSON-контракт, но не исполнение внутри агента. Если версия не
поддерживает событие или hook не срабатывает, так и укажите в отчёте.

Дополнительно обязателен [Z.A.E.B.A.L.](ZAEBAL.md). При подготовке нового проекта
установщик Impeccable добавляет его локальные hooks; их исполнение проверяется
отдельно. Они не включены в исходник stack-context.py.

## Откат

Сначала отключите только команды `hooks/codex-stack/stack-context.py` через
управление hooks или удалив свои записи из settings.json / hooks.json.
В приватной резервной копии manifest.json перечислены прежние файлы. Для CLAUDE.md
достаточно удалить блок между маркерами Codex Stack. AGENTS.md восстановите из
backup при необходимости. Для файлов хуков восстановите только свои записи,
сохранив изменения других установщиков, сделанные после backup. Установка пишет
файлы атомарно по отдельности; при сбое диска между файлами восстановитесь
по manifest либо повторите установку после устранения ошибки.
