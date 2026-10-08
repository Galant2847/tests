# Автотесты API Музея Метрополитен

Тесты для [Met Museum Collection API](https://metmuseum.github.io)
на Python, Pytest и Pydantic.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Логи пишутся в консоль и в файл `logs/api_tests.log`

## Структура

| Файл | Что внутри |
|---|---|
| `models.py` | модели Pydantic |
| `client.py` | HTTP-клиент и логирование |
| `conftest.py` | фикстуры |
| `tests/test_objects.py` | объект по ID |
| `tests/test_search.py` | поиск, лимиты, фильтры |

## Что проверяется

- **Объект по ID** — статус 200, модель `MetObject`,
  несуществующий ID → 404.
- **Поиск** — выдача и её структура, релевантность, пустой результат.
- **Лимиты** — по умолчанию 100, `limit` до 500, `offset`.
- **Фильтры** — `departmentId`, `isHighlight`, `title`,
  `dateBegin`/`dateEnd`.
- **Сортировка** — параметр `sort` API игнорирует.
