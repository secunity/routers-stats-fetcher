import os
import datetime

health_check_file_path = "logs/health_check.txt"
error_health_check_file_path = "logs/error_health_check.txt"
format_time = '%Y-%m-%d - %H:%M:%S'
max_size_log = 10
min_size_log = max_size_log//2


def add_line(line, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{line}\n")


def check_lines_size(lines, file_path):
    if len(lines) > max_size_log:
        os.remove(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[min_size_log:])


def read_health_check(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        remove_n = -1
        dt1 = lines[-1].split(',')[1][:remove_n]
        dt1 = dt1
        dt1 = datetime.datetime.strptime(dt1, format_time)
        check_lines_size(lines=lines, file_path=file_path)
        return dt1


def after_request(url_path, file_path):
    add_line(f'{url_path},{datetime.datetime.utcnow().strftime(format_time)}', file_path)

