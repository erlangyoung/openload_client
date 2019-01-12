try:
    from Tkinter import *
except ImportError:
    from tkinter import *

from TkTreectrl import *

'''The fancy_multilistbox demo shows how to use some of the more advanced
capabilities of the MultiListbox widget:
   - add icons to the first column
   - add different colors for rows in the listbox
   - make columns sortable
   - make columns editable'''

root = Tk()
root.title('Fancy ScrolledMultiListbox demo')
message='''Sort the columns by clicking the column headers!
Edit the ratings by clicking in the third column (or hit Ctrl-e)!'''
Label(root, text=message).pack(side='top', padx=5, pady=5)
m = ScrolledMultiListbox(root, relief='groove', bd=2, width=250, height=200)
m.pack(side='top', fill='both', expand=1, padx=2, pady=2)
Button(text='Close', command=root.quit).pack(side='top', pady=8)

m.listbox.config(columns=('Dish', 'Price', 'Rating'), expandcolumns=(0,), selectmode='extended')

###################################################################
###### add a set of different colors for itembackground ###########
###################################################################

# in case anyone wants more than two colors: it is possible
colors = ('white', '#ffdddd', 'white', '#ddeeff')
m.listbox.column_configure(m.listbox.column(0), itembackground=colors)
m.listbox.column_configure(m.listbox.column(1), itembackground=colors)
m.listbox.column_configure(m.listbox.column(2), itembackground=colors)

###################################################################
###### add a different style with an icon for the first column ####
###################################################################

# first create an image element:
icon = PhotoImage(data=('R0lGODlhDgAPAKL/AAAAAAD/AP8AAMDAwP//AICAAAAA/wAAACH5BAEAAAMA'
                        'LAAAAAAOAA8AQANCOAqs/kAIBkIBi5XL931DZXUbthiAcZmOGLwBUILMO4ff'
                        'Au8sfoMhAEEoyy08nhGrNolVjKGJaCYzTVea3BUZGyQAADs='))
el_image = m.listbox.element_create(type='image', image=icon)

# by default all columns use the same style, so
# we cannot simply change the configuration for the style in column 0
# because this would apply the change to all columns; so we need to define a new style
# create and configure the new style:
icon_style = m.listbox.style_create()
m.listbox.style_elements(icon_style, m.listbox.element('select'), el_image, m.listbox.element('text'))
m.listbox.style_layout(icon_style, el_image, padx=3, pady=2)
m.listbox.style_layout(icon_style, m.listbox.element('text'), padx=4, iexpand='e', expand='ns')
m.listbox.style_layout(icon_style, m.listbox.element('select'),
                        union=(m.listbox.element('text'), el_image), ipady=1, iexpand='nsew')

# apply the new style for the first column
m.listbox.style(0, icon_style)

# insert something and see how it looks...
dishes = ('Spam', 'Eggs', 'Hamburger', 'Pizza', 'Wholewheat bun', 'Spinach', 'Broccoli', 'Schnitzel')
prices = ('0.99', '0.48', '1.48', '2.99', '0.29', '0.79', '1.19', '5.99')
ratings = ('+++++', '++', '----', '+++', '-----', '---', '-', '+++++')
for i in range(8):
    m.listbox.insert('end', dishes[i], prices[i], ratings[i])

###################################################################
############## make the columns sortable ##########################
###################################################################

# add arrow icons to the column headers first
m.listbox.column_configure(m.listbox.column(0), arrow='down', arrowgravity='right')
m.listbox.column_configure(m.listbox.column(1), arrow='down', arrowgravity='right')
m.listbox.column_configure(m.listbox.column(2), arrow='down', arrowgravity='right')

# set sortorder flags indicating the sorting order for every column
sortorder_flags = {0 : 'increasing', 1 : 'increasing', 2 : 'increasing'}

# we will use builtin ascii sorting for column 0, builtin float sorting for col 1
# and define a special sort command for column 2:

def sort_by_rating(item1, item2):
    i1, i2 = m.listbox.index(item=item1), m.listbox.index(item=item2)
    a = m.listbox.get(i1)[0][2]
    b = m.listbox.get(i2)[0][2]

    if a.startswith('+') and b.startswith('-'):
        return -1
    elif a.startswith('-') and b.startswith('+'):
        return 1
    elif a.startswith('+'):
        if a > b:
            return -1
        elif a < b:
            return 1
        else:
            return 0
    elif b > a:
        return -1
    elif b < a:
        return 1
    else:
        return 0

# now create a common sort command for all columns
def sort_list(event):
    # do the sorting
    if event.column == 0:
        m.listbox.sort(column=0, mode=sortorder_flags[0])
    elif event.column == 1:
        m.listbox.sort(column=1, mode=('real', sortorder_flags[1]))
    else:
        m.listbox.sort(column=2, command=sort_by_rating, mode=sortorder_flags[2])
    # switch the sortorder flag and turn the arrow icons upside down
    if sortorder_flags[event.column] == 'increasing':
        m.listbox.column_configure(m.listbox.column(event.column), arrow='up')
        sortorder_flags[event.column] = 'decreasing'
    else:
        m.listbox.column_configure(m.listbox.column(event.column), arrow='down')
        sortorder_flags[event.column] = 'increasing'

# finally register the sort command
m.listbox.notify_install('<Header-invoke>')
m.listbox.notify_bind('<Header-invoke>', sort_list)

###################################################################
############## make the last column editable ######################
###################################################################

# for look'n'feel: while editing, floating Entry widgets are put on top
# of cell that is being edited
root.option_add('*Entry*selectForeground', m.listbox['selectforeground'])
root.option_add('*Entry*selectBackground', m.listbox['selectbackground'])

# define edit state and apply filelist bindings
m.listbox.state_define('edit')
m.listbox.bindtags((m.listbox, 'TreeCtrlFileList', 'TreeCtrl', m.listbox.winfo_toplevel(), 'all'))

# make all columns sensitive to mouse events, but only column 2 editable
setsensitive = [(m.listbox.column(i), m.listbox.style(i),
                m.listbox.element('text')) for i in range(m.listbox.numcolumns())]
m.listbox.set_sensitive(*setsensitive)
m.listbox.set_editable((m.listbox.column(2), m.listbox.style(2), m.listbox.element('text')))

# hide the old text while editing, that's what we need the "edit" state for
m.listbox.element_configure(m.listbox.element('text'), draw=(0, 'edit'), lines=1)

# a helper function for validating user input:
def is_valid(text):
    # return True if text is a valid "rating" we will accept, else return False
    # reject empty strings and strings greater than 10 characters:
    if not (0 < len(text) < 11):
        return 0
    # string must begin with "+" or "-":
    if not text[0] in ('+', '-'):
        return 0
    # string must either contain only "+" or only "-":
    for sign in ('+', '-'):
        if text.startswith(sign):
            for char in text:
                if char != sign:
                    return 0
    return 1

# now define callbacks for edit event handlers;
# the three mandatory handlers for making cells editable with a mouse click:

def edit_begin(event):
    # toggle "edit" state to "on"
    m.listbox.itemstate_forcolumn(event.item, m.listbox.column(2), 'edit')

def edit_accept(event):
    # if our demo claims to be "fancy", there should be some validating
    # of the user input...
    if is_valid(event.text):
        # apply the new text; we could use the listbox methods here,
        # but it's really easier with the treectrl method
        m.listbox.itemelement_config(event.item, m.listbox.column(2),
                                     m.listbox.element('text'), text=event.text)
    else:
        m.bell()

def edit_end(event):
    # toggle edit state to "off"
    m.listbox.itemstate_forcolumn(event.item, m.listbox.column(2), '!edit')

# a special callback to enable editing with the keyboard;
# if you find a more obvious way to do this, send me a mail!
def edit_invoke(event):
    # emulate a mouse-click onto the active "rating";
    # in order to achieve this we first have to make the item visible and select it,
    # then calculate its x and y coords and generate the ButtonPress
    # and ButtonRelease events there
    index = m.listbox.index('active')
    if index > -1:
        m.listbox.see(index)
        m.listbox.select_set(index)
        x0, y0, x1, y1 = m.listbox.item_bbox(m.listbox.item(index), m.listbox.column(2),
                                             m.listbox.element('text'))
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        m.listbox.event_generate('<ButtonPress-1>', x=x, y=y)
        m.listbox.event_generate('<ButtonRelease-1>', x=x, y=y)


# finally install the event handlers
m.listbox.notify_install('<Edit-begin>')
m.listbox.notify_bind('<Edit-begin>', edit_begin)
m.listbox.notify_install('<Edit-accept>')
m.listbox.notify_bind('<Edit-accept>', edit_accept)
m.listbox.notify_install('<Edit-end>')
m.listbox.notify_bind('<Edit-end>', edit_end)
m.listbox.bind('<Control-e>', edit_invoke)

# shows how to identify a clicked list item
def on_button_1(event):
    info = m.listbox.identify(event.x, event.y)
    if not info:
        print('You clicked into the void.')
    elif info[0] == 'item':
        print('You clicked item', info[1], 'at listbox index', m.listbox.index(item=info[1]))
    elif info[0] == 'header':
        print('You clicked the column header of column', info[1])
m.listbox.bind('<1>', on_button_1, add=1)


root.mainloop()
