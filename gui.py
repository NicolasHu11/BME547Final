from tkinter import *
from tkinter import ttk


def window_layout():

    def select_file():
        pass

    def start_p():
        pass

    def close_window():
        pass

    root = Tk()
    root.title('BME547 - Image Processing')

    # User ID input
    id_label = ttk.Label(root, text='1. Please enter your name')
    id_label.grid(column=0, row=0)
    user_id = StringVar()
    id_entry = ttk.Entry(root, textvariable=user_id)
    id_entry.grid(column=0, row=1)

    # Select action
    action_label = ttk.Label(root, text='2. Please select an action')
    action_label.grid(column=0, row=3)
    new_req_label = ttk.Label(root, text='  - Start a new request')
    new_req_label.grid(column=0, row=4, sticky=W)
    new_file_btn = ttk.Button(root, text='Browse files', command=select_file)
    new_file_btn.grid(column=0, row=5, sticky=E)
    old_req_label = ttk.Label(root, text='  - Retrieve a request')
    old_req_label.grid(column=0, row=6, sticky=W)
    open_req_btn = ttk.Button(root, text='Browse requests', command=select_file)
    open_req_btn.grid(column=0, row=7, sticky=E)

    # Choose process
    process_label = ttk.Label(root, text='3. Please choose the process')
    process_label.grid(column=1, row=0, columnspan=2, sticky=W)
    process_h = IntVar()
    process_c = IntVar()
    process_l = IntVar()
    process_r = IntVar()
    p_h_btn = ttk.Checkbutton(root, text='Histogram Equalization',
                              variable=process_h, onvalue=1, offvalue=0)
    p_h_btn.grid(column=1, row=1)
    p_c_btn = ttk.Checkbutton(root, text='Contrast Stretching',
                              variable=process_c, onvalue=1, offvalue=0)
    p_c_btn.grid(column=2, row=1)
    p_l_btn = ttk.Checkbutton(root, text='Log Compression', variable=process_l,
                              onvalue=1, offvalue=0)
    p_l_btn.grid(column=3, row=1)
    p_r_btn = ttk.Checkbutton(root, text='Reverse Video', variable=process_r,
                              onvalue=1, offvalue=0)
    p_r_btn.grid(column=4, row=1)
    start_btn = ttk.Button(root, text='Start Processing', command=start_p)
    start_btn.grid(column=4, row=2, sticky=E)

    # Show results
    result_label = ttk.Label(root, text='4. Result')
    result_label.grid(column=1, row=3, sticky=W)
    original_image = None
    processed_image = None
    o_image_label = ttk.Label(root, text='Original Image', image=original_image)
    o_image_label.grid(column=1, row=4, columnspan=2, rowspan=2)
    p_image_label = ttk.Label(root, text='Processed Image',
                              image=processed_image)
    p_image_label.grid(column=3, row=4, columnspan=2, rowspan=2)

    # Show information
    original_histogram = None
    processed_histogram = None
    t_upload = None
    t_process = None
    image_size = None
    info_label = ttk.Label(root, text='5. Image Parameters')
    info_label.grid(column=1, row=6, sticky=W)

    o_hist_label = ttk.Label(root, text='Original Histogram',
                             image=original_histogram)
    o_hist_label.grid(column=1, row=7)
    p_hist_label = ttk.Label(root, text='Processed Histogram',
                             image=processed_histogram)
    p_hist_label.grid(column=2, row=7)
    infos_label = ttk.Label(root, text='Time uploaded: {}\nTime to process: {'
                                       '}\nImage size: {}'.format(t_upload,
                                                                  t_process,
                                                                  image_size))
    infos_label.grid(column=3, row=7)

    # Close button
    close_button = ttk.Button(root, text='Close', command=root.destroy)
    close_button.grid(column=4, row=7)
    root.mainloop()
    return


if __name__ == "__main__":
    window_layout()
