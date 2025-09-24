## Как поднять для разработки
1. Разархивируйте media из архива в корневую папку проекта
2. Создайте базу данных PostgreSQL или SQLite
3. Настройте .env чтобы подключиться к вашей БД, а также другие настройки
4. Выполните миграции
```bash
python manage.py migrate
```
5. Загрузите данные через loaddata
```bash
python manage.py loaddata dumpdata.json
```
6. Установите `uv`
```bash
pip install uv
```
7. Установите зависимости
```bash
uv sync
```
8. Активируйте venv
```bash
.venv/Scripts/activate
# На linux
source .venv/Scripts/activate
```
Готово!

Ps: в будущем создам команду initdata которая загрузит все .json данные из папки fixtures/initdata и там будут отдельные файлы под каждую модель (точнее, только необходимые для поднятия).
