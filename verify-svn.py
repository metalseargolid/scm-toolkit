import sys
import os
from subprocess import Popen, PIPE
from time import sleep
import argparse

# Bin paths
svnadmin_bin = '/usr/bin/svnadmin'

# Global vars
__verbose = False
__repo_dir = '/repositories/svn'


# Functions
def verify_repository(repo_path):
    global __verbose

    # Since Python reads the buffer slower than it fills up, we deadlock and the program won't finish in a timely manner
    # Throw the output away because of this.
    nullpipe = open(os.devnull, "w")
    p = Popen([svnadmin_bin,
               'verify',
               repo_path], stdout=nullpipe, stderr=nullpipe)
    p.wait()
    if not p.returncode == 0:
        print("Svnadmin verify failed with return code {}".format(p.returncode), file=sys.stderr)
        return False
    return True


def parse_args():
    global __verbose
    global __repo_dir
    global svnadmin_bin

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False,
                        help='Display more verbose output.')
    parser.add_argument('-d', '--directory', dest='directory', type=str, default=__repo_dir,
                        help='Path to the repositories directory.')
    parser.add_argument('-b', '--svnadmin', dest='svnadmin_bin', type=str, default=svnadmin_bin)
    args = parser.parse_args()
    # Set verbose flag

    __verbose = args.verbose
    # Set repo dir
    __repo_dir = args.directory
    # Set svnadmin bin
    svnadmin_bin = args.svnadmin_bin


def process_output(file):
    output = file.read().split()
    for x in range(0, len(output)):
        output[x] = output[x].decode()
    return output


def append_to_list(original_list, list_to_append):
    for i in list_to_append:
        original_list.append(i)


def get_repository_list(dir_path):
    return os.listdir(dir_path)


def check_paths():
    global __repo_dir
    if not os.path.exists(svnadmin_bin):
        return "Can't find svnadmin binary at {}.".format(svnadmin_bin)
    if not os.path.exists(__repo_dir):
        return "Repository directory path does not exist at {}".format(__repo_dir)
    return None


# Main function
def __main():
    global __repo_dir
    print("Getting list of repositories at {}...".format(__repo_dir))
    try:
        repo_list = get_repository_list(__repo_dir)
    except FileNotFoundError as err:
        print(("Repository directory not found at '{}'. Please verify that the directory exists and that you have "
               "permission to access it.".format(__repo_dir)), file=sys.stderr)
        return -2
    except NotADirectoryError as err2:
        print(
            "The specified repository directory '{}' is not a directory. Please check your path and try again.".format(
                __repo_dir), file=sys.stderr)
        return -3
    print("Beginning repository verification process...")
    for repo_name in repo_list:
        print()
        print("Verifying {}".format(repo_name))
        full_path = os.path.join(__repo_dir, repo_name)
        if verify_repository(full_path):
            print("{} verified successfully!".format(repo_name))
        else:
            print("{} failed to verify.".format(repo_name), file=sys.stderr)
    return 0


# Entry point
if __name__ == '__main__':
    parse_args()
    check = check_paths()
    if check is None:
        sys.exit(__main())
    else:
        print(check)
        sys.exit(-1)
