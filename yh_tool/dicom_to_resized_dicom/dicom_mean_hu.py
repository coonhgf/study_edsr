#-*- coding: utf-8 -*-
import sys
import os
import numpy as np
import shutil
import traceback
import hashlib
import time
import datetime
import tarfile
import hashlib
#import SimpleITK as sitk
import pandas
from PIL import Image

###
#import pydicom
from pydicom import dcmread
from scipy.ndimage.interpolation import zoom
import shutil
from collections import Counter


def csv_mapping_get_seri_id_by_folder_name(csv_fp, folder_name):
    #
    # [y] read name mapping csv
    # format of csv : (shorter_id, seri_id, pat_id)
    #
    np_mapping = np.array(pandas.read_csv(csv_fp))
    got_seri_id = None
    
    for idx in range(np_mapping.shape[0]):
        # [y] if each row starting of #, skip this line
        the_row_string_col0 = str(np_mapping[idx][0])
        if "#" in the_row_string_col0:
            continue
        
        if str(np_mapping[idx][2]).strip() == folder_name:
            got_seri_id = np_mapping[idx][1]
            break
        
    if got_seri_id == None:
        return -1, got_seri_id
    else:
        return 0, got_seri_id


def clear_dir(the_dp):
    for filename in os.listdir(the_dp):
        file_path = os.path.join(the_dp, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            retm = traceback.format_exc()
            print(retm)
            return -1, retm
    return 0, ""


def create_dir(the_dp):
    try:
        os.makedirs(the_dp, exist_ok=True)
    except:
        retm = traceback.format_exc()
        print(retm)
        return -1, retm
    return 0, ""


def apply_lung_window(np_hu_img):
    set_lung_window = np.array([-1200.0, 600.0])  # [y] from hu to hu, not (window_center, window_length)
    np_lw_img = (np_hu_img-set_lung_window[0]) / (set_lung_window[1]-set_lung_window[0])
    np_lw_img[np_lw_img < 0]=0
    np_lw_img[np_lw_img > 1]=1
    np_lw_img = (np_lw_img*255).astype('uint8')
    return 0, np_lw_img


if __name__ == '__main__':
    print("calc hu mean start!")
    #
    # read dicom by seri_id(will need csv mapping file), 
    # => save each slice dicom to png, filename will be folder_name__4digits_number.png, as HighResolution
    # => resize X2(i.e. 512 to 256), as LowResolution X2
    #
    
    #
    # setting, usually fix
    #
    
    #
    # setting, usually modified
    #
    src_dcm_root_dp = "/media/sdc1/home/yh_dataset/edsr/yh_edsr_csh_axial/original/train"
    src_dcm_folder_by_file_fp = "/media/sdc1/home/yh_dataset/edsr/tool_txt/copy_folder_by_file__210707_train.txt"  # [y] txt檔案, 裡面每一行表示一個folder name
    
    #
    # auto set
    #
    list_src_dcm_folder = []
    with open(src_dcm_folder_by_file_fp, "r") as infile:
        for a_line in infile:
            content = a_line.strip()
            list_src_dcm_folder.append(content)
            
            
    #
    # checking
    #
    # check each folder exist
    not_exist_folder = []
    for a_folder in list_src_dcm_folder:
        tmp_dp = os.path.join(src_dcm_root_dp, a_folder)
        if not os.path.isdir(tmp_dp):
            not_exist_folder.append(a_folder)
    if len(not_exist_folder) >= 1:
        print("src folder not exist:{0}".format(not_exist_folder))
        exit(1)
    
           
    #
    # main process
    #
    
    # read each dicom folder's dicom and convert to png
    # png naming is FolderName___001.png etc.
    mean_per_scan = []  # a list
    mean_per_slice = []  # list of list
    hu_max_exception_cnt = 0
    hu_min_exception_cnt = 0
    list_hu_min = []  # -1025 start add to list
    list_hu_max = []  # 3072 start add to list
    for a_dcm_fd in list_src_dcm_folder:
        print("processing : {0}".format(a_dcm_fd))
        tmp_src_dp = os.path.join(src_dcm_root_dp, a_dcm_fd)
        
        # list files in this folder
        list_filename = []
        for tmp_fn in os.listdir(tmp_src_dp):
            tmp = os.path.join(tmp_src_dp, tmp_fn)
            if os.path.isfile(tmp):
                list_filename.append(tmp_fn)
        list_filename.sort()
        
        # process
        tmp_mean_slice = []
        tmp_rec_min_fn = []
        for sidx, tmp_dcm_fn in enumerate(list_filename):
            tmp_dcm_fp = os.path.join(tmp_src_dp, tmp_dcm_fn)
            #print("now dcm fp : {0}".format(tmp_dcm_fp))
            
            # HR
            # read hu and calc mean
            dcm_data = dcmread(tmp_dcm_fp)
            dcm_img = dcm_data.pixel_array.astype(np.float64)
            
            # calc mean of this slice
            a_mean_of_slice = np.mean(dcm_img)
            tmp_mean_slice.append(a_mean_of_slice)
            tmp_max_val = np.max(dcm_img)
            tmp_min_val = np.min(dcm_img)
            if tmp_max_val > 3071.0:
                hu_max_exception_cnt += 1
                list_hu_max.append(tmp_max_val)
            if tmp_min_val < -1024.0:
                hu_min_exception_cnt += 1
                list_hu_min.append(tmp_min_val)
                tmp_rec_min_fn.append(tmp_dcm_fn)
        
        
        # save the number
        mean_per_slice.append(tmp_mean_slice)
        a_mean_of_scan = sum(tmp_mean_slice)/len(tmp_mean_slice)
        mean_per_scan.append(a_mean_of_scan)
    
    ### debug
    print("tmp_rec_min_fn={0}".format(tmp_rec_min_fn))
    
        
    # calc all scan's mean and show
    a_mean_of_all = sum(mean_per_scan)/len(mean_per_scan)
    
    print("mean_per_scan={0}".format(mean_per_scan))
    print("len of mean_per_scan={0}".format(len(mean_per_scan)))
    print("a_mean_of_all={0}".format(a_mean_of_all))
    print("")
    
    # shift from -1024~3071 to 0~4095
    ###print("shift hu from -1024~3071 to 0~4095")
    # =>
    print("assume hu range is -2048~3071, now shift to 0~5119")
    mean_with_shift = a_mean_of_all + 2048
    norm_mean_with_shift = mean_with_shift / 5119
    print("mean_with_shift={0}".format(mean_with_shift))
    print("norm_mean_with_shift={0}".format(norm_mean_with_shift))
    print("")
    
    # hu value exception checking
    dict_hu_max_counter = Counter(list_hu_max)
    dict_hu_min_counter = Counter(list_hu_min)
    cvt_sorted_list_hu_max = sorted(dict_hu_max_counter.items(), key=lambda x:x[1], reverse=True)
    cvt_sorted_list_hu_min = sorted(dict_hu_min_counter.items(), key=lambda x:x[1], reverse=True)
    print("hu_max_exception_cnt={0}".format(hu_max_exception_cnt))
    print("hu_min_exception_cnt={0}".format(hu_min_exception_cnt))
    print("top 10 of cvt_sorted_list_hu_max=\n{0}".format(cvt_sorted_list_hu_max[0:10]))
    print("top 10 of cvt_sorted_list_hu_min=\n{0}".format(cvt_sorted_list_hu_min[0:10]))
    print("")
    
    print("calc hu mean end")