# Публикация и защита ЛР11–12

## ЛР11

1. Создайте на GitHub новый репозиторий `game-user-analytics-research`. Удобнее создать его **пустым** (без автоматического README), так как файлы уже подготовлены локально. Для учебного проекта возможен публичный репозиторий, только если всё содержимое разрешено публиковать.
2. В терминале VS Code, открытом в корне проекта, выполните (подставьте **свой логин**):

```powershell
git init
git branch -M main
git add .
git commit -m "chore: initial reproducible analytics project"
git remote add origin https://github.com/ВАШ_ЛОГИН/game-user-analytics-research.git
git push -u origin main
```

3. Проверьте на странице GitHub наличие README, LICENSE, .gitignore, `data/raw/user_sessions.csv`, `app.py`. Скопируйте настоящую ссылку на репозиторий в ответ по ЛР11.

## ЛР12

1. Создайте шесть Issues по `docs/ISSUES_PLAN.md`; назначьте метки.
2. Создайте Project со статусами To Do, In Progress, Review, Done, привяжите Issues.
3. Создайте ветку от main, например:

```powershell
git switch -c feature/documentation
```

4. Внесите небольшое реальное изменение в README (например, дополните раздел ограничений), сделайте коммит и push:

```powershell
git add README.md
git commit -m "docs: clarify research limitations"
git push -u origin feature/documentation
```

5. Через GitHub создайте Pull Request в main, укажите `Closes #N` с номером настоящего Issue. Если есть второй участник, попросите у него независимое code review с конкретными замечаниями. Если работаете один, не называйте собственный комментарий независимым ревью; можно продемонстрировать учебный PR и пояснить ограничение.
6. После проверки объедините PR. Создайте GitHub Wiki: *Введение*, *Методология*, *Результаты*, *Выводы*, *Список литературы*; черновики в `docs/wiki_drafts/`.
7. Создайте Discussion о выборе интерпретации DAU или дизайна фильтра (если репозиторий допускает Discussions).
8. Заполните `reports/final_report.md` реальными ссылками, статусом задач, коммитами и результатами проверки, приложите скриншоты и ссылку на Project и основной PR. При необходимости оформите презентацию со скриншотами.

Автоматизация CI/CD и интеграции с внешними инструментами по методичке **опциональны**; для начала достаточно базового цикла Issue → ветка → коммит → PR → ревью → merge.
