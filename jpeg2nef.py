import os
import sys
import shutil

def replace_jpeg_with_nef(dir):
    if not os.path.isdir(dir):
        print(f"Directory {dir} does not exist.")
        return

    # Get the parent directory path
    parent_dir = os.path.abspath(os.path.join(dir, os.pardir))

    # Replace JPEG files with NEF files
    for file in os.listdir(dir):
        if file.lower().endswith('.jpeg') or file.lower().endswith('.jpg'):
            jpeg_file_path = os.path.join(dir, file)

            # Assume the corresponding NEF file is in the parent directory
            nef_file_name = os.path.splitext(file)[0] + '.NEF'
            nef_file_path = os.path.join(parent_dir, nef_file_name)

            if os.path.isfile(nef_file_path):
                # Replace the JPEG file with the NEF file
                print(f"Replacing {jpeg_file_path} with {nef_file_path}")
                shutil.copy2(nef_file_path, os.path.join(dir, nef_file_name))
                os.remove(jpeg_file_path)
            else:
                print(f"Corresponding NEF file not found: {nef_file_path}")

def main():
    # Check for command line arguments
    if len(sys.argv) != 2:
        print("Usage: python script.py <working_directory>")
        sys.exit(1)

    work_dir = sys.argv[1]
    replace_jpeg_with_nef(work_dir)

if __name__ == '__main__':
    main()