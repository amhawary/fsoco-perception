#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#      Author = "Namik Delilovic"
#      Contact = "namikdelilovic@gmail.com"
#      License = "GPLv3"
#      Version = "0.9"
#      Date = "2019/10/09"

import glob
import json
import optparse
import os
import shutil
from shutil import copyfile
import typing

import yaml
from sklearn.model_selection import train_test_split

y2s_flag = "y2s"
s2y_flag = "s2y"


class S2Y:
    @staticmethod
    def get_class_names_from_supervisely(input_path: str) -> typing.List:
        """
        Get class names from meta.json file.
        :param input_path: path of Supervise.ly dataset folder
        :return: list of all classes used in Supervise.ly dataset
        """
        class_names_array = []
        class_names_path = os.path.join(input_path, 'meta.json')
        with open(class_names_path, "r") as file:
            json_classes = json.load(file)["classes"]
            for json_class in json_classes:
                class_names_array.append(json_class["title"])
        return class_names_array

    @staticmethod
    def create_yolo_file_structure(output_path: str) -> None:
        """
        Create the folder hierarchy to welcome the images and the label files. The YOLO dataset structure can be found
        in the ReadME.md
        :param output_path: absolute path of YOLO dataset
        """
        for step in ["train", "val"]:
            os.makedirs(os.path.join(output_path, step, 'labels'), exist_ok=True)
            os.makedirs(os.path.join(output_path, step, 'images'), exist_ok=True)

    @staticmethod
    def create_class_file(class_names_array, output_path) -> None:
        class_file_path = os.path.join(output_path, 'labels', 'classes.txt')
        with open(class_file_path, 'w') as f:
            for class_name in class_names_array:
                f.write("%s\n" % class_name)

    @staticmethod
    def create_data_file(class_name_list: typing.List, output_path: str) -> None:
        """
        Create YOLO .yaml data file which is a yaml file gathering several dataset information:
        - train images folder
        - val images folder
        - test images' folder (currently not used in this project)
        - number of object classes
        - object class names
        :param class_name_list: list of all object classes used in the Supervise.ly input dataset
        :param output_path: Path of YOLO project
        """
        class_file_path = os.path.join(output_path, 'data.yaml')
        dict_yaml = {"train": "train/images",
                     "val": "val/images",
                     "nc": len(class_name_list),
                     "names": class_name_list}

        with open(class_file_path, 'w') as outfile:
            yaml.dump(dict_yaml, outfile, default_flow_style=False)

    @staticmethod
    def get_yolo_annotation_info(json_file: str, class_names_array: typing.List) -> typing.List:
        with open(json_file, "r") as file:
            json_object = json.load(file)

        class_coord_list = []

        class_id = 0
        if len(json_object["objects"]) > 0:

            for obj in json_object["objects"]:
                points = obj["points"]["exterior"]
                w = json_object["size"]["width"]
                h = json_object["size"]["height"]
                w_point = points[1][0] - points[0][0]
                h_point = points[1][1] - points[0][1]
                x1 = round((points[0][0] + w_point / 2) / w, 5)
                y1 = round((points[0][1] + h_point / 2) / h, 5)
                x2 = round(w_point / w, 5)
                y2 = round(h_point / h, 5)
                class_id = class_names_array.index(obj["classTitle"])

                class_coord_list.append({"class_id": class_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2})

        return class_coord_list  # class_id, x1, y1, x2, y2

    @staticmethod
    def create_text_file(output_folder: str, y_file: str, class_names_array: typing.List) -> None:
        """
        Write a YOLO txt file corresponding to Supervise.ly annotation json file.
        :param output_folder: Outout folder where YOLO dataset will lie.
        :param y_file: absolute path of the Supervise.ly json annotation file.
        :param class_names_array: list of all object classes in Supervise.ly the dataset.
        """
        # class_id, x1, y1, x2, y2 = S2Y.get_yolo_annotation_info(folder_name, file_name, class_names_array)
        class_coord_list = S2Y.get_yolo_annotation_info(json_file=y_file, class_names_array=class_names_array)

        if len(class_coord_list) > 0:

            txt_path = os.path.join(output_folder, "labels", os.path.basename(y_file)[:-9] + ".txt")

            with open(txt_path, 'w') as text_file:
                for coord in class_coord_list:
                    class_id = coord["class_id"]
                    x1 = coord["x1"]
                    y1 = coord["y1"]
                    x2 = coord["x2"]
                    y2 = coord["y2"]

                    text_file.write('{} {} {} {} {}'.format(class_id, x1, y1, x2, y2))
                    text_file.write('\n')


class Y2S:
    @staticmethod
    def create_supervisely_file_structure(input_path):
        os.makedirs(os.path.dirname(input_path + '//dataset_1//ann//'), exist_ok=True)
        os.makedirs(os.path.dirname(input_path + '//dataset_1//img//'), exist_ok=True)

    @staticmethod
    def get_class_names_from_yolo(output_path: str):
        class_names_path = output_path + '//labels//classes.txt'
        with open(class_names_path) as file:
            class_names_array = file.read().splitlines()
        return class_names_array

    @staticmethod
    def get_supervisely_annotation_info(file_name, output_path=None, skip_copy=None, input_path=None):
        for image_path in glob.glob(os.path.join(output_path + "//images//", file_name + '.*')):
            pass

        if not skip_copy:
            copy_path = input_path + '//dataset_1//img//' + os.path.basename(image_path)
            copyfile(image_path, copy_path)

        image = cv2.imread(image_path, 0)
        h, w = image.shape[:2]
        class_coord_list = []

        image_text_file = output_path + '//labels//' + file_name + '.txt'

        with open(image_text_file) as file:
            # read all labels, split by line and add to list
            all_labels = file.read().splitlines()

            for data in [x.split() for x in all_labels]:
                class_id = int(data[0])
                bbox_width = float(data[3]) * w
                bbox_height = float(data[4]) * h
                center_x = float(data[1]) * w
                center_y = float(data[2]) * h
                x1 = int(center_x - (bbox_width / 2))
                y1 = int(center_y - (bbox_height / 2))
                x2 = int(center_x + (bbox_width / 2))
                y2 = int(center_y + (bbox_height / 2))
                class_coord_list.append({"class_id": class_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2})

        return w, h, class_coord_list

    @staticmethod
    def create_meta_file(class_names_array, input_path):
        classes_array = []
        for name in class_names_array:
            classes_array.append({"title": name, "shape": "rectangle", "color": "#FF0000"})

        meta_format = {
            "tags": [],
            "classes": classes_array
        }

        meta_file_path = input_path + '//meta.json'
        with open(meta_file_path, 'w') as json_file:
            json.dump(meta_format, json_file)

    @staticmethod
    def create_json_file(file_name: str, class_names_array: typing.List, input_path: str, output_path: str,
                         skip_copy: bool) -> str:
        w, h, class_coord_list = Y2S.get_supervisely_annotation_info(file_name, output_path, skip_copy, input_path)

        json_format = {
            "description": "",
            "name": file_name,
            "size": {
                "width": w,
                "height": h
            },
            "tags": [],
            "objects": [
            ]
        }

        for class_coord in class_coord_list:
            json_format["objects"].append({
                "description": "",
                "tags": [],
                "bitmap": None,
                "classTitle": class_names_array[class_coord['class_id']],
                "points": {
                    "exterior": [
                        [
                            class_coord['x1'],
                            class_coord['y1']
                        ],
                        [
                            class_coord['x2'],
                            class_coord['y2']
                        ]
                    ],
                    "interior": []
                }
            })

        json_file_path = input_path + '//dataset_1//ann//' + file_name + '.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(json_format, json_file)


def img_path_from_label(y_path: str) -> str:
    """
    Get image absolute path from corresponding annotation file path.
    Transform 'img' folder to 'ann' folder in the absolute path
    :param y_path:
    :return:
    """
    head, tail = os.path.split(y_path)
    x_name = tail[:-5]
    list_path = head.split(os.sep)
    list_path[-1] = 'img'
    list_path.append(x_name)
    return os.path.join(*list_path)


def img_set_from_labels(annotation_files: typing.List) -> typing.List:
    """
    Get image set from label set thanks to the annotation path. Label set is made up of json annotation full paths.
    :param annotation_files: list of annotations files which compose the label set
    :return: Image set with absolute path of each picture in the set.
    """
    X = []
    for ann_file in annotation_files:
        X.append(img_path_from_label(y_path=ann_file))
    return X

def main(dest_path: str, input_path: str, skip_copy: bool, conversion_type: str, val_size: float, test_size: float) -> None:
    """
    Main function which enables the possibility to pass from YOLO dataset to Supervise.ly dataset and inversely.
    :param dest_path: Output folder path
    :param input_path: Input folder path
    :param skip_copy: *not used for the moment*
    :param conversion_type: type of conversion, could be Supervise.ly to YOLO or YOLO to Supervise.ly
    :param val_size: proportion of the dataset to use for validation
    :param test_size: proportion of the dataset to use for testing
    """

    print("Processing...")
    if conversion_type == y2s_flag:
        ...
        # No changes needed in y2s conversion
    else:
        try:
            class_names_array = S2Y.get_class_names_from_supervisely(input_path=input_path)
        except IOError:
            print('Error [meta.json not found]')
            exit(1)

        # Create structure including 'test'
        for split in ["train", "val", "test"]:
            os.makedirs(os.path.join(dest_path, split, 'labels'), exist_ok=True)
            os.makedirs(os.path.join(dest_path, split, 'images'), exist_ok=True)

        # Save data.yaml with test key
        class_file_path = os.path.join(dest_path, 'data.yaml')
        dict_yaml = {
            "train": "train/images",
            "val": "val/images",
            "test": "test/images",
            "nc": len(class_names_array),
            "names": class_names_array
        }
        with open(class_file_path, 'w') as outfile:
            yaml.dump(dict_yaml, outfile, default_flow_style=False)

        # Collect all annotation files
        dataset_folders = [folder for folder in os.listdir(input_path)]
        y = []
        for folder in dataset_folders:
            labels_path = os.path.join(input_path, folder, "ann")
            for file_path in glob.glob(os.path.join(labels_path, '*.json')):
                y.append(file_path)

        X = img_set_from_labels(y)

        # Split into train, val, test
        X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
        val_ratio = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=val_ratio, random_state=42)

        def process_subset(X_subset, y_subset, split_name):
            for x_path, y_path in zip(X_subset, y_subset):
                img_dest = os.path.join(dest_path, split_name, 'images', os.path.basename(x_path))
                lbl_dest_folder = os.path.join(dest_path, split_name, 'labels')
                os.makedirs(lbl_dest_folder, exist_ok=True)
                copyfile(x_path, img_dest)
                S2Y.create_text_file(output_folder=os.path.join(dest_path, split_name),
                                     y_file=y_path,
                                     class_names_array=class_names_array)

        process_subset(X_train, y_train, "train")
        process_subset(X_val, y_val, "val")
        process_subset(X_test, y_test, "test")

        print("YOLO structure with train/val/test created at => {}".format(dest_path))

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-p', '--dest_path',
                      action="store", dest="dest_path",
                      help="full path of the output folder")

    parser.add_option('-i', '--input_path', dest="input_path",
                      help="full path of the source folder (default path is the location of this script)",
                      default=os.path.dirname(os.path.realpath(__file__)))

    parser.add_option('-s', '--skip',
                      action="store_true", dest="skip_copy",
                      help="disable copying images from the source folder to the destination folder",
                      default=False)

    parser.add_option('-t', '--type',
                      type='choice',
                      choices=[y2s_flag, s2y_flag],
                      action="store",
                      dest="conversion_type",
                      help="conversion type: yolo2supervisely or supervisely2yolo (default supervisely2yolo)",
                      default=s2y_flag)

    parser.add_option('--test_size',
                      dest="test_size", type=float,
                      help="Represent the proportion of the dataset to include in the test split",
                      default=0.15)

    options, args = parser.parse_args()


    input_path = "supervisely/"  # where 'meta.json' is
    output_path = "dataset02"
    conversion_type = "s2y"  # use "s2y" for Supervise.ly → YOLO, or "y2s" for reverse
    skip_copy = False
    val_size = 0.1
    test_size = 0.1

    main(dest_path=output_path, input_path=input_path, skip_copy=skip_copy, conversion_type=conversion_type, val_size=val_size, test_size=test_size)

