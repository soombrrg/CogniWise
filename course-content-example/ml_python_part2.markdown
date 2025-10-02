# Машинное обучение на Python: Часть 2

Продолжаем изучать машинное обучение с Python. В этом блоке рассмотрим анализ данных с *Pandas*, визуализацию с *Matplotlib* и создание простой модели с *scikit-learn*.

## Анализ данных с Pandas

*Pandas* — мощная библиотека для работы с данными.

### Пример: Чтение и фильтрация

```python
import pandas as pd

# Чтение CSV
data = pd.read_csv('housing.csv')
# Фильтрация данных
filtered_data = data[data['price'] > 100000]
print(filtered_data.head())
```

> **Совет**: Используйте `data.describe()` для быстрого анализа статистики.

## Визуализация с Matplotlib

*Matplotlib* помогает создавать графики для анализа данных.

### Пример: Построение графика

```python
import matplotlib.pyplot as plt

plt.scatter(data['size'], data['price'], color='blue')
plt.xlabel('Размер (кв.м)')
plt.ylabel('Цена ($)')
plt.title('Зависимость цены от размера')
plt.show()
```

## Построение модели с scikit-learn

Создадим простую модель линейной регрессии.

### Пример: Линейная регрессия

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

X = data[['size']]  # Признак
y = data['price']   # Целевая переменная
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)
print(f"Точность: {model.score(X_test, y_test):.2f}")
```

## Практическое задание

1. Загрузите датасет с [Kaggle](https://kaggle.com).
2. Проведите анализ: найдите средние значения и постройте график.
3. Создайте и обучите модель линейной регрессии.

```python
# Пример предсказания
prediction = model.predict([[120]])  # Размер 120 кв.м
print(f"Предсказанная цена: ${prediction[0]:.2f}")
```

## Что дальше?

- Изучите **очистку данных**: обработка пропусков и выбросов.
- Попробуйте **нейронные сети** с TensorFlow.
- Углубитесь в метрики оценки моделей: MSE, R².

Для практики посетите [Kaggle](https://kaggle.com) или [Google Colab](https://colab.research.google.com).