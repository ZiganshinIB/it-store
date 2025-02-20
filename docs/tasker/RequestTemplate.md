# RequestTemplate - шаблон заявки
## Цель
Служит шаблоном для заявок. На их основании формируются заявки. 
Создают и редактируют их только люди имеющие права(соответствующие доступы).

## Поля

| Название          | Тип        | Описание             | Обязательность    |
|-------------------|------------|----------------------|-------------------|
| title             | CharField  | Название шаблона     | Обязательное поле |
| description       | CharField  | Описание шаблона     | -                 |
| image             | ImageField | Изображение шаблона  | -                 |
| dedline           | Duration   | Срок выполнения      | Обязательное поле |
| approval_route    | ForeignKey | Маршрут согласования | Обязательное поле |
| dedline           | Duration   | Срок выполнения      | Обязательное поле |
| complexity        | Сhoice     | Сложность            | Обязательное поле |
| group             | ForeignKey | Группа               | -                 |
| tasks             | ManyToMany | Задачи               | Может быть Пустым |


## Доступы

| Доступ                        | Описание                                         |
|-------------------------------|--------------------------------------------------|
| tasker.add_requesttemplate    | Пользователь может создавать шаблоны заявок      |
| tasker.view_requesttemplate   | Пользователь может просматривать шаблоны заявок  |
| tasker.change_requesttemplate | Пользователь может редактировать шаблоны заявок  |
| tasker.delete_requesttemplate | Пользователь может удалять шаблоны заявок        |

## Работа
Заявка созданное по этому шаблону будут доступны только тем пользователям, имеющим группу указанная в поле `group` и также сам владелец (автор) заявки.
Также и оповещение будет направлено этим пользователям. Если группа пустая то оповещения будут направлены всем пользователям.
Если `approval_route` не пустая. То заявка будет создана с согласованием в маршруте и заявка будет иметь статус "На согласовании". 
Если `tasks` не пустая. То заявка будет создана с задачами, указанными в поле `tasks`.

В админ панели вы можете сразу указать список [шаблонов задач](./TaskTemplate.md)