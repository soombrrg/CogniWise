# Python для начинающих: Часть 2

Продолжаем изучать основы Python. В этой статье разберем списки, словари, работу с файлами и установку библиотек.

## Списки

Списки — это упорядоченные коллекции данных:

```python
fruits = ["яблоко", "банан", "апельсин"]
fruits.append("груша")  # Добавление элемента
print(fruits[0])  # Вывод: яблоко
```

- Изменение элемента: `fruits[1] = "киви"`
- Удаление: `fruits.remove("банан")` или `del fruits[0]`

## Словари

Словари хранят пары "ключ-значение":

```python
person = {"name": "Алексей", "age": 25}
print(person["name"])  # Вывод: Алексей
person["city"] = "Москва"  # Добавление
```

> **Совет**: Используйте `person.get("key", "default")`, чтобы избежать ошибок при отсутствии ключа.

## Работа с файлами

Чтение и запись файлов — важная часть программирования:

```python
# Запись в файл
with open("example.txt", "w") as file:
    file.write("Привет, Python!\n")

# Чтение из файла
with open("example.txt", "r") as file:
    content = file.read()
    print(content)
```

## Установка библиотек

Python имеет множество библиотек. Установите их с помощью `pip`:

```bash
pip install requests
```

Пример использования библиотеки `requests`:

```python
import requests
response = requests.get("https://api.github.com")
print(response.status_code)  # Вывод: 200
```

## Практическое задание

1. Создайте список покупок.
2. Добавьте в него 3 продукта.
3. Сохраните список в файл `shopping.txt`.
4. Прочитайте файл и выведите содержимое.

```python
shopping = ["хлеб", "молоко", "яйца"]
with open("shopping.txt", "w") as file:
    for item in shopping:
        file.write(item + "\n")

with open("shopping.txt", "r") as file:
    print(file.read())
```

## Что дальше?

- Изучите **обработку исключений** с `try/except`.
- Погрузитесь в **объектно-ориентированное программирование**.
- Попробуйте библиотеки вроде `pandas` для анализа данных.

Для вопросов и поддержки посетите [форум Python](https://python.org/community/).