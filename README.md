# CTF Challenge: SQL Injection Exploit

## Описание уязвимости
Это приложение демонстрирует уязвимость, связанную с SQL-инъекцией на эндпоинте авторизации. Участникам CTF нужно получить доступ к защищённому ресурсу, используя уязвимость в механизме авторизации.

## Почему это происходит?
- Приложение использует сырой SQL-запрос для проверки логина и пароля.
- Пользовательский ввод не экранируется, что позволяет внедрить произвольный SQL-код.
- Если инъекция успешна, злоумышленник может войти в систему под любым пользователем, включая администратора.

## Способы защиты
1. **Использование ORM** – замените сырые SQL-запросы на безопасные ORM-запросы (например, SQLAlchemy).
2. **Экранирование пользовательского ввода** – используйте параметризованные запросы или подготовленные выражения.
3. **Валидация входных данных** – проверяйте, соответствует ли пользовательский ввод ожидаемым форматам.
4. **Ограничение привилегий БД** – минимизируйте права пользователей БД, чтобы ограничить потенциальный ущерб.

## Запуск приложения
### Требования:
- Docker
- Docker Compose

### Инструкция по запуску:
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/CTF_SQLi.git
2. Перейдите в директорию проекта:
    ```bash
   cd CTF_SQLi
3. Запустите приложение:
    ```bash
   docker-compose up --build
4. Приложение будет доступно по адресу: `http://localhost:5000`

### PoC-эксплоит для получения флага
1. Зарегистрируйтесь как обычный пользователь через `/register`
2. Зайдите в систему под своим созданным аккаунтом
3. Далее перейдите на Эндпоинт для добавления записи на страницу `/text` и попробуйте добавить пост `Add post`
4. Перейдите на домашнюю страницу `/`
5. Вы увидите, что все посты читаемы для вас кроме поста админа с ником `Kirill`
6. В правом верхнем углу нажмите на кнопку выхода из аккаунта `Log out`
7. Теперь вы неавторизованы. Ещё раз перейдите на эндпоинт `/login`. Вас изместен никнейм админа, осталось использовать SQL-инъекцию и получить доступ к аккаунту админа.
8. В поле логина введите `Kirill' --`, а в поле пароля любую последовательность букв или цифр.
9. Если инъекция успешна, вы войдёте в систему как администратор.
10. Перейдите на домашнюю страницу `/`, чтобы увидеть флаг, который содержится в посте администратора.

### Как это работает?
1. Приложение выполняет следующий небезопасный SQL-запрос при входе пользователя:
    ```sql
   SELECT * FROM users WHERE username = 'введённый_логин' AND password = 'введённый_пароль';
2. Если мы введём Kirill' -- в поле логина, запрос примет следующий вид:
    ```sql
    SELECT * FROM users WHERE username = 'admin' -- ' AND password = '123';
Запрос теперь проверяет только `username = 'Kirill'`, а всё, что идёт после `--`, игнорируется.
Таким образом, проверка пароля пропускается, и система авторизует нас как администратора.