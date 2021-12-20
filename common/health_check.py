import os
import datetime

from common.consts import HEALTH_CHECK
from common.logs import Log


def add_line(line, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{line}\n")


def check_lines_size(lines, file_path):
    if len(lines) > HEALTH_CHECK.MAX_SIZE_LOG:
        Log.info(f'remove lines for file: {file_path}')
        os.remove(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[HEALTH_CHECK.MIN_SIZE_LOG:])


def read_health_check_files(logfile_path: str, ok_health_check: str, error_health_check: str, **kwargs):
    def check_file(file_name: str):
        file_path = f'{logfile_path}{file_name}'
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                remove_n = -1
                dt1 = lines[-1].split(',')[1][:remove_n]
                dt1 = dt1
                dt1 = datetime.datetime.strptime(dt1, HEALTH_CHECK.FORMAT_TIME)
                check_lines_size(lines=lines, file_path=file_path)
                return dt1

        return False
    return check_file(file_name=ok_health_check), check_file(file_name=error_health_check)

def after_request(url_full_path: str, success:bool, logfile_path: str, ok_health_check: str, error_health_check: str, **kwargs):
    file_name = ok_health_check if success else error_health_check
    file_path = f'{logfile_path}{file_name}'
    add_line(f'{url_full_path},{datetime.datetime.utcnow().strftime(HEALTH_CHECK.FORMAT_TIME)}', file_path)



