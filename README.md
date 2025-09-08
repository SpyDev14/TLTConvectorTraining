Ps: Информация о проекте будет здесь позже

## Как поднять
1. Разархивируйте media и data.dump из архива compressed_data.zip в конрневую папку проекта
2. Создайте базу данных PostgreSQL
3. Настройте .env чтобы подключиться к вашей БД
4. Восстановите данные, миграции проводить **НЕ НУЖНО**
```bash
pg_restore -h localhost -p 5432 -U tlt_convector_user -d tlt_convector_db data.dump
```
- Если по каким-либо причинам это не сработало, используйте
```bash
psql -h localhost -p 5432 -U tlt_convector_user -d tlt_convector_db -f alt_data.sql
```
- Если оно всё ещё не работает, то к сожалению, ничем помочь вам не могу
