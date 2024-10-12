import os
import sys


def get_repo_tree(repo_path):
    tree = {}
    for root, dirs, files in os.walk(repo_path):
        # Get relative path
        rel_root = os.path.relpath(root, repo_path)
        if rel_root == ".":
            rel_root = ""
        parts = rel_root.split(os.sep) if rel_root else []
        current = tree
        for part in parts:
            current = current.setdefault(part, {})
        for dir_name in sorted(dirs):
            current.setdefault(dir_name, {})
        for file_name in sorted(files):
            current[file_name] = None
    return tree


def print_tree(tree, prefix=""):
    lines = []
    for key in sorted(tree.keys()):
        if tree[key] is None:
            lines.append(prefix + key)
        else:
            lines.append(prefix + key + "/")
            lines.extend(print_tree(tree[key], prefix + "    "))
    return lines


def is_binary_file(file_path):
    """
    Simple binary file detection.
    Reads the first 1024 bytes of the file and checks for null bytes.
    """
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return True
            # Additional binary detection logic can be added here
    except:
        return True
    return False


def main(repo_path, output_file):
    if not os.path.isdir(repo_path):
        print(f"The specified path is not a directory: {repo_path}")
        sys.exit(1)

    # Get the directory tree structure
    tree = get_repo_tree(repo_path)
    tree_lines = print_tree(tree)

    with open(output_file, "w", encoding="utf-8") as out_f:
        out_f.write("Repository Tree:\n")
        out_f.write("\n".join(tree_lines))
        out_f.write("\n\n")

        files = []
        for root, dirs, filenames in os.walk(repo_path):
            # Uncomment the following lines to skip hidden directories or files
            # dirs[:] = [d for d in dirs if not d.startswith('.')]
            # filenames = [f for f in filenames if not f.startswith('.')]

            rel_root = os.path.relpath(root, repo_path)
            if rel_root == ".":
                rel_root = ""
            for file in sorted(filenames):
                rel_path = os.path.join(rel_root, file) if rel_root else file
                files.append(rel_path)

        for i, file_path in enumerate(files):
            abs_path = os.path.join(repo_path, file_path)
            # Skip binary files
            if is_binary_file(abs_path):
                content = f"// Binary file content skipped: {file_path}\n"
            else:
                try:
                    with open(abs_path, "r", encoding="utf-8") as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(abs_path, "r", encoding="latin-1") as f:
                            content = f.read()
                    except Exception as e:
                        print(f"Error reading file ({file_path}): {e}")
                        content = f"// Failed to read file: {e}\n"
                except Exception as e:
                    print(f"Error reading file ({file_path}): {e}")
                    content = f"// Failed to read file: {e}\n"

            out_f.write(content)
            out_f.write(f"[End of file No.{i}]\n\n")
            if i + 1 < len(files):
                out_f.write(f"{file_path}:\n[Start of file No.{i + 1}]\n")

    print(f"Output file has been created: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python repo_to_text_no_git.py <Directory Path> <Output File Name>"
        )
        sys.exit(1)

    repo_path = sys.argv[1]
    output_file = sys.argv[2]
    main(repo_path, output_file)
