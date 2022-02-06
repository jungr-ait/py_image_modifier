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


def get_exif(fn):
    exif = {}
    error = True
    success = False
    try:
        i = Image.open(fn)
        info = i._getexif()
        if info != None:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif[decoded] = value

            return exif, False, True
        else:
            return None, False, False
    except:
        return None, True, False


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)


def get_datatime_object_from_image(fn):
    ret, error, success = get_exif(fn)

    if error:
        return None, False

    if success:
        if "DateTimeOriginal" in ret:
            datetime_str = ret["DateTimeOriginal"]
            try:
                datetime_object = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                return datetime_object, True
            except:
                return None, False

        elif "DateTime" in ret:
            datetime_str = ret["DateTime"]
            try:
                datetime_object = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                return datetime_object, True
            except:
                return None, False

    try:  # try the modification timestamp:
        # mtime = creation_date(fn)
        datetime_object = datetime.fromtimestamp(os.path.getmtime(fn))
        # print("last modified: %s" % time.ctime(datetime_object))
        return datetime_object, True
    except:
        return None, False


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


# --input_dir ../test/rename_in --output_dir ../test/rename_out --ext jpg --prefix bla --verbose --no_recursive --add_hours -24 --skip_duplicates  --create_tree
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Renaming all images from the input_dir by file timestamp and stored in output_dir:\n usage: --input_dir ../test/rename_in --output_dir ../test/rename_out --ext JPG --prefix bla --verbose --add_hours 123')
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
    for file_orig in tqdm(file_list, unit="imgs"):
        datetime_object, success = get_datatime_object_from_image(file_orig)
        if not success:
            total_error += 1
            print("failure at: %s" % file_orig)
            continue

        datetime_object = datetime_object + timedelta(hours=args.add_hours, minutes=args.add_minutes,
                                                      seconds=args.add_seconds)
        datetime_str = datetime_object.strftime('%Y%m%d_%H%M%S')

        path = output_dir_root
        if args.create_tree:
            datetime_path_str = datetime_object.strftime("%Y/%m/")
            path = path + "/" + datetime_path_str
            if not os.path.exists(path):
                os.makedirs(path)
                if args.verbose:
                    print("directory created: %s" % path)

        new_name = args.prefix + "_" + datetime_str + "." + args.ext
        file_new = os.path.join(path, new_name)

        number = 0
        while os.path.exists(file_new):
            number += 1
            new_name = args.prefix + "_" + str(number) + "_" + datetime_str + "." + args.ext
            file_new = os.path.join(args.output_dir, new_name)

        if number > 0 and args.skip_duplicates:
            total_skipped += 1
            if args.verbose:
                print("Skip \n\t-src:" + file_orig + " \n\t-dest: " + file_new)
        else:
            if args.verbose:
              print("Copy \n\t-src:" + file_orig + " \n\t-dest: " + file_new)
              
            dest = shutil.copy(file_orig, file_new)

            # change the modified timestamp of the new file based on the old files timestamp!
            creation_time = os.path.getmtime(file_orig)
            os.utime(file_new, (creation_time, creation_time))
            total_cnt += 1


    print("total copied files: %s" % total_cnt)
    print("total skipped files: %s" % total_skipped)
    print("total error files: %s" % total_error)
    exit_success()
