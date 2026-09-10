# Codex Stack — mrcertis

Мой набор инструментов для работы с AI-агентами: от постановки задачи до кода, дизайна, проверки и проектной Wiki. Основа — [KISA Stack](https://github.com/howdeploy/kisa-stack), адаптированная под **Codex** и дополненная **Impeccable, Emil Design Engineering и Context7**.

Это открытая сборка инструкций и шаблонов. Она помогает воспроизвести подход, не копируя чужие ключи, личные проекты и настройки компьютера. Старый глобальный AGENTS.md сохраняется в приватной резервной копии и полностью заменяется шаблоном стека. Остальная конфигурация сохраняется.

## Быстрый старт

1. Установите и авторизуйте Codex. Нужны Git, Node.js LTS; для полного набора также Python 3.11+, uv и Bun.
2. Склонируйте этот репозиторий и откройте его в Codex:

   ```bash
   git clone https://github.com/mrcertis/codex-stack.git
   cd codex-stack
   ```

3. Передайте агенту этот запрос:

   > Настрой мне Codex Stack по docs/AGENT-SETUP.md. Проверь существующие установки. Сделай приватную резервную копию старого глобального AGENTS.md и полностью замени его шаблоном стека; не объединяй старые инструкции с новыми. Сохрани config.toml, чужие hooks и PROJECTS.md. Установи основной набор, включая grill-with-docs с зависимостями, Context7, emil-design-eng и обязательный Z.A.E.B.A.L. Подключи поставляемые хуки Codex. Impeccable устанавливай только локально после выбора UI-проекта. Согласуй недостающие пути, входы и требуемые разрешения. Проверь реальные вызовы и покажи остаточные действия.

4. Откройте новую задачу Codex и выполните [проверки](docs/VERIFY.md).

**Вручную:** [полная установка](docs/INSTALL.md). **Для агента:** [порядок настройки](docs/AGENT-SETUP.md). **На каждый день:** [короткая шпаргалка](docs/USAGE.md).

## Что входит

| Слой | Инструменты | Для чего |
|---|---|---|
| Правила | [AGENTS.md](global-config/AGENTS.md), [PROJECTS.example.md](global-config/PROJECTS.example.md) | Границы работы, проверяемый результат, проекты read-only по умолчанию |
| Документация | [Context7](https://github.com/upstash/context7) | Актуальные API и примеры под нужную версию библиотеки |
| Разработка | [GSD Core](https://github.com/open-gsd/gsd-core), [gstack](https://github.com/garrytan/gstack) | Этапы, планирование, ревью и браузерный QA |
| Старт проекта | [grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs) | Интервью → требования и модель предметной области |
| Самопроверка | [Z.A.E.B.A.L.](https://github.com/howdeploy/Z.A.E.B.A.L) | Обязательный skill и hook реакции на недовольство |
| Контекст | [Хуки Codex](docs/HOOKS.md) | Маршрут работы и напоминание о Wiki |
| Дизайн | [Impeccable](https://github.com/pbakaus/impeccable), [Emil](https://github.com/emilkowalski/skills) | Цельный интерфейс, компоненты, анимации и детали взаимодействия |
| Обратная связь | [Agentation](https://github.com/benjitaylor/agentation) | Замечания прямо на элементах страницы → агент |
| Код и вывод | [Graphify](https://github.com/Graphify-Labs/graphify), [RTK](https://github.com/rtk-ai/rtk) | Связи в коде и компактный вывод команд |
| Знания | [ObsidianDataWeave](https://github.com/howdeploy/ObsidianDataWeave), [researcher](https://github.com/howdeploy/kisa-stack/tree/main/skills/researcher) | Общая LLM Wiki, источники и исследование |
| По задаче | [MTGA](https://github.com/howdeploy/MTGA), [Remotion](https://github.com/remotion-dev/remotion) | Стиль ответов и видео на React |

Подробнее: [каталог со ссылками и назначением](plugins.md).

## Как это работает

Новый проект начинается с `$grill-with-docs`: идея → интервью → требования → дизайн, если есть UI → документы и код → проверка. [Пошаговый старт и готовый запрос](docs/NEW-PROJECT.md). Impeccable устанавливается в выбранный репозиторий, Emil помогает с взаимодействием, Context7 проверяет API, браузер и Agentation помогают оценить результат. Небольшая правка существующего проекта не требует повторного интервью и полного GSD-процесса.

Wiki одна для общего знания, внутри отдельные spaces. Реестр проектов приватный. Просьба «проверь проект» разрешает чтение, но не изменения. Запись в Wiki — по явному запросу.

## Совместимость и ограничения

- Основной сценарий: локальный Codex на macOS/Linux. На Windows команды shell выполняются в WSL; нативные пути и менеджеры пакетов требуют адаптации.
- Многие upstream-инструменты поддерживают Claude Code и другие среды. Их конфигурации не взаимозаменяемы; эта инструкция настраивает Codex.
- MCP, skill, CLI и плагин — разные сущности. Наличие skill не означает, что MCP подключён.
- Это не обещание установки всего стека за пять минут. Авторизация, браузеры, hooks trust и проектные интеграции проверяются отдельно.
- Инструкции сверены 10 сентября 2026. Upstream меняется; после обновления повторяйте проверки. См. [статус проверки](docs/VERIFY.md).

## Происхождение

Спасибо [howdeploy / KISA](https://github.com/howdeploy/kisa-stack) за исходную методологию, RTK/Wiki-подход и подборку инструментов. Здесь сохранено указание авторства и добавлены собственная структура, инструкции для Codex и дизайн-набор. [Лицензия](LICENSE) относится к материалам этого репозитория; внешние продукты имеют собственные лицензии. Подробности — [NOTICE.md](NOTICE.md).
