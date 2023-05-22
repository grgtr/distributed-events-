import os


def run_server(statement=0):
    if statement:
        os.system('python manage.py makemigrations')
        os.system('python manage.py migrate')
        #os.system('python manage.py loaddata fixtures/testing_data.json')
    # os.system('python manage.py collectstatic')
    os.system('python manage.py runserver')


if __name__ == '__main__':
    state = input('Выполнить миграции? Y/N \n').lower()
    state = 1 if state == 'y' else 0
    run_server(state)
