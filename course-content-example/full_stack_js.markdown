# Full-stack JavaScript: React, Node.js, Express и MongoDB

Full-stack разработка на JavaScript позволяет создавать современные веб-приложения от фронтенда до бэкенда. В этой статье разберем ключевые технологии: *React*, *Node.js*, *Express* и *MongoDB*.

## Почему JavaScript для full-stack?

- **Единый язык**: JavaScript используется как на клиенте, так и на сервере.
- **Экосистема**: Огромное количество библиотек и инструментов.
- **Производительность**: Быстрая разработка и масштабируемость.

## React: Фронтенд

*React* — библиотека для создания пользовательских интерфейсов.

### Пример компонента

```javascript
import React from 'react';

function App() {
  return <h1>Привет, React!</h1>;
}

export default App;
```

> **Совет**: Используйте [Create React App](https://create-react-app.dev) для быстрого старта.

## Node.js: Среда выполнения

*Node.js* позволяет запускать JavaScript на сервере.

### Пример сервера

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Привет, Node.js!\n');
});

server.listen(3000, () => {
  console.log('Сервер запущен на порту 3000');
});
```

## Express: Бэкенд-фреймворк

*Express* упрощает создание API.

### Пример API

```javascript
const express = require('express');
const app = express();

app.get('/api', (req, res) => {
  res.json({ message: 'Привет, Express!' });
});

app.listen(3000, () => console.log('API работает на порту 3000'));
```

> Установите Express: `npm install express`

## MongoDB: База данных

*MongoDB* — NoSQL база данных для хранения данных в формате JSON.

### Пример подключения

```javascript
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/mydb', {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => console.log('Подключено к MongoDB'));
```

## Практическое задание

1. Создайте React-компонент для отображения списка задач.
2. Настройте Express API для получения задач из MongoDB.
3. Подключите фронтенд к бэкенду через `fetch`.

```javascript
// Пример API-запроса в React
fetch('/api/tasks')
  .then(res => res.json())
  .then(data => console.log(data));
```

## Что дальше?

- Изучите **Redux** для управления состоянием в React.
- Настройте **аутентификацию** с помощью JWT.
- Разверните приложение на [Heroku](https://heroku.com) или [Vercel](https://vercel.com).