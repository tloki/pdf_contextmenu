from cfg import *
from context_menu import menus
from PyPDF2 import PdfFileWriter, PdfFileReader
import tkinter
from tkinter import messagebox
import tkinter as tk
# from time import sleep
import os


def remove_ext(filename: str):
    # TODO: this is hardcoded linux path separator. Make dynamic or be able to choose

    pre = None

    sep = '/'
    if os.name == 'nt':
        sep = '\\'

    if sep in filename:
        i = filename[::-1].index(sep)
        i = len(filename) - i - 1
        pre = filename[0:i]
        filename = filename[i:]
    #
    # print(pre)
    # print(filename)

    try:
        i = filename[::-1].index('.')
        i = len(filename) - i - 1
    except ValueError:
        if pre is None:
            return filename
        else:
            return pre + filename

    if pre is None:
        return filename[0:i]
    return pre + filename[0:i]


class PopupWindow(object):
    def __init__(self, query, value_array, master: tk.Tk):
        self.value_array = value_array
        top = self.top = tk.Toplevel(master)
        self.l = tk.Label(top, text=query)
        self.l.pack()
        self.e = tk.Entry(top)
        self.e.pack()
        self.b = tk.Button(top, text='Ok', command=self.cleanup)
        self.b.pack()
        self.value = []

        self.top.mainloop()

    def cleanup(self):
        self.value = self.e.get()
        self.value_array.append(self.value)
        self.top.destroy()
        self.top.quit()


def prompt_page_number(msg, min_page=0, max_page=100):
    root = tk.Tk()
    root.withdraw()

    values = []
    print(f"{msg.format(min_page, max_page)}")

    win = PopupWindow(query=msg.format(min_page, max_page), value_array=values, master=root)

    if len(values) == 0:
        return None

    # print("unesen broj:")
    value = values[0]

    allowed_chars = [str(e) for e in range(0, 10)]
    allowed_chars.append(",")
    allowed_chars.append(" ")

    if len(value) == 0:
        warn(PAGE_FORMAT_WARNING)
        return None

    for c in value:
        if not c in allowed_chars:
            warn(PAGE_FORMAT_WARNING)
            return None

    while " " in value:
        value = value.replace(" ", "")

    value = value.split(",")

    for v in value:
        if not v.isnumeric() or int(v) not in range(min_page, max_page + 1):
            warn(MUST_BE_NUMBER.format(min_page, max_page))
            return None

    value = [int(v) for v in value]

    for i in range(1, len(value)):
        if not value[i] > value[i - 1]:
            warn(PAGE_FORMAT_WARNING)
            return None

    return value


def warn(msg):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title=None, message=msg)


def split_to_multiple_pdfs(pdf, page_number: list, original_path):
    pth_root = remove_ext(original_path)

    last_page_number = 1

    for current_page_num in page_number:
        first_path = pth_root + "_{}_{}.pdf".format(last_page_number, current_page_num)

        output = PdfFileWriter()

        for i in range(last_page_number - 1, current_page_num):
            output.addPage(pdf.getPage(i))

        with open(first_path, "wb") as output_stream:
            output.write(output_stream)

        last_page_number = current_page_num + 1

    first_path = pth_root + "_{}_{}.pdf".format(last_page_number, pdf.getNumPages())
    output = PdfFileWriter()
    for i in range(last_page_number - 1, pdf.getNumPages()):
        output.addPage(pdf.getPage(i))

    with open(first_path, "wb") as output_stream:
        output.write(output_stream)



def split_to_two_pdfs(pdf, page_number: int, original_path):
    pth_root = remove_ext(original_path)
    first_path = pth_root + "_{}_{}.pdf".format(1, page_number)
    second_path = pth_root + "_{}_{}.pdf".format(page_number + 1, pdf.getNumPages())

    output_first = PdfFileWriter()
    output_second = PdfFileWriter()

    for i in range(page_number):
        output_first.addPage(pdf.getPage(i))

    for i in range(page_number, pdf.getNumPages()):
        output_second.addPage(pdf.getPage(i))

    with open(first_path, "wb") as output_stream:
        output_first.write(output_stream)

    with open(second_path, "wb") as output_stream:
        output_second.write(output_stream)


def pdf_merge_menu(filenames, params):
    print(filenames)
    input("not yet implemented")


def pdf_split_menu(filenames, params):
    # print(filenames)
    if len(filenames) != 1:
        warn(CHOOSE_ONLY_ONE_PDF)
        return

    file_path = filenames[0]
    if not file_path.lower().endswith(".pdf"):
        warn(CHOOSE_PDF)
        return

    # print(file_path)
    # # input("read?")

    with open(file_path, "rb") as f:
        pdf = PdfFileReader(f)

        num_pages = pdf.getNumPages()
        if num_pages < 2:
            warn(PDF_MUST_MULTIPAGE)
            f.close()
            return

        num = prompt_page_number(INSERT_PAGE_NUMBER, 1, num_pages - 1)
        if num is None:
            f.close()
            return

        split_to_multiple_pdfs(pdf, num, file_path)
        # split_to_two_pdfs(pdf, num, file_path)


if os.name != "nt" and __name__ == '__main__':
    pdf_split_menu(["/Users/loki/Projects/pdf_contextmenu/example_pdfs/multipage_manual.pdf"], None)
    exit(0)

if __name__ == '__main__':
    from context_menu import menus

    # TODO: fix with multiple selected documents
    cm = menus.ContextMenu(MENU_NAME, type='FILES')

    cm.add_items([
        menus.ContextCommand(SPLIT_NAME, python=pdf_split_menu),
        # menus.ContextCommand(MERGE_NAME, python=pdf_merge_menu)
    ])

    cm.compile()
