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
python manage.py loaddata fixtures/initdata/*.json
```
6. Если вы разработчик, можете загрузить тестовые данные
```bash
python manage.py loaddata fixtures/initdata/dev/*.json
```
7. Установите `uv`
```bash
pip install uv
```
8. Установите зависимости
```bash
uv sync
```
9. Активируйте venv
```bash
.venv/Scripts/activate
# На linux
source .venv/Scripts/activate
```
Готово!
