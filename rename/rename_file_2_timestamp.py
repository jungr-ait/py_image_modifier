#!/usr/bin/env python
# Software License Agreement (GNU GPLv3  License)
#
# Copyright (c) 2019, Roland Jung (rolandjung0@gmail.com)
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
from PIL import Image
from PIL.ExifTags import TAGS
import shutil
from tqdm import tqdm
from datetime import datetime
from datetime import date
from datetime import timedelta


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


# --input_dir ../test/rename_in --output_dir ../test/rename_out --ext jpg --prefix bla --verbose --no_recursive --add_hours -24 --skip_duplicates  --create_tree
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Renaming all files from the input_dir by file creation data and stored in output_dir:\n usage: --input_dir ../test/rename_in --output_dir ../test/rename_out --ext JPG --prefix bla --verbose --add_hours 123')
    parser.add_argument('--input_dir', help='directory with images', default="")
    parser.add_argument('--output_dir', help='directory for renamed images', default="")
    parser.add_argument('--prefix', help='prefix to the final image name: <prefix><data>.<ext>', default='IMG')
    parser.add_argument('--ext', help='file extension', default='jpg')
    parser.add_argument('--verbose', action='store_true', help='verbose', default=False)
    parser.add_argument('--create_tree', action='store_true', help='create date folder tree', default=False)
    parser.add_argument('--no_recursive', action='store_true', help='no recursive file search', default=False)
    parser.add_argument('--add_seconds', help='adds <N> seconds to the timestamps', type=int, default=0)
    parser.add_argument('--add_minutes', help='adds <N> minutes to the timestamps', type=int, default=0)
    parser.add_argument('--add_hours', help='adds <N> hours to the timestamps', type=int, default=0)
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

        datetime_object = datetime_object + timedelta(hours=args.add_hours, minutes=args.add_minutes,
                                                      seconds=args.add_seconds)
        datetime_str = datetime_object.strftime('%Y%m%d_%H%M%S')

        new_name = args.prefix + "_" + datetime_str + "." + args.ext

        path = output_dir_root
        if args.create_tree:
            datetime_path_str = datetime_object.strftime("%Y/%m/")
            path = path + "/" + datetime_path_str
            if not os.path.exists(path):
                os.makedirs(path)
                if args.verbose:
                    print("directory created: %s" % path)

        file_new = os.path.join(path, new_name)

        number = 0
        while os.path.exists(file_new):
            number += 1
            new_name = args.prefix + "_" + datetime_str + "_" + str(number) + "." + args.ext
            file_new = os.path.join(args.output_dir, new_name)

        if number > 0 and args.skip_duplicates:
            total_skipped += 1
            if args.verbose:
                print("Skip \n\t-src:" + file_orig + " \n\t-dest: " + file_new)
        else:
            dest = shutil.copy(file_orig, file_new)
            total_cnt += 1
            if args.verbose:
                print("Copy \n\t-src:" + file_orig + " \n\t-dest: " + file_new)

    print("total copied files: %s" % total_cnt)
    print("total skipped files: %s" % total_skipped)
    print("total error files: %s" % total_error)
    exit_success()
