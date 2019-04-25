from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from flask import Flask, jsonify
from zipfile import ZipFile
import matplotlib.image as mpimg
import requests
import base64
import os

app = Flask(__name__)
address = "http://localhost:5000"


def window_layout():
    global o_img, p_img
    o_img = None
    p_img = None

    def get_user_metric():
        user_name = id_entry.get()
        if user_name == '':
            messagebox.showinfo('Error', 'Please enter your user name.')
        # r = requests.get()
        # user_metric = r.json()
        return None

    def select_file():
        file_name = fd.askopenfilename()
        if file_name != '':
            selected_label.config(text='{}'.format(file_name))
        return None

    def select_request():
        user_name = id_entry.get()
        r = requests.get(address + "/api/previous_request/" +
                                   user_name)
        pre_request = r.json()
        if type(pre_request) == dict:
            open_req_cb['value'] = pre_request
        else:
            messagebox.showinfo('Error', pre_request)
        return None

    def unzip_encode_img():
        file_name = selected_label.cget('text')
        file_format = file_name.split(".")[-1]
        if file_format != 'zip':
            img_num = 1
            with open(file_name, "rb") as image_file:
                img_b64b = base64.b64encode(image_file.read())
            img = str(img_b64b, encoding='utf-8')
            print(img)
        else:
            img = []
            with ZipFile(file_name, 'r') as zip_file:
                file_list = zip_file.namelist()
            img_num = len(file_list)
            for i in range(img_num):
                with open(file_name, "rb") as image_file:
                    img_b64b = base64.b64encode(image_file.read())
                img.append(str(img_b64b, encoding='utf-8'))
        return img_num, file_format, img

    def show_time(r_dict):
        # show only the info for the first image if a bunch is uploaded
        t_upload = r_dict['Time upload'][0]
        t_process = r_dict['Time to process'][0]
        img_size = r_dict['Image size'][0]
        t_up_label.config(text='Time uploaded: {}'.format(t_upload))
        t_pr_label.config(text='Time to process: {}'.format(t_process))
        img_size_label.config(text='Image size: {}*{}'.format(img_size[0],
                                                              img_size[1]))

    def show_hist(r_dict):
        o_hist = r_dict['Original histogram'][0]
        p_hist = r_dict['Processed histogram'][0]
        o_hist_label.config(image=o_hist)
        p_hist_label.config(image=p_hist)

    def start_p():
        global o_img, p_img
        img_num, file_format, img = unzip_encode_img()
        p_dict = {'filename': selected_label.cget('text'),
                  'imgs': img,
                  'username': id_entry.get(),
                  'num_img': img_num,
                  'procedure': p_method,
                  'img_format': file_format}
        r = requests.post(address + "/api/process_img", json=jsonify(p_dict))
        result = r.json()
        if type(result) == dict:
            show_time(result)
            show_hist(result)
            o_img = result['Original image']
            p_img = result['Processed image']
        else:
            messagebox.showinfo('Error', result)
        return None

    def combo_callback(self):
        global o_img, p_img
        request_name = open_req_cb.get()
        selected_label.config(text='{}'.format(request_name))
        p_dict = {['request_number']: selected_label.cget('text'),
                  ['user_name']: id_entry.get()}
        r = requests.post("http://example.com/", json=jsonify(p_dict))
        result = r.json()
        show_time(result)
        show_hist(result)
        o_img = result['Original image']
        p_img = result['Processed image']
        return None

    def display_img():
        pass

    def download_image(dl_format):
        pass
        '''global p_img
        os.mkdir('./Img')
        download_path = r'./Img'
        img_num = len(p_img)
        if img_num > 1:
            os.mkdir('./temp/')
            file_path = r'./temp/'
            zip_file = ZipFile(download_path, 'w')
            for i in range(img_num):
                with open("./temp/Img{}.{}".format(i, dl_format), "wb") as \
                        download_img:
                    download_img.write()
                zip_file.write(file_path, "Img{}.{}".format(i, dl_format))
            zip_file.close()
            os.remove(file_path)
        else:
            with open("./temp/Img.{}".format(dl_format), "wb") as download_img:
                download_img.write()'''

    root = Tk()
    root.title('BME547 - Image Processing')

    # User ID input
    row_1 = 0
    id_label = ttk.Label(root, text='1. Please enter your name')
    id_label.grid(column=0, row=row_1)
    id_entry = ttk.Entry(root)
    id_entry.grid(column=1, row=row_1)
    user_info_btn = ttk.Button(root, text='Get my processing history',
                               command=get_user_metric)
    user_info_btn.grid(column=2, row=row_1)

    # Select action
    row_2 = row_1 + 1
    req_option = StringVar()
    action_label = ttk.Label(root, text='2. Please select an action')
    action_label.grid(column=0, row=row_2, sticky=W)
    new_file_btn = ttk.Button(root, text='Upload a new file',
                              command=select_file)
    new_file_btn.grid(column=0, row=row_2+1, sticky=W)
    open_req_btn = ttk.Button(root, text='View a previous request',
                              command=select_request)
    open_req_btn.grid(column=1, row=row_2+1, sticky=W)
    open_req_cb = ttk.Combobox(root, textvariable=req_option)
    open_req_cb.bind("<<ComboboxSelected>>", combo_callback)
    open_req_cb.grid(column=2, row=row_2+1)
    selected_label = ttk.Label(root, text='None file or request selected')
    selected_label.grid(column=0, row=row_2+2, columnspan=5, sticky=W)

    # Choose process
    row_3 = row_2 + 3
    process_label = ttk.Label(root, text='3. Please choose the procedure')
    process_label.grid(column=0, row=row_3, columnspan=2, sticky=W)
    p_method = StringVar()
    p_method.set('histogram_eq')
    p_h_btn = ttk.Radiobutton(root, text='Histogram Equalization',
                              variable=p_method, value='histogram_eq')
    p_h_btn.grid(column=0, row=row_3+1)
    p_c_btn = ttk.Radiobutton(root, text='Contrast Stretching',
                              variable=p_method, value='contrast_str')
    p_c_btn.grid(column=1, row=row_3+1)
    p_l_btn = ttk.Radiobutton(root, text='Log Compression', variable=p_method,
                              value='log_compress')
    p_l_btn.grid(column=2, row=row_3+1)
    p_r_btn = ttk.Radiobutton(root, text='Reverse Video', variable=p_method,
                              value='reverse_vid')
    p_r_btn.grid(column=3, row=row_3+1)
    start_btn = ttk.Button(root, text='Start Processing', command=start_p)
    start_btn.grid(column=4, row=row_3+1)

    # Show results
    row_4 = row_3 + 2
    result_label = ttk.Label(root, text='4. Result')
    result_label.grid(column=0, row=row_4, sticky=W)

    t_up_label = ttk.Label(root, text='Time uploaded:')
    t_up_label.grid(column=0, row=row_4+1, columnspan=2, sticky=W)
    t_pr_label = ttk.Label(root, text='Time to process:')
    t_pr_label.grid(column=2, row=row_4+1, columnspan=2, sticky=W)
    img_size_label = ttk.Label(root, text='Image size:')
    img_size_label.grid(column=4, row=row_4+1, columnspan=2, sticky=W)
    histimg = PhotoImage('IMG_2051.gif')
    o_hist_label = ttk.Label(root, text='Original Histogram', image=histimg,
                             compound='center')
    o_hist_label.grid(column=0, row=row_4+2, columnspan=2, rowspan=2)
    p_hist_label = ttk.Label(root, text='Processed Histogram', image=None)
    p_hist_label.grid(column=2, row=row_4+2, columnspan=2, rowspan=2)
    disp_btn = ttk.Button(root, text='Display and compare', command=display_img)
    disp_btn.grid(column=4, row=row_4+3)

    # Download choices
    row_5 = row_4 + 4
    download_label = ttk.Label(root, text='5. Download image(s)')
    download_label.grid(column=0, row=row_5, sticky=W)

    d_format = StringVar()
    d_format.set('jpg')
    jpg_btn = ttk.Radiobutton(root, text='JPG', variable=d_format, value='jpg')
    jpg_btn.grid(column=0, row=row_5+1, sticky=W)
    jpeg_btn = ttk.Radiobutton(root, text='JPEG', variable=d_format,
                               value='jpeg')
    jpeg_btn.grid(column=1, row=row_5+1, sticky=W)
    png_btn = ttk.Radiobutton(root, text='PNG', variable=d_format, value='png')
    png_btn.grid(column=2, row=row_5+1, sticky=W)
    tiff_btn = ttk.Radiobutton(root, text='TIFF', variable=d_format,
                               value='tiff')
    tiff_btn.grid(column=3, row=row_5+1, sticky=W)

    d_btn = ttk.Button(root, text='Download', command=download_image(
        d_format))
    d_btn.grid(column=4, row=row_5+1)

    root.mainloop()
    return


if __name__ == "__main__":
    # window_layout()
    pass
