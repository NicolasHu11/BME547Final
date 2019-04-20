from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from flask import Flask, jsonify, request
import requests
app = Flask(__name__)


def window_layout():
    t_upload = None
    t_process = None
    image_size = None
    original_histogram = None
    processed_histogram = None

    def select_file():
        filename = fd.askopenfilename()
        if filename != '':
            selected_label.config(text='File selected: {}'.format(filename))
        return None

    def select_request():
        username = id_entry.get()
        # pre_request = requests.get('http://example.com/{}'.format(username))
        pre_request = ['request 1', 'request 2', 'request 3']
        open_req_cb['value'] = pre_request
        return None

    def combo_callback(self):
        requestname = open_req_cb.get()
        selected_label.config(text='Request selected: {}'.format(requestname))

        return None

    def start_p(filename, username, num_img, procedure, fileformat):
        """
        Args:
            filename: list containing strings of the file name
            username: string containing the user name
            num_img:
            procedure:
            fileformat: string containing the format of the file(s)
        Returns:
            json: the client json file for POST
        """
        pass

    def display_img():
        pass

    def download_image():
        pass

    root = Tk()
    root.title('BME547 - Image Processing')

    # User ID input
    row_1 = 0
    id_label = ttk.Label(root, text='1. Please enter your name')
    id_label.grid(column=0, row=row_1)
    id_entry = ttk.Entry(root)
    id_entry.grid(column=1, row=row_1)

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

    t_up_label = ttk.Label(root, text='Time uploaded: {}'.format(t_upload))
    t_up_label.grid(column=0, row=row_4+1, columnspan=2, sticky=W)
    t_pr_label = ttk.Label(root, text='Time to process: {}'.format(t_process))
    t_pr_label.grid(column=2, row=row_4+1, columnspan=2, sticky=W)
    imsize_label = ttk.Label(root, text='Image size: {}'.format(image_size))
    imsize_label.grid(column=4, row=row_4+1, columnspan=2, sticky=W)

    o_hist_label = ttk.Label(root, text='Original Histogram',
                             image=original_histogram)
    o_hist_label.grid(column=0, row=row_4+2, columnspan=2, rowspan=2)
    p_hist_label = ttk.Label(root, text='Processed Histogram',
                             image=processed_histogram)
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

    d_btn = ttk.Button(root, text='Download', command=download_image)
    d_btn.grid(column=4, row=row_5+1)

    root.mainloop()
    return


if __name__ == "__main__":
    window_layout()
