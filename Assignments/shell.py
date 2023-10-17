import os
import threading
import time

import shutil
import glob
import re

history = []


def run_command(command, args, background, input_data):

    if command == 'exit':
        os._exit(0)
    elif command == 'ls':
        if len(args) == 1 and args[0] == "--help":
            return execute_ls._doc_
        return execute_ls(args)
    elif command == 'mkdir':
        if len(args) == 1 and args[0] == "--help":
            return execute_mkdir._doc_
        return execute_mkdir(args)
    elif command == 'cd':
        if len(args) == 1 and args[0] == "--help":
            return execute_cd._doc_
        return execute_cd(args)
    elif command == 'pwd':
        if len(args) == 1 and args[0] == "--help":
            return execute_pwd._doc_
        return execute_pwd()
    elif command == 'cp':
        if len(args) == 1 and args[0] == "--help":
            return execute_cp._doc_
        return execute_cp(args)
    elif command == 'mv':
        if len(args) == 1 and args[0] == "--help":
            return execute_mv._doc_
        return execute_mv(args)
    elif command == 'rm':
        if len(args) == 1 and args[0] == "--help":
            return execute_rm._doc_
        return execute_rm(args)
    elif command == 'rmdir':
        if len(args) == 1 and args[0] == "--help":
            return execute_rmdir._doc_
        return execute_rmdir(args)
    elif command == 'cat':
        if len(args) == 1 and args[0] == "--help":
            return execute_cat._doc_
        return execute_cat(args)
    elif command == 'head':
        if len(args) == 1 and args[0] == "--help":
            return execute_head._doc_
        return execute_head(args, input_data)
    elif command == 'tail':
        if len(args) == 1 and args[0] == "--help":
            return execute_tail._doc_
        return execute_tail(args, input_data)
    elif command == 'grep':
        if len(args) == 1 and args[0] == "--help":
            return execute_grep._doc_
        return execute_grep(args, input_data)
    elif command == 'wc':
        if len(args) == 1 and args[0] == "--help":
            return execute_wc._doc_
        return execute_wc(args, input_data)
    else:
        return f'Command {command} not found.'


def format_size(num, suffix='B'):
    '''Helper function to return size in a human readable format'''
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def execute_ls(args):
    """
    list files and directories
    Uses: ls [flags]

    flags:
    -a : list all show hidden files
        -l : long listing
    -h : human readable sizes
    """

    list_all = '-a' in args
    long_listing = '-l' in args
    human_readable = '-h' in args

    flags = [x for x in args if x[0] == "-"]
    for flag in flags:
        if 'a' in flag:
            list_all = True
        if 'l' in flag:
            long_listing = True
        if 'h' in flag:
            human_readable = True

    directory = '.'

    if len(args) > 0 and not (list_all or long_listing or human_readable):
        directory = args[0]
    else:
        directory = os.getcwd()

    filenames = os.listdir(directory)

    if not list_all:
        filenames = [f for f in filenames if not f.startswith('.')]

    results = []

    for filename in filenames:
        path = os.path.join(directory, filename)
        stats = os.stat(path)

        if long_listing:
            file_mode = stats.st_mode
            file_links = stats.st_nlink
            file_owner = stats.st_uid
            file_group = stats.st_gid
            file_size = stats.st_size if not human_readable else format_size(
                stats.st_size)
            file_mtime = stats.st_mtime
            formatted_time = time.strftime(
                '%b %d %H:%M', time.localtime(file_mtime))

            results.append(
                f"file_mode  file_links  file_owner  file_group  file_size   formatted_time  filename")
            results.append(
                f"{file_mode:7}\t\t{file_links}\t{file_owner}\t{file_group}\t{file_size:8}\t{formatted_time}\t{filename}")
        else:
            results.append(filename)

    return "\n".join(results)


def execute_mkdir(args):
    """
    make a directory
    Uses: mkdir directory_name
    """
    if len(args) != 1:
        return "Usage: mkdir directory_name"
    else:
        directory_name = args[0]
        try:
            os.mkdir(directory_name)
            return f"{directory_name} created successfully"
        except FileExistsError:
            return f"mkdir: cannot create directory '{directory_name}': File exists"
        except FileNotFoundError:
            return f"mkdir: cannot create directory '{directory_name}': No such file or directory"


def execute_cd(args):
    """
    change to named directory
    Uses: cd directory_name
    """
    if not args or args[0] == "~":
        target_directory = os.path.expanduser("~")
    else:
        target_directory = args[0]

    try:
        os.chdir(target_directory)
    except FileNotFoundError:
        return f"cd: {target_directory}: No such file or directory"


def execute_pwd():
    """
    display the path of the current directory
    Uses: pwd
    """
    return os.getcwd()


def execute_cp(args):
    """
    copy file1 and call it file2
    Uses: cp file1 file2
    """
    if len(args) < 2:
        return "cp: missing destination file operand"
    src, dest = args[0], args[1]
    if not os.path.exists(src):
        return f"cp: cannot stat '{src}': No such file or directory"
    try:
        shutil.copy2(src, dest)
        return f"file {src} copied to {dest}"
    except Exception as e:
        return f"cp: error: {str(e)}"


def execute_mv(args):
    """
    move or rename file1 to file2
    Uses: mv file1 file2
    """
    if len(args) < 2:
        return "mv: missing destination file operand"
    src, dest = args[0], args[1]
    if not os.path.exists(src):
        return f"mv: cannot stat '{src}': No such file or directory"
    try:
        shutil.move(src, dest)
        return f"file {src} moved to {dest}"
    except Exception as e:
        return f"mv: error: {str(e)}"


def execute_rm(args):
    """
    remove a file
    Uses: rm [Flags] filename

    Flags:
    -r : recurse into non-empty folder to delete all
    """
    if not args:
        return "rm: missing operand"
    file_pattern = args[-1]

    recursive = '-r' in args

    result = ""
    for file_or_dir in glob.glob(file_pattern):
        try:
            if os.path.isdir(file_or_dir):
                if recursive:
                    shutil.rmtree(file_or_dir)
                    result += f"Removed directory {file_or_dir}\n"
                else:
                    return f"rm: cannot remove '{file_or_dir}': Is a directory"
            else:
                os.remove(file_or_dir)
                result += f"Removed directory {file_or_dir}\n"
        except Exception as e:
            return f"rm: error removing '{file_or_dir}': {str(e)}"
    return result[:-1]


def execute_rmdir(args):
    """
    remove a directory
    """
    if not args:
        return "rmdir: missing operand"
    directory = args[0]
    try:
        os.rmdir(directory)
        return f"Directory removed: {directory}"
    except Exception as e:
        return f"rmdir: error: {str(e)}"


def execute_cat(args):
    """
    display a file
    Uses: cat file

    For cat file1 file2 fileN display each of the files as if they were concatenated
    """
    if not args:
        return "cat: missing file operand"

    output = []
    for filename in args:
        try:
            with open(filename, 'r') as f:
                output.append(f.read())
        except FileNotFoundError:
            output.append(f"cat: {filename}: No such file or directory")
        except Exception as e:
            output.append(f"cat: {filename}: {str(e)}")
    return "\n".join(output)


def execute_head(args, input_data):
    """
    display the first few lines of a file
    Uses head [-n ...] file
    """
    if (not input_data) and not args:
        return "head: missing file operand"

    num_lines = 10  # Default value
    filename = ""

    if '-n' in args:
        try:
            n_index = args.index('-n')
            num_lines = int(args[n_index + 1])
            if not input_data:
                filename = args[n_index + 2]
        except (ValueError, IndexError):
            return "head: invalid number of lines"

    if input_data:
        lines = input_data.splitlines()[:num_lines]
        return "\n".join(lines)
    else:
        filename = args[0]
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return f"head: {filename}: No such file or directory"
        except Exception as e:
            return f"head: {filename}: {str(e)}"

    return ''.join(lines[:num_lines])


def execute_tail(args, input_data):
    """
    display the last few lines of a file
    Uses tail [-n ...] file
    """
    if (not input_data) and not args:
        return "tail: missing file operand"

    num_lines = 10  # Default value
    filename = ""

    if '-n' in args:
        try:
            n_index = args.index('-n')
            num_lines = int(args[n_index + 1])
            if not input_data:
                filename = args[n_index + 2]
        except (ValueError, IndexError):
            return "tail: invalid number of lines"

    if input_data:
        lines = input_data.splitlines()[-num_lines:]
        return "\n".join(lines)
    else:
        filename = args[0]
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return f"tail: {filename}: No such file or directory"
        except Exception as e:
            return f"tail: {filename}: {str(e)}"

    return ''.join(lines[-num_lines:])


def execute_grep(args, input_data):
    """
    search a file(s) files for keywords and print lines where pattern is found
    Uses: grep [Flags] keyword file

    Flag:
    -l : only return file names where the word or pattern is found
    """
    if (not input_data) and len(args) < 2:
        return "grep: missing arguments"

    list_files_only = False
    if '-l' in args:
        list_files_only = True
        args.remove('-l')

    keyword = args[0]
    files = args[1:]

    output = []
    try:
        if input_data:
            for index, line in enumerate(input_data.splitlines()):
                if re.search(keyword, line):
                    if not list_files_only:
                        output.append(f"{index+1}:{line.strip()}")
        else:
            for filename in files:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    for index, line in enumerate(lines):
                        if re.search(keyword, line):
                            if not list_files_only:
                                output.append(
                                    f"{filename}:{index+1}:{line.strip()}")
                            else:
                                output.append(filename)
                                break
    except FileNotFoundError:
        output.append(f"grep: {filename}: No such file or directory")
    except Exception as e:
        output.append(f"grep: {filename}: {str(e)}")

    return "\n".join(output)


def execute_wc(args, input_data):
    if (not input_data) and not args:
        return "wc: missing file operand"

    result = ""

    count_lines = False
    count_words = False
    count_chars = False

    flags = [x for x in args if x[0] == "-"]
    for flag in flags:
        if 'l' in flag:
            count_lines = True
        if 'w' in flag:
            count_words = True
        if 'm' in flag:
            count_chars = True

    args = [x for x in args if x[0] != "-"]

    if not (count_lines or count_words or count_chars):
        count_lines, count_words, count_chars = True, True, True

    if input_data:
        content = input_data
    else:
        filename = args[0]
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return f"wc: {filename}: No such file or directory"
        except Exception as e:
            return f"wc: {filename}: {str(e)}"

    lines = content.split('\n')
    words = content.split()
    chars = len(content)

    if count_lines:
        result += "Lines: " + str(len(lines)) + '\n'
    if count_words:
        result += "Words: " + str(len(words)) + '\n'
    if count_chars:
        result += "Characters: " + str(chars) + '\n'

    if not input_data:
        result += "Filename: " + filename

    return result[:-1]


def main():
    while True:
        # try:
            output = ""
            # Print prompt
            print('$: ', end='', flush=True)

            # Read a line from stdin
            line = input().strip()

            # Tokenize the command
            tokens = line.split()
            if len(tokens) == 0:
                continue

            input_file = None
            output_file = None
            if "<" in tokens:
                ind = tokens.index("<")
                input_file = tokens[ind + 1]
                tokens = tokens[:ind]
            elif ">" in tokens:
                ind = tokens.index(">")
                output_file = tokens[ind + 1]
                tokens = tokens[:ind]

            pipe_to_command = None
            if "|" in tokens:
                ind = tokens.index("|")
                tokens, pipe_to_command = tokens[:ind], tokens[ind+1:]

            else:
                pass

            command = tokens[0]
            args = tokens[1:]

            input_data = None
            if input_file:
                with open(input_file, 'r') as f:
                    input_data = f.read()

            if pipe_to_command:
                input_data = run_command(command, args, None, input_data)
                command = pipe_to_command[0]
                args = pipe_to_command[1:]

            background = False
            if '&' in args:
                background = True
                args.remove('&')

            if background:
                thread = threading.Thread(target=run_command, args=(
                    command, args, background, input_data))
                thread.start()
            else:
                output = run_command(command, args, background, input_data)

            if output_file:
                
                with open(output_file, 'w') as f:
                    f.write(output)
            elif not background:
                if output:
                    print(output)
            history.append(line)

        # except Exception as e:
        #     print("Error ", e)


if _name_ == '_main_':
    main()
