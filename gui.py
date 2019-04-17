from tkinter import *
from tkinter import ttk


def window_layout():

    def select_file():
        pass

    def select_request():
        pass

    def start_p(filename, username, num_img, procedure):
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
    id_label = ttk.Label(root, text='1. Please enter your name')
    id_label.grid(column=0, row=0)
    user_id = StringVar()
    id_entry = ttk.Entry(root, textvariable=user_id)
    id_entry.grid(column=1, row=0)

    # Select action
    action_label = ttk.Label(root, text='2. Please select an action')
    action_label.grid(column=0, row=1, sticky=W)
    new_file_btn = ttk.Button(root, text='Browse files to start a new process',
                              command=select_file)
    new_file_btn.grid(column=1, row=1, columnspan=2)
    open_req_btn = ttk.Button(root, text='Browse requests to retrieve a '
                                         'former process',
                              command=select_request)
    open_req_btn.grid(column=3, row=1, columnspan=2)

    # Choose process
    process_label = ttk.Label(root, text='3. Please choose the procedure')
    process_label.grid(column=0, row=2, columnspan=2, sticky=W)
    p_method = StringVar()
    p_h_btn = ttk.Radiobutton(root, text='Histogram Equalization',
                              variable=p_method, value='histogram_eq')
    p_h_btn.grid(column=0, row=3)
    p_c_btn = ttk.Radiobutton(root, text='Contrast Stretching',
                              variable=p_method, value='contrast_str')
    p_c_btn.grid(column=1, row=3)
    p_l_btn = ttk.Radiobutton(root, text='Log Compression', variable=p_method,
                              value='log_compress')
    p_l_btn.grid(column=2, row=3)
    p_r_btn = ttk.Radiobutton(root, text='Reverse Video', variable=p_method,
                              value='reverse_vid')
    p_r_btn.grid(column=3, row=3)
    start_btn = ttk.Button(root, text='Start Processing', command=start_p)
    start_btn.grid(column=4, row=3)

    # Show results
    result_label = ttk.Label(root, text='4. Result')
    result_label.grid(column=0, row=4, sticky=W)

    t_upload = None
    t_process = None
    image_size = None
    t_up_label = ttk.Label(root, text='Time uploaded: {}'.format(t_upload))
    t_up_label.grid(column=0, row=5, columnspan=2, sticky=W)
    t_pr_label = ttk.Label(root, text='Time to process: {}'.format(t_process))
    t_pr_label.grid(column=2, row=5, columnspan=2, sticky=W)
    imsize_label = ttk.Label(root, text='Image size: {}'.format(image_size))
    imsize_label.grid(column=4, row=5, columnspan=2, sticky=W)

    original_histogram = None
    processed_histogram = None
    o_hist_label = ttk.Label(root, text='Original Histogram',
                             image=original_histogram)
    o_hist_label.grid(column=0, row=6, columnspan=2, rowspan=2)
    p_hist_label = ttk.Label(root, text='Processed Histogram',
                             image=processed_histogram)
    p_hist_label.grid(column=2, row=6, columnspan=2, rowspan=2)
    disp_btn = ttk.Button(root, text='Display and compare', command=display_img)
    disp_btn.grid(column=4, row=6)

    # Download choices
    download_label = ttk.Label(root, text='5. Download image(s)')
    download_label.grid(column=0, row=9, sticky=W)

    d_format = StringVar()
    jpg_btn = ttk.Radiobutton(root, text='JPG', variable=d_format, value='jpg')
    jpg_btn.grid(column=0, row=10, sticky=W)
    jpeg_btn = ttk.Radiobutton(root, text='JPEG', variable=d_format,
                               value='jpeg')
    jpeg_btn.grid(column=1, row=10, sticky=W)
    png_btn = ttk.Radiobutton(root, text='PNG', variable=d_format, value='png')
    png_btn.grid(column=2, row=10, sticky=W)
    tiff_btn = ttk.Radiobutton(root, text='TIFF', variable=d_format,
                               value='tiff')
    tiff_btn.grid(column=3, row=10, sticky=W)

    d_btn = ttk.Button(root, text='Download', command=download_image)
    d_btn.grid(column=4, row=10)

    root.mainloop()
    return


if __name__ == "__main__":
    window_layout()
