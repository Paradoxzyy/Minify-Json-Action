import json
import os
import sys
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("--changed_files", default="[]")
parser.add_argument("--deleted_files", default="[]")
parser.add_argument("--prefix", default="")
parser.add_argument("--suffix", default="")
args = parser.parse_args()
args.changed_files = json.loads(args.changed_files, strict=False)
args.deleted_files = json.loads(args.deleted_files, strict=False)

def main():
    # Changed files
    for i, in_file in enumerate(args.changed_files):
        if not in_file or not os.path.isfile(in_file):
            print("index:", i, "{:} is not a file!".format(in_file))
            continue

        try:
            path, filefullname = os.path.split(in_file)
            filename, ext = os.path.splitext(filefullname)
            out_file = path + "/" + args.prefix + filename + args.suffix + ext
            content = None

            print("index:", i, "Reading file {:}".format(in_file))
            with open(in_file, "r", encoding="utf-8") as f_in:
                content = remove_comments(f_in.read())
                content = json.loads(content, strict=False)
        
            print("index:", i, "Writing file {:}".format(out_file))
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            with open(out_file, "w", encoding="utf-8") as f_out:
                json.dump(content, f_out, ensure_ascii=False, check_circular=False, indent=None, separators=(",", ":"))

        except Exception as e:
            print("index:", i, "Failed to parse {:}, skipping".format(in_file))
            pass

    # Deleted files
    for i, in_file in enumerate(args.deleted_files):
        if os.path.isfile(in_file):
            continue

        path, filefullname = os.path.split(in_file)
        filename, ext = os.path.splitext(filefullname)
        prefix_path = os.path.split(args.prefix)[0]
        out_file = path + "/" + args.prefix + filename + args.suffix + ext
        out_dir = path + "/" + prefix_path

        if os.path.isfile(out_file):
            os.remove(out_file)
            print("index:", i, "Deleted file {:}".format(out_file))

        if os.path.isdir(out_dir):
            try:
                os.rmdir(out_dir)
                print("index:", i, "Deleted directory {:}".format(out_dir))
            except OSError:
                pass

def remove_comments(string):
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)

    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        # so we will return empty to remove the comment
        # otherwise, we will return the 1st group
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)

    return regex.sub(_replacer, string)

if __name__ == "__main__":
    main()
