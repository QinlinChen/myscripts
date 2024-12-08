import os
import sys
import filecmp
import shutil
import argparse


def die(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Directory synchronization')
    parser.add_argument('src_dir', help='source directory')
    parser.add_argument('dst_dir', help='destination directory')
    return parser.parse_args()


def check_dirs(src_dir, dst_dir, del_dir):
    if os.path.dirname(os.path.abspath(dst_dir)).startswith(os.path.abspath(src_dir)):
        die('The destination should not be the subdirectory of the source')
    if not os.path.exists(src_dir):
        die('The source directory does not exists.')
    if not os.path.isdir(src_dir):
        die('The source is not a directory.')
    if os.path.exists(dst_dir) and not os.path.isdir(dst_dir):
        die('The destination is not a directory.')
    if os.path.exists(del_dir):
        die(f"The directory '{del_dir}' containing last deleted files still exists. "
            f"Please delete it if it has no longer use.")


def sync_dir(src_dir, dst_dir, del_dir):
    cmp_result = filecmp.dircmp(src_dir, dst_dir)

    # Add files and directories only contained in src_dir to dst_dir.
    for src_uniq in cmp_result.left_only:
        src_path = os.path.join(src_dir, src_uniq)
        dst_path = os.path.join(dst_dir, src_uniq)
        add_path(src_path, dst_path)

    # Delete files and directories only contained in dst_dir.
    for dst_uniq in cmp_result.right_only:
        dst_path = os.path.join(dst_dir, dst_uniq)
        del_path = os.path.join(del_dir, dst_uniq)
        delete_path(dst_path, del_path)

    # Update different common files from src_dir to dst_dir.
    for diff_file in cmp_result.diff_files:
        src_path = os.path.join(src_dir, diff_file)
        dst_path = os.path.join(dst_dir, diff_file)
        del_path = os.path.join(del_dir, diff_file)
        update_path(src_path, dst_path, del_path)

    # Recursively synchronize common directories.
    for common_dir in cmp_result.common_dirs:
        sub_src = os.path.join(src_dir, common_dir)
        sub_dst = os.path.join(dst_dir, common_dir)
        sub_del = os.path.join(del_dir, common_dir)
        sync_dir(sub_src, sub_dst, sub_del)


def add_path(src_path, dst_path):
    try:
        if os.path.isfile(src_path):
            print('adding file:', dst_path)
            shutil.copy2(src_path, dst_path)
        elif os.path.isdir(src_path):
            print('adding dir:', dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            print('warning: file type unknown:', src_path)
    except PermissionError:
        print(f"No permission to sync: {src_path}.")


del_dir_used = False


def delete_path(dst_path, del_path):
    print('deleting:', dst_path)
    os.makedirs(os.path.dirname(del_path), exist_ok=True)
    shutil.move(dst_path, del_path)
    global del_dir_used
    del_dir_used = True


def update_path(src_path, dst_path, del_path):
    print('updating:', dst_path)
    os.makedirs(os.path.dirname(del_path), exist_ok=True)
    shutil.move(dst_path, del_path)
    shutil.copy2(src_path, dst_path)
    global del_dir_used
    del_dir_used = True


def append_basename(path, new_name):
    if path[-1] == '\\' or path[-1] == '/':
        path = path[:-1]
    new_basename = os.path.basename(path) + new_name
    return os.path.join(os.path.dirname(path), new_basename)


if __name__ == "__main__":
    print(sys.argv)
    args = parse_args()
    del_dir = append_basename(args.dst_dir, '.deleted')
    check_dirs(args.src_dir, args.dst_dir, del_dir)

    os.makedirs(args.dst_dir, exist_ok=True)
    sync_dir(args.src_dir, args.dst_dir, del_dir)

    print('Completed!')
    if del_dir_used:
        print(f"You can find deleted files or updated old files in the directory '{del_dir}'. "
              f"Remember to delete it if it has no longer use.")
