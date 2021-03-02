import os
import glob
import pathlib

root_path = pathlib.Path(__file__).parent.absolute()


def remove_migrations():
    migrations_paths = str(root_path)+'/**/migrations/*'
    res = glob.glob(migrations_paths, recursive=True)
    cnt = 0
    for file_path in res:
        if file_path.startswith(str(root_path)+'/django/'):
            continue
        if file_path.endswith('__pycache__'):
            file_path = file_path+'/*'
            sub_res = glob.glob(file_path)
            for file_sub_path in sub_res:
                cnt += 1
                os.remove(file_sub_path)
        elif not file_path.endswith('__init__.py'):
            cnt += 1
            os.remove(file_path)
    print(str(cnt) + ' migrations files removed')


def remove_files_by_type(ext):
    sub_res = glob.glob(str(root_path)+'/**/*.'+ext, recursive=True)
    cnt = 0
    for file_path in sub_res:
        cnt += 1
        os.remove(file_path)
    print(str(cnt)+' ' + ext + ' files removed')


remove_migrations()
remove_files_by_type('pyc')
remove_files_by_type('po')

print('done')