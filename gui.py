from tkinter import *
from tkinter import filedialog as fd
from tkinter import ttk, messagebox
from zipfile import ZipFile

import matplotlib as mpl
from PIL import Image, ImageTk
from flask import Flask
mpl.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
import base64
import io
import os
import shutil


app = Flask(__name__)
address = "http://localhost:5000"


def window_layout():
    """ This function designs and shows the GUI window

    This function determines the labels, buttons and figures that show on the
    GUI window, along with their position, appearances and commands.

    Returns:
        None
    """
    global o_img, p_img, file_upload
    o_img = None
    p_img = None

    def get_user_metric():
        """ Callback function of 'Get my info' button

        This function takes the entered user id and requests the user
        information from server. If no user id entered, a message will show.

        :return:
            None
        """
        user_name = id_entry.get()
        if user_name == '':
            messagebox.showinfo('Error', 'Please enter your user name.')
            return
        r = requests.get(address + "/api/user_metrics/" + user_name)
        user_metric = r.json()
        info_n = r.status_code
        if info_n == 200:
            t = user_metric['user_creation_time']
            n_h = user_metric['num_actions']['histogram_eq']
            n_c = user_metric['num_actions']['contrast_str']
            n_l = user_metric['num_actions']['log_compress']
            n_r = user_metric['num_actions']['reverse_vid']
            messagebox.showinfo('Your Info', 'Time you created account:{} \n '
                                             'Histogram equalization: {} \n '
                                             'Contras stretch: {} \n Log '
                                             'compress: {} \n Reverse video: '
                                             '{}'.format(t, n_h, n_c, n_l, n_r))
        else:
            messagebox.showinfo('Error', user_metric)
        return None

    def select_file():
        """ Callback function of the 'Upload new image(s)'

        This function allows the user to select one or more images or a zip
        file to upload. The selected file name shows up on the window after
        selecting.

        Returns:
            None
        """
        global file_upload
        file_upload = list(fd.askopenfilenames())
        if file_upload:
            if len(file_upload) == 1:
                selected_label.config(text='{}'.format(file_upload[0]))
            else:
                selected_label.config(text='{} ...'.format(file_upload[0]))
        return None

    def select_request():
        """ Callback function of the 'View a previous request' button

        This function takes entered user id and requests the user information
        from server. It parse the returned information to options in the
        drop down bar. If the user has no previous request, a message will
        show.

        Returns:
            None
        """
        user_name = id_entry.get()
        if user_name == '':
            messagebox.showinfo('Error', 'Please enter your user name.')
            return
        r = requests.get(address + "/api/previous_request/" + user_name)
        pre_req = r.json()
        if type(pre_req) == dict:
            req_keys = []
            for key, value in pre_req.items():
                f_n = value['filename']
                t_u = value['time_uploaded']
                p = value['procedure']
                k = key + ':' + f_n + t_u + p
                req_keys.append(k)
            open_req_cb['value'] = req_keys
        else:
            messagebox.showinfo('Error', pre_req)
        return None

    def unzip_encode_img():
        """ This function encode images to pass to the server.

        This function is called after the 'Start processing' button is clicked.
        It encodes the selected image files and convert them to utf-8 string.
        If the selected file is a zip folder, it unzip it to images first.

        Returns:
            int: the number of images
            string: the format of the images
            list: the encoded images
        """
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
                print(file_list)
                for member in file_list:
                    if member[0] != '_' and member[0] != '.':
                        file_format = member.split('.')[-1]
                        with zip_file.open(member) as image_file:
                            img_b64b = base64.b64encode(image_file.read())
                            img.append(str(img_b64b, encoding='utf-8'))
        return img_num, file_format, img

    def show_time(r_dict):
        """ This function shows processing time information

        This function is called after the 'Start processing' button is clicked,
        and the processing result is returned. It takes the result and show the
        information of time uploaded, time to process and image size.

        Args:
            r_dict (dict): returned information from the server
        Returns；
            None
        """
        t_upload = r_dict['time_uploaded']
        t_process = r_dict['time_to_process']
        img_size = r_dict['img_size'][0]
        t_up_label.config(text='Time uploaded: {}'.format(t_upload))
        t_pr_label.config(text='Time to process: {} s'.format(t_process))
        img_size_label.config(text='Image size: {}*{}'.format(img_size[0],
                                                              img_size[1]))
        return None

    def show_hist(r_dict):
        """ This function shows histograms

        This function is called after the 'Start processing' button is clicked,
        and the processing result is returned. It takes the result tuple and
        plot it on the window.

        Args:
            r_dict (dict): returned information from the server
        Returns:
            None
        """
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
        p_plot._tkcanvas.grid(column=2, row=row_4 + 2, columnspan=2, rowspan=2)
        return None

    def start_p():
        """ Callback function of the 'Start processing' button

        This function encode the images, pass it to the server along with other
        processing information, and takes the returned result. It then show or
        plot the returned result.

        Returns:
            None
        """
        global o_img, p_img, file_upload
        try:
            len_f = len(file_upload)
            if len_f < 1:
                raise NameError('error')
        except NameError:
            messagebox.showinfo('Error', 'Please select file')
            return None

        img_num, file_format, o_img = unzip_encode_img()
        p_dict = {'filename': selected_label.cget('text').split('/')[-1],
                  'imgs': o_img,
                  'username': id_entry.get(),
                  'num_img': img_num,
                  'procedure': p_method.get(),
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
        """ Callback function of the drop down bar

        This funtion shows the selected previous request. It passes the user id
        and request id to the server, and show or plot the returned information.

        Returns:
             None
        """
        global o_img, p_img
        request_name = open_req_cb.get()
        selected_label.config(text='{}'.format(request_name))
        request_id = selected_label.cget('text').split(':')[0]
        user_name = id_entry.get()
        r = requests.get(
            address + "/api/retrieve_request/" + user_name + '/' + request_id)
        result = r.json()
        p_method.set(result['procedure'])
        selected_label.config(text=result['filename'])
        show_time(result)
        show_hist(result)
        o_img = result['original_img']
        p_img = result['processed_img']

        return None

    def decode_resize_img(img):
        """ This function decode and resize images to show

        This function takes the utf-8 string formatted images and decode it to
        images that can be plotted. It also resizes them so that they fit the
        window.

        Args:
            img (str): encoded images from the server

        Returns:
            PhotoImage: image to be plotted.
        """
        img = Image.open(io.BytesIO(base64.b64decode(img)))
        img = ImageTk.PhotoImage(img.resize((500, 300)))
        return img

    def download_image(dl_format):
        """ Callback function of the 'Download image(s)' button

        This function allows user to select the folder where they would like to
        download their processed images and name the image or zip file. If more
        than one images is to be downloaded, they will be downloaded as zip.
        User can select the format.

        Args:
            dl_format (string): user selected format to download the images

        Returns:
            None
        """
        global p_img
        if p_img is None:
            messagebox.showinfo('Error', 'No image to download.')
            return
        desired_name = fd.asksaveasfilename(initialdir=os.getcwd(),
                                            title='Select directory')
        if desired_name == '':
            return None
        print(desired_name)
        img_num = len(p_img)
        if img_num > 1:
            try:
                os.mkdir('./temp/')
            except FileExistsError:
                print('temp folder already exists')
            file_path = r'./temp/'
            for i in range(img_num):
                decoded = decode_b64(p_img[i], 'JPG')
                temp_file_name = str(i) + '.' + dl_format.get()
                mpimg.imsave(file_path + temp_file_name, decoded,
                             format=dl_format.get().upper())
            zip_file = ZipFile(desired_name + '.zip', 'w')
            for i in range(img_num):
                zip_file.write("./temp/{}.{}".format(i, dl_format.get()),
                               arcname="{}.{}".format(i, dl_format.get()))
            zip_file.close()
            shutil.rmtree(file_path)
        else:
            one_img = p_img[0]
            decoded = decode_b64(one_img, 'JPG')
            final_file_name = desired_name + '.' + dl_format.get()
            mpimg.imsave(final_file_name, decoded, format=dl_format.get().upper())
        return None

    def display_img():
        """ Callback function of the 'Display and compare images' button

        This function uses a pop-up window to show the original image and
        processed image.

        Returns:
            None
        """
        global o_img, p_img
        if o_img is None or p_img is None:
            messagebox.showinfo('Error', 'No image to compare.')
            return
        o_img_first = decode_resize_img(o_img[0])
        p_img_first = decode_resize_img(p_img[0])
        disp_window = Toplevel()
        o_img_label = ttk.Label(disp_window, text='Original Image')
        o_img_label.grid(column=0, row=0)
        o_img_canv = Canvas(disp_window, bg='white', width=500, height=300)
        o_img_canv.grid(column=0, row=1)
        o_img_canv.create_image(250, 200, image=o_img_first)
        p_img_label = ttk.Label(disp_window, text='Processed Image')
        p_img_label.grid(column=1, row=0)
        p_img_canv = Canvas(disp_window, bg='white', width=500, height=300)
        p_img_canv.grid(column=1, row=1)
        p_img_canv.create_image(250, 200, image=p_img_first)
        disp_window.mainloop()
        return None

    def decode_b64(base64_string, img_format):
        """Decodes a single image from b64 format

        Args:
            base64_string (str): image before decoding
            img_format (str): what format the string was encoded in

        Returns:
            ndarray: image in matrix form
        """
        image_bytes = base64.b64decode(base64_string)
        image_buf = io.BytesIO(image_bytes)
        return mpimg.imread(image_buf, format=img_format)

    def encode_b64(image, img_format):
        """Encodes a single image with b64

        Args:
            image (ndarray): image in matrix form
            img_format (str): format to encode image

        Returns:
            str: encoded image
        """
        image_buf = io.BytesIO()
        mpimg.imsave(image_buf, image, format=img_format)
        image_buf.seek(0)
        b64_bytes = base64.b64encode(image_buf.read())
        return str(b64_bytes, encoding='utf-8')
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

    d_btn = ttk.Button(root, text='Download',
                       command=lambda i=d_format: download_image(i))
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
