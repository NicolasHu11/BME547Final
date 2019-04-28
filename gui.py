from tkinter import *
from tkinter import ttk, messagebox
from tkinter import filedialog as fd
from flask import Flask
from zipfile import ZipFile
from PIL import Image, ImageTk
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib import figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, \
    NavigationToolbar2Tk
import matplotlib.pyplot as plt
import matplotlib as mpl
# import matplotlib.backends.tkagg as tkagg
import requests
import base64
import io
import os


app = Flask(__name__)
address = "http://localhost:5000"


def window_layout():
    global o_img, p_img, file_upload
    o_img = None
    p_img = None

    def get_user_metric():
        user_name = id_entry.get()
        if user_name == '':
            messagebox.showinfo('Error', 'Please enter your user name.')
            return
        r = requests.get(address + "/api/user_metrics/" + user_name)
        user_metric, info_n = r.json()
        if info_n == 200:
            t = user_metric['user_creation_time']
            n = user_metric['num_actions']
            messagebox.showinfo('Your Info', 'Time you created account:{} \n '
                                             'Total actions: {}'.format(t, n))
        else:
            messagebox.showinfo('Error', user_metric)
        return None

    def select_file():
        global file_upload
        file_upload = list(fd.askopenfilenames())
        if file_upload:
            if len(file_upload) == 1:
                selected_label.config(text='{}'.format(file_upload[0]))
            else:
                selected_label.config(text='{} ...'.format(file_upload[0]))
        return None

    def select_request():
        user_name = id_entry.get()
        if user_name == '':
            messagebox.showinfo('Error', 'Please enter your user name.')
            return
        r = requests.get(address + "/api/previous_request/" + user_name)
        pre_req = r.json()
        if type(pre_req) == dict:
            num_req = len(pre_req)
            req_keys = []
            for i in range(num_req):
                f_n = pre_req[i]['filename']
                t_u = pre_req[i]['time_uploaded']
                p = pre_req[i]['procedure']
                k = str(i) + ':' + f_n + t_u + p
                req_keys.append(k)
            open_req_cb['value'] = req_keys
        else:
            messagebox.showinfo('Error', pre_req)
        return None

    def unzip_encode_img():
        global file_upload
        file_format = file_upload[0].split('.')[-1]
        img = []
        if file_format != 'zip':
            img_num = len(file_upload)
            for i in range(img_num):
                with open(file_upload[0], 'rb') as image_file:
                    img_b64b = base64.b64encode(image_file.read())
                img.append(str(img_b64b, encoding='utf-8'))
        else:
            with ZipFile(file_upload[0], 'r') as zip_file:
                file_list = zip_file.namelist()
            img_num = len(file_list)
            for i in range(1, img_num):
                file_name = file_upload[0].replace('.zip', '') + '/' + \
                            file_list[i].split('/')[-1]
                print(file_name)
                file_format = file_name.split('.')[-1]
                with open(file_name, 'rb') as image_file:
                    img_b64b = base64.b64encode(image_file.read())
                img.append(str(img_b64b, encoding='utf-8'))
        return img_num, file_format, img

    def show_time(r_dict):
        t_upload = r_dict['time_uploaded'][0]
        t_process = r_dict['time_to_process'][0]
        img_size = r_dict['img_size'][0]
        t_up_label.config(text='Time uploaded: {}'.format(t_upload))
        t_pr_label.config(text='Time to process: {}'.format(t_process))
        img_size_label.config(text='Image size: {}*{}'.format(img_size[0],
                                                              img_size[1]))

    def show_hist(r_dict):
        o_hist = r_dict['original_histograms'][0]
        fig_o = plt.figure(figsize=(4, 2.4))
        fig_r1 = plt.subplot(3, 1, 1)
        fig_r1.plot(o_hist['red'][0], o_hist['red'][1], color='red',
                    linewidth=2)
        fig_r1.set_title('Red channel')
        fig_g1 = plt.subplot(3, 1, 2)
        fig_g1.plot(o_hist['green'][0], o_hist['green'][1], color='green',
                    linewidth=2)
        fig_g1.set_title('Green channel')
        fig_b1 = plt.subplot(3, 1, 3)
        fig_b1.plot(o_hist['blue'][0], o_hist['blue'][1], color='blue',
                    linewidth=2)
        fig_b1.set_title('Blue channel')
        o_plot = FigureCanvasTkAgg(fig_o, root)
        o_plot.draw()
        o_plot._tkcanvas.grid(column=0, row=row_4 + 2, columnspan=2, rowspan=2)

        p_hist = r_dict['processed_histograms'][0]
        fig_p = plt.figure(figsize=(4, 2.4))
        fig_r2 = plt.subplot(3, 1, 1)
        fig_r2.plot(p_hist['red'][0], p_hist['red'][1], color='red',
                    linewidth=2)
        fig_r2.set_title('Red channel')
        fig_g2 = plt.subplot(3, 1, 2)
        fig_g2.plot(p_hist['green'][0], p_hist['green'][1], color='green',
                    linewidth=2)
        fig_g2.set_title('Green channel')
        fig_b2 = plt.subplot(3, 1, 3)
        fig_b2.plot(p_hist['blue'][0], p_hist['blue'][1], color='blue',
                    linewidth=2)
        fig_b2.set_title('Blue channel')
        p_plot = FigureCanvasTkAgg(fig_p, root)
        p_plot.draw()
        p_plot._tkcanvas.grid(column=0, row=row_4 + 2, columnspan=2, rowspan=2)
        root.mainloop()

    def start_p():
        global o_img, p_img
        img_num, file_format, o_img = unzip_encode_img()
        p_dict = {'filename': selected_label.cget('text'),
                  'imgs': o_img,
                  'username': id_entry.get(),
                  'num_img': img_num,
                  'procedure': p_method,
                  'img_format': file_format}
        r = requests.post(address + "/api/process_img", json=p_dict)
        result = r.json()
        if type(result) == dict:
            show_time(result)
            show_hist(result)
            p_img = result['processed_img']
        else:
            messagebox.showinfo('Error', result)
        return None

    def combo_callback(self):
        global o_img, p_img
        request_name = open_req_cb.get()
        selected_label.config(text='{}'.format(request_name))
        request_id = selected_label.cget('text').split(':')[0]
        user_name = id_entry.get()
        r = requests.get(
            address + "/api/retrieve_request/" + user_name + '/' + request_id)
        result = r.json()
        p_method = result['procedure']
        selected_label.config(text=result['filename'])
        show_time(result)
        show_hist(result)
        o_img = result['original_img']
        p_img = result['processed_img']
        return None

    def decode_resize_img(img):
        img = Image.open(io.BytesIO(base64.b64decode(img)))
        img = ImageTk.PhotoImage(img.resize((500, 300)))
        return img

    def display_img():
        global o_img, p_img
        img = decode_resize_img(o_img[0])
        p_img = decode_resize_img(p_img[0])
        disp_window = Toplevel()
        o_img_label = ttk.Label(disp_window, text='Original Image')
        o_img_label.grid(column=0, row=0)
        o_img_canv = Canvas(disp_window, bg='white', width=500, height=300)
        o_img_canv.grid(column=0, row=1)
        o_img_canv.create_image(250, 200, image=img)
        p_img_label = ttk.Label(disp_window, text='Processed Image')
        p_img_label.grid(column=1, row=0)
        p_img_canv = Canvas(disp_window, bg='white', width=500, height=300)
        p_img_canv.grid(column=1, row=1)
        p_img_canv.create_image(250, 200, image=p_img)
        disp_window.mainloop()

    def download_image(dl_format):
        global p_img
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
                download_img.write()
        return dl_format

    root = Tk()
    root.title('BME547 - Image Processing')

    # User ID input
    row_1 = 0
    id_label = ttk.Label(root, text='1. Please enter your name')
    id_label.grid(column=0, row=row_1, sticky=W)
    id_entry = ttk.Entry(root)
    id_entry.grid(column=1, row=row_1)
    user_info_btn = ttk.Button(root, text='Get my user info',
                               command=get_user_metric)
    user_info_btn.grid(column=2, row=row_1)

    # Select action
    row_2 = row_1 + 1
    req_option = StringVar()
    action_label = ttk.Label(root, text='2. Please select an action')
    action_label.grid(column=0, row=row_2, sticky=W)
    new_file_btn = ttk.Button(root, text='Upload new file(s)',
                              command=select_file)
    new_file_btn.grid(column=0, row=row_2+1)
    open_req_btn = ttk.Button(root, text='View a previous request',
                              command=select_request)
    open_req_btn.grid(column=1, row=row_2+1)
    open_req_cb = ttk.Combobox(root, textvariable=req_option)
    open_req_cb.bind("<<ComboboxSelected>>", combo_callback)
    open_req_cb.grid(column=2, row=row_2+1, columnspan=3, sticky=W)
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
    t_up_label.grid(column=0, row=row_4+1, columnspan=2)
    t_pr_label = ttk.Label(root, text='Time to process:')
    t_pr_label.grid(column=2, row=row_4+1, columnspan=2)
    img_size_label = ttk.Label(root, text='Image size:')
    img_size_label.grid(column=4, row=row_4+1)

    o_hist_canv = Canvas(root, borderwidth=5, relief=GROOVE, width=400,
                         height=240)
    o_hist_canv.grid(column=0, row=row_4+2, columnspan=2, rowspan=2)
    o_hist_canv.create_text(70, 20, text='Original Histogram')
    p_hist_canv = Canvas(root, borderwidth=5, relief=GROOVE, width=400,
                         height=240)
    p_hist_canv.grid(column=2, row=row_4+2, columnspan=2, rowspan=2)
    p_hist_canv.create_text(70, 20, text='Processed Histogram')
    disp_btn = ttk.Button(root, text='Display and compare images',
                          command=display_img)
    disp_btn.grid(column=4, row=row_4+3, sticky=S)

    # Download choices
    row_5 = row_4 + 4
    download_label = ttk.Label(root, text='5. Download processed image(s)')
    download_label.grid(column=0, row=row_5, sticky=W)

    d_format = StringVar()
    d_format.set('jpg')
    jpg_btn = ttk.Radiobutton(root, text='JPG', variable=d_format, value='jpg')
    jpg_btn.grid(column=0, row=row_5+1)
    jpeg_btn = ttk.Radiobutton(root, text='JPEG', variable=d_format,
                               value='jpeg')
    jpeg_btn.grid(column=1, row=row_5+1)
    png_btn = ttk.Radiobutton(root, text='PNG', variable=d_format, value='png')
    png_btn.grid(column=2, row=row_5+1)
    tiff_btn = ttk.Radiobutton(root, text='TIFF', variable=d_format,
                               value='tiff')
    tiff_btn.grid(column=3, row=row_5+1)

    d_btn = ttk.Button(root, text='Download', command=download_image(
        d_format))
    d_btn.grid(column=4, row=row_5+1)

    root.columnconfigure(0, minsize=170)
    root.columnconfigure(1, minsize=170)
    root.columnconfigure(2, minsize=170)
    root.columnconfigure(3, minsize=170)
    root.columnconfigure(4, minsize=170)

    root.mainloop()
    return


if __name__ == "__main__":
    window_layout()
