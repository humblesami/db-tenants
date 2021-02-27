import os
import glob


def remove_migrations():
    res = glob.glob('*/migrations/*', recursive=True)
    for file_path in res:
        if file_path.endswith('__pycache__'):
            file_path = file_path+'/*'
            sub_res = glob.glob(file_path)
            for file_sub_path in sub_res:
                os.remove(file_sub_path)
        elif not file_path.endswith('__init__.py'):
            os.remove(file_path)


def remove_files_by_type(ext):
    sub_res = glob.glob('*.'+ext, recursive=True)
    cnt = 0
    for file_path in sub_res:
        cnt += 1
        os.remove(file_path)
    print(str(cnt)+' ' + ext + ' files removed')


remove_migrations()
remove_files_by_type('pyc')
remove_files_by_type('po')

print('done')