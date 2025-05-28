 # Запуск
 Для запуска проекта необходимо создать файл .env и заполнить его аналогично .env_example

# Доступно два варианта запуска
## USE_TEST_BASE=True
В этом случае проект запустится с базой данных sqlite на которой будут присутствовать тестовые данные.
Уже созданы следущие аккаунты

1. Иван Петров
Никнейм: IvanTheGreat
Почта: ivan.petrov@example.com
Пароль: Petrov123!

2. Елена Смирнова
Никнейм: LenaSmile
Почта: elena.smirnova@testmail.com
Пароль: SmirnovaE2024

3. Алексей Козлов
Никнейм: Kozel_Alex
Почта: alex.kozlov@demo.org
Пароль: Kozlov$$99

4. Мария Иванова
Никнейм: MashaMagic
Почта: maria.ivanova@fakeinbox.com
Пароль: Masha12345

5. Дмитрий Соколов
Никнейм: SokolDima
Почта: dmitry.sokolov@temp-mail.net
Пароль: Sokol!D2024

6. Анна Кузнецова
Никнейм: AnnaKuz
Почта: anna.kuznetsova@mockbox.org
Пароль: KuzAnna!777

7. admin
Почта: admin@example.com
Пароль: admin

## USE_TEST_BASE=False
В данном случае тестовой базы нет, проект работает на postgresql. В базе присутствуют только админ и ингредиенты.