#!/usr/bin/env python
# Software License Agreement (GNU GPLv3  License)
#
# Copyright (c) 2022, Roland Jung (rolandjung0@gmail.com)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Requirements:
# sudo pip install Pillow tqdm argparse

import sys
import os
import platform
import argparse
import shutil
from tqdm import tqdm
from datetime import datetime
from datetime import date
from datetime import timedelta
import subprocess


def exit_success():
    print("#########################   SUCCESS   #######################")
    sys.exit(0)


def exit_failure():
    print("#########################   FAILURE   #######################")
    sys.exit(1)


def get_files_with_ext(dir, ext, verbose, recursive):
    file_list = []
    if recursive:
        for r, d, f in os.walk(dir):
            for file in f:
                if file.endswith(ext):
                    found_file = os.path.join(r, file)
                    if verbose:
                        print("found file:%s" % found_file)
                    file_list.append(found_file)
    else:
        for file in os.listdir(dir):
            if file.endswith(ext):
                found_file = os.path.join(dir, file)
                if verbose:
                    print("found file:%s" % found_file)
                file_list.append(found_file)
    return file_list


def get_datatime_object_from_file(fn):
    try:  # try the modification timestamp:
        # mtime = creation_date(fn)
        datetime_object = datetime.fromtimestamp(os.path.getmtime(fn))
        # print("last modified: %s" % time.ctime(datetime_object))
        return datetime_object, True
    except:
        return None, False

# --input_dir ./test/in --output_dir ./test/out --verbose --create_tree
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Converting all HEIC files from the input_dir and stores it in output_dir using heif-convert (sudo apt install libheif-examples):\n usage: --input_dir ../test/rename_in --output_dir ../test/rename_out --ext heic --prefix bla --verbose --add_hours 123')
    parser.add_argument('--input_dir', help='directory with images', default="")
    parser.add_argument('--output_dir', help='directory for converted images', default="")
    parser.add_argument('--quality', required=False, type=int, choices=range(0, 101), metavar='[0-100]', help='JPG quality 0-100 (95)', default=95)
    parser.add_argument('--prefix', help='prefix to the final image name: <prefix><data>.<ext>', default='')
    parser.add_argument('--ext', help='file extension', default='HEIC')
    parser.add_argument('--verbose', action='store_true', help='verbose', default=False)
    parser.add_argument('--create_tree', action='store_true', help='create date folder tree', default=False)
    parser.add_argument('--no_recursive', action='store_true', help='no recursive file search', default=False)
    parser.add_argument('--skip_duplicates', action='store_true', help='verbose', default=False)

    args = parser.parse_args()
    file_list = []

    if args.input_dir != "":
        path = os.path.abspath(args.input_dir)
        if not os.path.isdir(path):
            print("is not a directory %s" % path)
            exit_failure()
        else:
            file_list = get_files_with_ext(path, args.ext, args.verbose, not (args.no_recursive))
    else:
        print('no input_dir specified!')
        exit_failure()

    if args.output_dir == "":
        args.output_dir = args.input_dir
    else:
        path = os.path.abspath(args.output_dir)
        if not os.path.exists(path):
            os.makedirs(path)
            print("directory created: %s" % path)

    output_dir_root = os.path.abspath(args.output_dir)

    total_cnt = 0
    total_skipped = 0
    total_error = 0
    for file_orig in tqdm(file_list, unit="files"):
        datetime_object, success = get_datatime_object_from_file(file_orig)
        if not success:
            total_error += 1
            print("failure at: %s" % file_orig)
            continue

        datetime_str = datetime_object.strftime('%Y%m%d_%H%M%S')

        path = output_dir_root
        if args.create_tree:
            path = path + "/" + datetime_object.strftime("%Y") + "/" + datetime_object.strftime("%m")
            if not os.path.exists(path):
                os.makedirs(path)
                if args.verbose:
                    print("directory created: %s" % path)

        # Add a prefix or take original basename:
        if args.prefix != '':
            prefix = args.prefix
        else:
            basename = os.path.basename(file_orig)  # os independent
            filename, file_extension = os.path.splitext(basename)
            prefix = filename

        # create new filename and check if it already exists:
        new_name = prefix + "_" + datetime_str + ".jpg"
        file_new = os.path.join(path, new_name)

        number = 0
        while os.path.exists(file_new):
            number += 1
            new_name = prefix + "_" + str(number) + "_" + datetime_str + ".jpg"
            file_new = os.path.join(path, new_name)

        # skip duplicates or convert the file:
        if number > 0 and args.skip_duplicates:
            total_skipped += 1
            if args.verbose:
                print("Skip \n\t-src:" + file_orig + " \n\t-dest: " + file_new)
        else:
            # run the bash command:  sudo apt install libheif-examples
            args2 = ['heif-convert', '-q 100 ', file_orig, file_new]
            subprocess.Popen(args2)

            # change the modified timestamp of the new file based on the old files timestamp!
            creation_time = os.path.getmtime(file_orig)
            os.utime(file_new, (creation_time, creation_time))

            total_cnt += 1
            if args.verbose:
                print("converting \n\t-src:" + file_orig + " \n\t-dest: " + file_new)

    print("total copied files: %s" % total_cnt)
    print("total skipped files: %s" % total_skipped)
    print("total error files: %s" % total_error)
    exit_success()
