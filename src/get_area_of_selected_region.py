# -*- coding: utf-8 -*-
# encoding: utf-8
from __future__ import unicode_literals
__copyright__ = "Copyright (c) 2016, Stanislav Vohnik. All rights reserved."
__license__ = "This source code is licensed under the BSD-style license."
__version__ = "2016-10-06"

from tkinter import Frame, Canvas, Menu, BOTH, YES, Label, StringVar, BOTTOM, Tk, mainloop, Entry, Button, ACTIVE, LEFT
#from area import area
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import Dialog
from os.path import expanduser
from datetime import datetime
import PIL.ExifTags
import numpy as np



home = expanduser("~")

class Start_Dialog(Dialog):
    ''' Trida dailogu pro vkladani hodnot, vlozene hodnotu jsou v self.result'''

    def __init__(self,parent,parameters, title = 'Enter detail', meassure_action = False):

        self.meassure_action = meassure_action
        self.parameters = parameters
        Dialog.__init__(self, parent, title)


        if parameters == None or parameters == []:
            self.result = {}
            return


    def body(self, parent):
        self.ee = {}
        for e,i in enumerate( self.parameters.keys()):
            Label(parent, text="{i}".format(i = i)).grid(row=e)
            vvalue = self.parameters.get(i)
            self.ee[i] = Entry(parent, width = 64)
            self.ee[i].insert(0,str(vvalue))
            self.ee[i].grid(row=e, column=1)

        return self.ee[i] # initial focus

    def apply(self):
        self.result = {}
        for i in self.ee.keys():
            value =self.ee[i].get()
            self.result[i] = value
        return

    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        if self.meassure_action :
            w = Button(box, text="Measure", width=10, command=self.meassure)
            w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def meassure(self,event=None):
        del self.ee['pixels']
        self.ok()
        return





class App(Frame):
    ''' Hlavni trida UI Aplikace  which loads  jpg file and lets you select an area which then calculates and saves along with other info to file'''

    def __init__(self, master):
        #''' kazda trida ma inicializacni proceduru '''
        Frame.__init__(self)
        self.master = master
        self.Type = ''
        self.x = self.y = 0
        self.coordinates = []
        self.prev = []
        self.count = 0
        self.Data = []
        self.label3text = StringVar()
        self.lines = {}
        self.ovals = {}
        self.area = []
        self.px = 62


        self.message = Label( self.master, textvariable = self.label3text )
        self.message.pack( side = BOTTOM )

        self.Start()

        #self.calibration = 180*360/area({'type':'Polygon','coordinates':[[[-180,-90],[-180,90],[180,90],[180,-90],[-180,-90]]]})


        self.create_menu()


    def create_menu(self):
        self.menubar = Menu(self.master)
        self.master['menu'] = self.menubar
        menu = Menu(self.menubar)
        self.menubar.add_cascade(menu=menu, label='File')
        menu.add_command(label='Open image', command= self.Start )
        #menu.add_command(label='Tdest Olot', command= make_report )

    def Start(self):
        #'''otevira soubor z disku a inicializuje praci se vzorkem, a cte exif s fotky'''
        self.file_name =  askopenfilename(initialdir = "~/",title = "choose your file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))

        try:
            image = Image.open(self.file_name)
            self.exif = { PIL.ExifTags.TAGS[k]: v  for k, v in image._getexif().items()  if k in PIL.ExifTags.TAGS}
        except:
            print('bad file: {0}'.format(self.file_name))
            self.exif = { }



        ratio = image.width/image.height
        self.canvas_height = 720
        self.canvas_width = int(self.canvas_height*ratio)

        self.image = image.resize((int((self.canvas_height)*ratio),self.canvas_height),resample = Image.LANCZOS)

        self.create_canvas()

        self.d= Start_Dialog(self,{'Measure':20e-6, "pixels": self.px},title='Enter Units in [m]',meassure_action = True)

        if self.d.result:
            self.Measure = self.d.result.get('Measure')
        else:
            self.Start()




        if self.d.result.get('pixels') :
            self.px = int(self.d.result.get('pixels'))
            self.on_button_release(None)
        else:
            self.label3text.set( "Draw  line with mouse to measure mark on the image")
            self.message = Label( self.master, textvariable = self.label3text )
            self.message.pack( side = BOTTOM )



    def create_canvas(self):
        try:
            #'''pokid platno existuje tak jej zlikviduje a vytvori nove'''
            self.w.destroy()
            self.message.destroy()
        except:
            pass

        self.w = Canvas(self.master,width=self.canvas_width,height=self.canvas_height)
        self.w.pack(expand = YES, fill = BOTH)
        self.w.bind("<ButtonPress-1>", self.on_button_press)
        self.w.bind("<ButtonRelease-1>", self.on_button_release)
        self.w.image = ImageTk.PhotoImage(self.image)
        self.w.create_image(0,0, image = self.w.image, anchor='nw')

    def on_button_press(self, event):
        self.master.title( "Get area of selected region version:0.1: " + self.file_name )
        self.x = event.x
        self.y = event.y

    def on_button_release(self, event):

        if event :
            x0,y0 = (self.x, self.y)
            x1,y1 = (event.x, event.y)
            self.w.create_line(x0,y0,x1,y1, fill="black")
            self.px= abs(x0 - x1)

        self.w.unbind("<ButtonPress-1>")
        self.w.unbind("<ButtonRelease-1>")
        self.w.bind( "<B1-Motion>", self.paint )
        self.label3text.set( "Press and Drag the mouse to draw area to estimate its Area. Data are recorded to file Area.csv in your home directory")

    def paint(self,event):

        self.curr = [event.x,event.y]

        self.re_initiate_draw_area()

        x1, y1 = ( event.x - 1 ), ( event.y - 1 )
        x2, y2 = ( event.x + 1 ), ( event.y + 1 )


        self.coordinates.append(self.curr)
        #obj = {'type':'Polygon',
        #       'coordinates':[self.coordinates + [self.coordinates[0]]]}
        #self.Area = (area(obj)*(float(self.Measure)/self.px)**2)*self.calibration
        self.Area = self.PolyArea()*(float(self.Measure)/self.px)**2
        cor = self.curr + self.prev
        self.lines[self.count].append(self.w.create_line(*cor, fill="red"))
        self.ovals[self.count].append(self.w.create_oval( x1, y1, x2, y2, fill = self.oval_color ))
        self.prev = self.curr
        print(self.PolyArea())
        self.label3text.set( "area = {0} [m^2], measure = {1} [m] => pixels = {2} [px]".format(self.Area, self.Measure, self.px) )

    def re_initiate_draw_area(self):
        if self.lines.get(self.count) == None or self.coordinates == []:
            self.oval_color = "yellow"
            self.prev  = self.start = self.curr
            self.lines[self.count] = []
            self.ovals[self.count] = []
            self.w.bind("<ButtonRelease-1>",self.save)

    def PolyArea(self):
        x = []
        y = []
        for a in self.coordinates:
            x.append(a[0])
            y.append(a[1])
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

    def close_line_and_label_area(self,event):
        self.lines[self.count].append(self.w.create_line(*(self.curr + self.start), fill="blue"))

        self.d = Start_Dialog(self,{'Type':self.Type})
        if self.d.result == None:
            print(self.ovals[self.count][1])
            for i in  self.ovals[self.count]: self.w.delete(i)
            for i in  self.lines[self.count]: self.w.delete(i)
            self.coordinates = []
            return False


        self.Type = self.d.result['Type']
        self.d.result['Area'] = self.Area
        self.d.result['measure'] = self.Measure
        self.d.result['count'] = self.count
        self.d.result['file_name'] = self.file_name
        self.d.result['coordinates'] = self.coordinates
        self.d.result['datetime'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
        self.d.result['image_data'] = self.exif
        self.w.create_text(self.start[0]  -10, self.start[1]  -10 , text = "{count}: {Type}: {Area:.2E}".format(**self.d.result))

        return True

    def save(self, event):
        if self.close_line_and_label_area(event) == False:
            return

        self.Data.append(self.d.result)
        f=open(home +'/area.csv','a')
        f.write('{datetime},{file_name},{count},{Area:.8E};{measure},{Type},"{0}"\n'.format(str(self.exif),**self.d.result))
        f.close()
        self.w.update()
        self.w.postscript(file="{0}.ps".format(self.file_name), colormode='color')
        self.count += 1
        self.coordinates = []
        self.prev = []


class process_data():
    def __init__(self,Data):
        self.DATA = {}

    def Process_Data(self):
        for item in self.Data:
            if  self.DATA.get(item['type']) == None:
                self.DATA[item['type']] = [item['Area']]
            else:
                self.DATA[item['type']].append(item['Area'])

    def make_report(self):
        pass


if __name__ == "__main__":
        #'''pokud se spusti soubor z prikazove radky tak se vykonna jinak se ignoruje'''
        root = Tk()
        App(root)
        root.title( "Get area of selected region version:0.1 " )
        mainloop()
