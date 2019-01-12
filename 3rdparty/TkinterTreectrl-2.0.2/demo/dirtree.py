try:
    from Tkinter import *
except ImportError:
    from tkinter import *

from TkTreectrl import *
import os
import sys

root = Tk()
t = Treectrl(root, showrootbutton=1)
t.pack(fill=BOTH, expand=1)

# create a column and define it as the widget's treecolumn
col = t.column_create(text="Basic directory tree browser", expand=1)
t.configure(treecolumn=col)

# create the elements of which a tree item will consist; use the treectrl's per-state option mechanism
# to assign different options for different states where neccessary
folder = PhotoImage(file=os.path.join(sys.path[0], 'folder.gif'))
openfolder = PhotoImage(file=os.path.join(sys.path[0], 'openfolder.gif'))
el_image = t.element_create(type=IMAGE, image=(openfolder, OPEN, folder, ''))
el_text = t.element_create(type=TEXT, fill=('white', SELECTED))
el_select = t.element_create(type=RECT, showfocus=1, fill=('blue4', SELECTED))

# put the elements together to make a style
st_folder = t.style_create()
t.style_elements(st_folder, el_image, el_select, el_text)
# layout options for look'n'feel:
t.style_layout(st_folder, el_text, padx=8, pady=2)
t.style_layout(st_folder, el_image, pady=2)
t.style_layout(st_folder, el_select, union=(el_text,), ipadx=2, iexpand=NS)


############################################################
# things to make the text cells editable                   #
############################################################

# make sure that during editing the Entry widget uses the same colors as the tree elements
root.option_add('*Entry*selectBackground', 'blue4')
root.option_add('*Entry*selectForeground', 'white')

# to enable editable cells define a new state "edit"
t.state_define('edit')
# hide the text and selection rectangle elements while editing
# set the lines option to 1, because if the text element is configured to allow
# multiple lines we get a text widget while editing instead of an entry
# which does not look so good here
t.element_configure(el_text, draw=(0, 'edit'), lines=1)
t.element_configure(el_select, draw=(0, 'edit'))

# apply the filelist bindings
t.bindtags((t, 'TreeCtrlFileList', 'TreeCtrl', t.winfo_toplevel(), 'all'))
t.set_sensitive((col, st_folder, el_text))
t.set_editable((col, st_folder, el_text))

# add callbacks for Edit events

def edit_begin(event):
    t.itemstate_set(event.item, '~edit')# toggle "edit" state to "on"

def edit_accept(event):
    t.itemelement_config(event.item, col, el_text, text=event.text)# apply the new text

def edit_end(event):
    t.itemstate_set(event.item, '~edit')# toggle "edit" state to "off"

t.notify_install('<Edit-begin>')
t.notify_bind('<Edit-begin>', edit_begin)
t.notify_install('<Edit-accept>')
t.notify_bind('<Edit-accept>', edit_accept)
t.notify_install('<Edit-end>')
t.notify_bind('<Edit-end>', edit_end)

#########################################################
#                                                       #
#########################################################

# this shows how to add a dragimage
t.set_dragimage((col, st_folder, el_text), (col, st_folder, el_image))


# define a callback to fill an opened item
def open_dir(event):
    item = event.item
    if t.item_numchildren(item):
        # directory has already been drawn, don't bother to track changes to the directory structure here
        return
    # that's a trick: store the item's full path in the text element's data option
    path = t.itemelement_cget(item, col, el_text, 'data')
    try:
        dirs = [x for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))]
        dirs.sort()
    except (OSError, IOError):
        dirs = []
    for d in dirs:
        new = t.create_item(parent=item, button=1, open=0)[0]
        t.itemstyle_set(new, col, st_folder)
        t.itemelement_config(new, col, el_text, text=d, datatype=STRING, data=os.path.join(path, d))

# bind the callback to <Expand-before> events
t.notify_bind('<Expand-before>', open_dir)

# set up the root item
t.itemstyle_set(ROOT, col, st_folder)
if sys.platform == "win32":
    t.itemelement_config(ROOT, col, el_text, text='C:', datatype=STRING, data='C:\\')
else:
    t.itemelement_config(ROOT, col, el_text, text=os.sep, datatype=STRING, data=os.sep)

t.item_config(ROOT, button=1)

# the root item is expanded by default but doesn't have any children yet, so we need to
# generate an <Expand-before> event to fill the root-directory
t.notify_generate('<Expand-before>', item=ROOT)
t.see(ROOT)

root.mainloop()
