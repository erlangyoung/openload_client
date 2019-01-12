try:
    from Tkinter import *
except ImportError:
    from tkinter import *

from TkTreectrl import *

root = Tk()
root.title('Simple MultiListbox demo')
label = Label(root, text='Running self test, please wait...')
label.pack(side='top', pady=5)
m = MultiListbox(root)
m.pack(side='top', fill='both', expand=1)
Button(root, text='Close', command=root.quit).pack(side='top', pady=5)
m.focus_set()

def select_cmd(selected):
    print('Selected items:', selected)

def dblclick_cmd(index):
    if index >= 0:
        cont = m.listbox.get(index)
    else:
        cont = ''
    print('Called "command" callback on item:', index, ':', cont)
    print('Currently selected:', m.listbox.curselection())

m.configure(selectcmd=select_cmd, command=dblclick_cmd, selectmode='extended')
print('Nearest item to y-coordinate 80:', m.nearest(80))

def test1():
    m.config(columns=('Column 1', 'Column 2', 'Column 3'), expandcolumns=(0, 1))
    for x in range(20):
        m.insert('end', 'Foo', 'Bar', 'blah')

def test2():
    m.select_set(7)
    m.config(columns=('Column 1', 'Column 2'), expandcolumns=())
    m.delete(5, 10)
    m.insert(3, 'foo', 'bar')

def test3():
    m.config(columns=('Foos', 'Bars'), expandcolumns=(0,))
    m.delete(0, 'end')
    for x in range(20):
        m.insert('end', 'Foo %d' % x, 'Bar %d' % x)
    m.insert(7, 'Spam', 'Eggs')
    print('Nearest item to y-coordinate 80:', m.nearest(80), ':', m.get(m.nearest(80)))

def test4():
    m.sort(column=0, mode='decreasing')
    m.activate(10)
    m.select_set(0, 7)

def test5():
    m.sort(column=0, mode=('dictionary', 'increasing'))
    m.activate(1)
    print('index(8) :', m.index(8), ', index("end") :', m.index('end'))
    print('index("active") :', m.index("active"), ', index("@75,100") :', m.index("@75,100"))
    m.see('end')

def test6():
    m.see(0)
    print(m.select_includes(70), m.select_includes(6))

def test7():
    m.sort(0, mode='decreasing', first=1, last=5)
    print('bbox(4):', m.bbox(4))


alltests = (test1, test2, test3, test4, test5, test6, test7)
next = 0
def next_test():
    global next
    try:
        test = alltests[next]
        test()
        next += 1
        root.after(1000, next_test)
    except IndexError:
        pass
    if next == len(alltests):
        label.configure(text='Self test successfully finished')

root.after(1000, next_test)

root.mainloop()

