import os
import re


def get_input_files(input_dirpath, pattern):
    """Returns the files in input_dirpath that matches pattern."""
    all_files = os.listdir(input_dirpath)
    for filename in all_files:
        if re.match(pattern, filename) and os.path.isfile(os.path.join(
                input_dirpath, filename)):
            yield os.path.join(input_dirpath, filename)


def get_input_directories(input_dirpath, pattern):
    """Returns the directories in input_dirpath that matches pattern."""
    all_files = os.listdir(input_dirpath)
    for dirname in all_files:
        if re.match(pattern, dirname) and not os.path.isfile(os.path.join(
                input_dirpath, dirname)):
            yield os.path.join(input_dirpath, dirname)


def safe_mkdir(dir_path):
    """Checks if a directory exists, and if it doesn't, creates one."""
    try:
        os.stat(dir_path)
    except OSError:
        os.mkdir(dir_path)