from functools import partial
import configparser 
import os
import threading
import logging
import openload
import task_queue
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import TkTreectrl

class OLWindow(object):
    config_name = 'openload_config.ini'
    section_name = 'LoginInfo'
    def __init__(self):
        # windows
        self.window = tk.Tk()
        self.window.title("Openload")
        self.window.geometry("700x500")
        #window.grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(1, weight=1)
        #window.grid_rowconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        # init entries
        self.lb_frame_init = tk.LabelFrame(self.window, text='Init info', takefocus=1, width=700)
        #lb_frame_init.pack(expand=1, fill='x', pady=10)
        self.lb_frame_init.grid_rowconfigure(0, weight=1)
        self.lb_frame_init.grid(row=0, sticky='ew')

        # init entries
        var_login_id = tk.StringVar()
        var_login_key = tk.StringVar()
        if os.path.exists(self.config_name):
            cf = configparser.ConfigParser()
            cf.read(self.config_name)
            kvs = cf.items(self.section_name)
            for key, value in kvs:
                if key == 'login_id':
                    var_login_id.set(value)
                if key == 'login_key':
                    var_login_key.set(value)

        self.lable_login_id = tk.Label(self.lb_frame_init, text='Login Id: ')
        self.lable_login_id.grid(row=0, column=0, sticky='nsew')
        self.entry_login_id = tk.Entry(self.lb_frame_init, textvariable=var_login_id, width=30)
        self.entry_login_id.grid(row=0, column=1, sticky='nsew')

        self.lable_login_key = tk.Label(self.lb_frame_init, text='Login Key: ')
        self.lable_login_key.grid(row=0, column=2)
        self.entry_login_key=tk.Entry(self.lb_frame_init, textvariable=var_login_key, width=30)
        self.entry_login_key.grid(row=0, column=3, sticky='nsew')

        # add tabs
        self.tab_control = ttk.Notebook(self.window)
        #tab_control.grid_columnconfigure(0, weight=1)
        self.tab_upload = ttk.Frame(self.tab_control)
        self.tab_upload.grid_rowconfigure(0, weight=1)
        self.tab_upload.grid_columnconfigure(0, weight=1)
        self.tab_upload.grid(sticky='nsew')
        self.tab_control.add(self.tab_upload, text='upload')
        self.tab_control.grid(row=1, sticky='nsew')
        self.tab_download = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_download, text='download')

        #upload list
        self.ul_tree_ctrl = TkTreectrl.MultiListbox(self.tab_upload)
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.ul_tree_ctrl.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.ul_tree_ctrl.xview)
        self.ul_tree_ctrl.configure(selectmode='multiple', yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.ul_tree_ctrl.config(columns=('file', 'progress'))
        self.ul_tree_ctrl.grid(row=0, column=0, columnspan=2, sticky='nsew')
        vsb.grid(column=2, row=0, sticky='ns', in_=self.tab_upload)
        hsb.grid(column=0, row=1, columnspan=2, sticky='ew', in_=self.tab_upload)

        self.file_sel_button = tk.Button(self.tab_upload, text='select files', command=self.select_files)
        self.file_sel_button.grid(row=2, column=0, sticky='w')

        self.upload_button = tk.Button(self.tab_upload, text='upload', width=10, command=self.upload_file)
        self.upload_button.grid(row=2, column=1, sticky='w')

        # data
        self.upload_file_dict = {}
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.task_queue = task_queue.TaskQueue(2)
        self.task_queue.start()

    def progress(self, index, size, progress):
        percent = progress * 100 / size
        self.update_progress(index, percent=percent)
        
    def reocord_login_info(self, login_id, login_key):
        ''' write config info'''
        cf = configparser.ConfigParser()
        if not cf.has_section(self.section_name):
            cf.add_section(self.section_name)
        cf.set(self.section_name, 'login_id', login_id)
        cf.set(self.section_name, 'login_key', login_key)
        cf.write(open(self.config_name, 'w'))

    def select_files(self):
        file_names = tk.filedialog.askopenfilenames()
        for path in file_names:
            with self.lock:
                index = self.ul_tree_ctrl.size()
                self.ul_tree_ctrl.insert('end', path, 'pending')
                self.upload_file_dict[index] = path

    def update_progress(self, index, percent=0, msg=None):
         with self.lock:
            item = self.ul_tree_ctrl.get(index)
            self.ul_tree_ctrl.delete(index)
            if not msg:
                self.ul_tree_ctrl.insert(index, item[0][0], '{percent:3.0f}%'.format(percent=percent))
            else:
                self.ul_tree_ctrl.insert(index, item[0][0], msg)

    def do_upload(self, openload, file, index):
        self.update_progress(index, 0)
        try:
            result = openload.upload_file(file, progress_cb=partial(self.progress, index))
        except Exception as e:
            logging.error(e)
            self.update_progress(index, percent=0, msg='failed')
            return
        self.update_progress(index, percent=100, msg='done')
        logging.info('upload file: %s done', file)
        print(result)

    def upload_file(self):
        login_id = self.entry_login_id.get()
        login_key = self.entry_login_key.get()
        self.reocord_login_info(login_id, login_key)
        self.ul_tree_ctrl.curselection()
        selected_items = [(idx, self.ul_tree_ctrl.get(idx)[0]) for idx in self.ul_tree_ctrl.curselection()]
        ol = openload.OpenLoad(login_id,login_key)
        for idx, item in selected_items:
            self.task_queue.queue(partial(self.do_upload, ol, item[0], idx))


def main():
    try:
        LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(filename='openload.log', level=logging.INFO, format=LOG_FORMAT)
        ol = OLWindow()
        ol.window.mainloop()
    except Exception as e:
        print(e)
        logging.error(e)

if __name__ == '__main__':
    main()


