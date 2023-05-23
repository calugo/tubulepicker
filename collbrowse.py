# Carlos A Lugo. 2023 Sainsbury Laboratory - University of Cambridge.
"""
Synopsis
    Deploys a GUI which allows to load tiff stacks of images of Microtubular Cortexes, browse through each frame and select points which define the angle between colliding Microtubules. 
    The events can be annotated by K-catastrophe, X-Crossing, U-undefined, Z-zippering.
    The results are stored in a CVS file.
"""

from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from glob import glob
from skimage import io
from skimage import color
from PIL import Image,ImageTk
import numpy as np
import csv
import operator
import pandas as pd


root = Tk()
#root.attributes('-zoomed',True)
root.title('Tiff-Picker')
m=0
n=0
global count, zoomst
zoomst = 0
count=0
countx = 0
points=[]
EList=['X','K','Z','U']
EListx=['ALL','X','K','Z','U']
global shcase
shcase='ALL'
#Scale factors
global lj,xi,xf,yi,yf
global LH,lh,DLH

#The transform L is 800 for zooms
LH=800 #Screen Image length
lh=512 #TIFF Image length
lj=LH/lh
DLH=LH
#Scale and slice factors of the original 512x512 image array
xi=0
xf=800
yi=0
yf=800
ax=0
bx=512
ay=0
by=512
###############################
btnframe=Frame(root)
#btnframe.pack()
btnframe.grid(column=0,row=0)

cnvframe=Frame(root)
cnvframe.grid(column=0, row=1,sticky='w')
#cnvframe.pack()

imframe=Frame(root)
#imframe.pack()
imframe.grid(column=0,row=2)

current_value = DoubleVar()
brvalue= DoubleVar()
anglevalue= DoubleVar()
colvalue= StringVar(root)
colvalue.set("Collision-type")

colvaluex= StringVar(root)
colvaluex.set("Show-Only")


global allyn
allyn=BooleanVar()
allyn.set(True)

global ecolors
ecolors = {'X':'orange', 'K':'red','Z':'white','U':'yellow'}


canvas=Canvas(cnvframe,bg='black',height=800,width=800)
canvas.grid(column=0,row=0,sticky='W',rowspan=3)

####
#Treeview 
Wn=70
table_pd = ttk.Treeview(cnvframe)
#table_pd['columns']=("X1","Y1","X2","Y2","X3","Y3","Angle","Event","Frame","Zoom")
table_pd['columns']=("X1","Y1","X2","Y2","X3","Y3","Angle","Event","Frame")
table_pd.column("#0",width=0,stretch=NO)
table_pd.column("X1",anchor=W,width=Wn)
table_pd.column("Y1",anchor=W,width=Wn)
table_pd.column("X2",anchor=W,width=Wn)
table_pd.column("Y2",anchor=W,width=Wn)
table_pd.column("X3",anchor=W,width=Wn)
table_pd.column("Y3",anchor=W,width=Wn)
table_pd.column("Angle",anchor=W,width=Wn)
table_pd.column("Event",anchor=W,width=Wn)
table_pd.column("Frame",anchor=W,width=Wn)
#table_pd.column("Zoom",anchor=W,width=Wn)

table_pd.heading("#0",text="",anchor=W)
table_pd.heading("X1",text="X1",anchor=W)
table_pd.heading("Y1",text="Y1",anchor=W)
table_pd.heading("X2",text="X2",anchor=W)
table_pd.heading("Y2",text="Y2",anchor=W)
table_pd.heading("X3",text="X3",anchor=W)
table_pd.heading("Y3",text="Y3",anchor=W)
table_pd.heading("Angle",text="Angle",anchor=W)
table_pd.heading("Event",text="Event",anchor=W)
table_pd.heading("Frame",text="Frame",anchor=W)
#table_pd.heading("Zoom",text="Zoom",anchor=W)

table_pd.grid(column=3,row=0,sticky=NW,rowspan=3,columnspan=5)

####

#####Callbacks
def patcharray(NF,Ox,Oy,imx):
    A1=int((512-Ox)*0.5)
    A2=int((512-Oy)*0.5)
    print(NF,Ox,Oy)
    Z=np.zeros((NF+1,512,512))
    print(imx.shape,Z.shape)
    for j in range(NF):
        Z[j,A1:(A1+Ox),A2:(A2+Oy)]=imx[j,:,:]
    return Z

    

def angle(points):
    #print(points)
    XA=points[1][0]-points[0][0]
    YA=points[1][1]-points[0][1]
    XB=points[1][0]-points[2][0]
    YB=points[1][1]-points[2][1]
    PDOT=XA*XB+YA*YB
    RA=np.sqrt(XA*XA+YA*YA)
    RB=np.sqrt(XB*XB+YB*YB)
    theta=np.arccos(PDOT/(RA*RB))
    #print(theta)
    return theta

def open_csv():
    global canvas,imtiff,image,xi,xf,yi,yf
    global ax,bx,ay,by, movname
    root.filename = fd.askopenfilename(initialdir='.', title="Choose File",  filetypes=(("All files","*.*"),("tiff","*.tiff")))
    print(root.filename)
    r1=root.filename.endswith('.tiff')
    r2=root.filename.endswith('.tif')
    global NFR
    if (r1 or r2):
        if r1:
            movname=root.filename
            imtiff=io.imread(root.filename)
            imtiff = (imtiff >> 8).astype('uint8')
            im=imtiff[0,ax:bx,ay:by]
            NFR = imtiff.shape[0]-1
            image = Image.fromarray(im)
            image = image.resize((800,800),Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            canvas.create_image(400,400, anchor=CENTER, image=image)
        if r2:
            movname=root.filename
            imtiff=100*color.rgb2gray(io.imread(root.filename))
            print(imtiff.shape)
            #imtiff = (imtiff >> 8).astype('uint8')
            im=imtiff[0,ax:bx,ay:by]
            NFR = imtiff.shape[0]-1
            Ox= imtiff.shape[1]
            Oy= imtiff.shape[2]
            if Ox!=512 or Oy!=512:
                imtiff=patcharray(NFR,Ox,Oy,imtiff)
            im=imtiff[0,ax:bx,ay:by]
            image = Image.fromarray(im)
            image = image.resize((800,800),Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            canvas.create_image(400,400, anchor=CENTER, image=image)
    else:
        print("Try a tiff or tif stack file")

def save_csv():
    global FN,shcase,told
    
    Q=colvaluex.get()
    FNC=movname.split('/')
    FND=FNC[len(FNC)-1]

    if 'FN' in globals():
        FNA=FN.split('/')
        FNB=FNA[len(FNA)-1]
 
        print(FNB,FND)
        print(FN,shcase,shcase+FN,colvaluex.get(),movname,'hi')
    else:
        FNB='Session.csv'
        print(FNB,shcase,shcase+FNB,colvaluex.get(),movname,'hi')
        print(FNB,FND)


    if (Q in ['ALL', "Show-Only"]):

        with open(FNB,"w",newline="") as save_file:
            csvwriter = csv.writer(save_file, delimiter=",")
            for row_id in table_pd.get_children():
                row = table_pd.item(row_id)['values']
                print('save_row:',row)
                csvwriter.writerow(row)

    #told=[table_pd.item(j)['values'] for j in table_pd.get_children()]
    
    if Q in ['K','U','Z','X']:
        with open(FNB,"w",newline="") as save_file:
            csvwriter = csv.writer(save_file, delimiter=",")
            for k in told:
                print('save_row',k)
                csvwriter.writerow(k)
    
    
    with open("INFO"+FNB,"w") as save_file:
            print("INFO"+FNB)
            print("INFO"+FNB)
            print("INFO"+FNB)
            print("INFO"+FNB)
            print("INFO"+FNB)
            print(FNB+'-'+FND)
            save_file.write(FNB+'-'+FND)

    #print(FN)
    #with open(FN,"w",newline="") as save_file:
    #    csvwriter = csv.writer(save_file, delimiter=",")
    #    for row_id in table_pd.get_children():
    #        row = table_pd.item(row_id)['values']
    #        print('save_row:',row)
    #        csvwriter.writerow(row)

def load_csv():
    global FN, csvdata
    root.filename = fd.askopenfilename(initialdir='.', title="Choose File",  filetypes=(("All files","*.*"),("csv","*.csv")))
    FN=root.filename
    with open(root.filename) as load_file:
        csvread = csv.reader(load_file, delimiter=',')
        csvdata = pd.read_csv(load_file,header=None)
        csvdata = csvdata.sort_values(8)
        for index, row in csvdata.iterrows():
            u=[row[j] for j in range(9)]
            print('load row:',u)
            table_pd.insert("", 'end', values=u)
    plot_angles()



def framen(event):
    global canvas,imtiff,image,brth,xi,xf,yi,yf
    global ax,bx,ay,by,allyn, NFR
    m=int(event)
    #print(m)
    if m>NFR:
        m=NFR
    im=float(brth.get())*imtiff[m,ax:bx,ay:by]
    image = Image.fromarray(im)
    image = image.resize((800,800),Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(400, 400, anchor=CENTER, image=image)
    plot_angles()
    

def setbr(event):
    global canvas,imtiff,image,frn,xi,xf,yi,yf
    global ax,bx,ay,by
    K=int(frn.get())
    #print(K,float(event))
    im=float(event)*imtiff[K,ax:bx,ay:by]
    image = Image.fromarray(im)
    image = image.resize((800,800),Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(400, 400, anchor=CENTER, image=image)
    plot_angles()

def get_xy_zoom(event):
    global sx,sy,countx
    if countx==0:
        sx,sy = event.x, event.y
    countx+=1

def zoom_sq(event):
    global sx, sy, countx,canvas,lj,xi,xf,yi,yf,ax,bx,ay,by
    global N1x,N1y,DLH

    canvas.create_oval(event.x-5,event.y-5,event.x+5,event.y+5,fill='',outline='yellow')
    if countx==2:
        N1x=sx 
        N1y=sy
        N2x= event.x
        DLH=N2x-N1x
        print("****")
        print("****")
        #TRANSTEST
        u1x=N1x
        u1y=N1y
        u2x=N2x
        u2y=N1y+DLH

        xi=u1x
        yi=u1y
        xf=u2x
        yf=u2y

        print(u1x,u2x,DLH)
        print(u1y,u2y,DLH)
        print("****")
        print("****")
        canvas.create_rectangle(N1x,N1y,N2x,N1y+DLH,outline='yellow')
        ay=int(np.floor(N1x/lj))
        by=int(np.floor((N1x+DLH)/lj))
        ax=int(np.floor(N1y/lj))
        bx=int(np.floor((N1y+DLH)/lj))

def plot_angles():
    global canvas,frn,xi,xf,yi,yf,csvdata,ecolors
    jnx=frn.get()
    #QN=csvdata.loc[csvdata[8]==jnx]

    for row_id in table_pd.get_children():
            row = table_pd.item(row_id)['values']
            if row[8]==jnx:
                pax,pay = Transfcoords(float(row[0]) , float(row[1]) )
                pbx,pby = Transfcoords(float(row[2]) , float(row[3]) )
                pcx,pcy = Transfcoords(float(row[4]) , float(row[5]) )
                canvas.create_rectangle(pax-5,pay-5,pax+5,pay+5,fill='',outline=ecolors[row[7]])
                canvas.create_oval(pbx-5,pby-5,pbx+5,pby+5,fill='',outline=ecolors[row[7]])
                canvas.create_oval(pcx-5,pcy-5,pcx+5,pcy+5,fill='',outline=ecolors[row[7]])
                canvas.create_line((pax,pay,pbx,pby),fill='yellow',width=0.1)
                canvas.create_line((pbx,pby,pcx,pcy),fill='yellow',width=0.1)
    
def replotframe():
    global canvas,imtiff,image,frn,xi,xf,yi,yf
    global ax,bx,ay,by,allyn
    K1=int(frn.get())
    K2=float(brth.get())
    im=K2*imtiff[K1,ax:bx,ay:by]
    image = Image.fromarray(im)
    image = image.resize((800,800),Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    canvas.create_image(400, 400, anchor=CENTER, image=image)
    if allyn.get() == True:
        allyn.set(False)
        #show_sel()
    else:
        allyn.set(True)
        plot_angles()
    


def zoom_out():
    global xi,xf,yi,yf,countx
    global ax,bx,ay,by,DLH
    xi=0
    xf=800
    yi=0
    yf=800
    ax=0
    bx=512
    ay=0
    by=512
    DLH=LH
    countx=0
    replotframe()
    plot_angles()

def zoom_in():
    global xi,xf,yi,yf,countx
    replotframe()
    plot_angles()

def get_xy(event):
    global lx, ly, points
    lx,ly = event.x,event.y
    points.append((lx,ly))

def Abscoords(xn,yn):
    global xi,yi,DLH,LH,lh,lj
    #global g1x,g1y,g2x,g2y
    kj=1.0/lj
    qlj=DLH/LH
    px = kj*(xi+qlj*xn) 
    py=  kj*(yi+qlj*yn)
    print(px,py)
    return px,py

def Transfcoords(xn,yn):
    global xi,yi,DLH,LH,lh,lj
    kj=lj
    qlj=LH/DLH
    px = qlj*(xn*kj-xi)
    py = qlj*(yn*kj-yi)
    return px,py 

def click_count(event):
    global n, lx,ly,points,canvas,count
    n+=1
    #print(n)
    canvas.create_oval(event.x-5,event.y-5,event.x+5,event.y+5,fill='',outline='blue')
    if n%3==0:
        ptabs=[]
        ############Below is for tests-remove once it is properly checked
        pttrans=[]
        for pt in points:
            #print(pt)
            ux,uy = Abscoords(pt[0],pt[1])
            #print(ux,uy)
            ptabs.append((ux,uy))
        for pt in ptabs:
            ux,uy = Transfcoords(pt[0],pt[1])
            pttrans.append((ux,uy))
        print("********")
        print(points)
        print(ptabs)
        print(pttrans)
        print("********")
        ##################
        K=int(frn.get())
        canvas.create_line((points[0][0],points[0][1],points[1][0],points[1][1]),fill='yellow',width=0.1)
        canvas.create_line((points[1][0],points[1][1],points[2][0],points[2][1]),fill='yellow',width=0.1)
        phi=angle(points)
        table_pd.insert(parent='',index='end',iid=count,values=(ptabs[0][0],ptabs[0][1],ptabs[1][0],ptabs[1][1],
                        ptabs[2][0],ptabs[2][1],phi,'U',K))
        count+=1
        n=0
        points=[]

def coll_option(event):  
    global count, table_pd
    sel = table_pd.focus()
    #print(sel,event)
    table_pd.set(sel, column="Event", value=event)

def del_row():
    global count, table_pd
    q=table_pd.selection()[0]
    table_pd.delete(q)
    replotframe()
    plot_angles()

def show_sel():
    global canvas,frn,xi,xf,yi,yf
    q=table_pd.selection()
    for p in q:
        #print(p.values)
        row = table_pd.item(p)['values']
        print(row)
        pax,pay = Transfcoords(float(row[0]) , float(row[1]) )
        pbx,pby = Transfcoords(float(row[2]) , float(row[3]) )
        pcx,pcy = Transfcoords(float(row[4]) , float(row[5]) )

        canvas.create_rectangle(pax-5,pay-5,pax+5,pay+5,fill='',outline=ecolors[row[7]])
        canvas.create_oval(pbx-5,pby-5,pbx+5,pby+5,fill='',outline=ecolors[row[7]])
        canvas.create_oval(pcx-5,pcy-5,pcx+5,pcy+5,fill='',outline=ecolors[row[7]])
        canvas.create_line((pax,pay,pbx,pby),fill='yellow',width=0.1)
        canvas.create_line((pbx,pby,pcx,pcy),fill='yellow',width=0.1)

def go_frame():
    #global canvas,frn,xi,xf,yi,yf,imtiff
    global canvas,imtiff,image,frn,xi,xf,yi,yf
    global ax,bx,ay,by,allyn

    q=table_pd.selection()
    for p in q[0:1]:
        row = table_pd.item(p)['values']
        fnq=row[len(row)-1]
        K1=int(fnq)
        frn.set(fnq)
        K2=float(brth.get())
        im=K2*imtiff[K1,ax:bx,ay:by]
        image = Image.fromarray(im)
        image = image.resize((800,800),Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        canvas.create_image(400, 400, anchor=CENTER, image=image)
    plot_angles()


def clear_table():
    global table_pd
    for j in table_pd.get_children():
        table_pd.delete(j)

def event_option(event):
    global table_pd, csvdata,told
    global shcase

    print(event,shcase)
    
    if (shcase=='ALL') and (event in ['K','U','Z','X']):
        told=[table_pd.item(j)['values'] for j in table_pd.get_children()]
        clear_table()
        for k in told:
            if k[7]==event:
                table_pd.insert("", 'end', values=k)
            shcase=event

    if (event in ['ALL','K','U','Z','X']) and (shcase in ['K','U','Z','X']):
        clear_table()
        for k in told:
            if event=='ALL':
                table_pd.insert("", 'end', values=k)
            else:
                if k[7]==event:
                    table_pd.insert("", 'end', values=k)

        shcase=event


####################################

canvas.bind("<Button-1>",get_xy)
canvas.bind("<ButtonRelease-1>",click_count)


canvas.bind("<Button-3>",get_xy_zoom)
canvas.bind("<ButtonRelease-3>",zoom_sq)


####NEW-SAVE-LOAD-BUTTONS 
nw_btn=Button(btnframe,text='New/Load-TIFF',fg="red",activebackground = "red",command=open_csv)  
nw_btn.pack(side = LEFT)  
  
sv_btn = Button(btnframe, text="Save", fg="brown", activebackground = "brown",command=save_csv)  
sv_btn.pack(side = RIGHT)

ld_btn = Button(btnframe, text="Load-CSV", fg="white", activebackground = "white",command=load_csv)  
ld_btn.pack(side = RIGHT) 

#######################
### Sliders
frn = Scale(imframe,from_=0, to = 299, orient=HORIZONTAL,command=framen,variable=current_value)
frn.set(0)
frn.pack()

brth = Scale(cnvframe,from_=1, to=10,resolution=0.5,orient=VERTICAL,command=setbr,variable=brvalue)
brth.set(1.0)
brth.grid(column=2,row=0)

anglerange = Scale(cnvframe,from_=np.pi/20, to=np.pi, resolution=(np.pi/20),orient=VERTICAL,variable=anglevalue)
anglerange.set(np.pi)
anglerange.grid(column=2,row=1)
#########################
###TOOL BUTTONS

collmenu=OptionMenu(cnvframe,colvalue,*EList,command=coll_option)
collmenu.grid(column=3,row=1,sticky=W)

RecButt = Button(cnvframe, text='Reset-View',command=zoom_out)
RecButt.grid(column=4,row=1,sticky=W)
DelButt = Button(cnvframe, text='Zoom-In', command=zoom_in)
DelButt.grid(column=5,row=1,sticky=W)
HideAll = Button(cnvframe, text='Hide/Show-All', command=replotframe)
HideAll.grid(column=6,row=1,sticky=W)
DrawSel = Button(cnvframe, text='Remove-row',command=del_row)
DrawSel.grid(column=7,row=1,sticky=W)

#####
MoreA = Button(cnvframe, text='Show-selected',command=show_sel)
MoreA.grid(column=3,row=2,sticky=W)
MoreB = Button(cnvframe, text='Go to sel-frame',command=go_frame)
MoreB.grid(column=4,row=2,sticky=W)
MoreC = Button(cnvframe, text='More3')#,command=clear_table)
MoreC.grid(column=6,row=2,sticky=W)

eventmenu=OptionMenu(cnvframe,colvaluex, *EListx,command=event_option)
eventmenu.grid(column=5,row=2,sticky=W)

MoreE = Button(cnvframe, text='More4')
MoreE.grid(column=7,row=2,sticky=W)


#######################################
root.bind("<Left>", lambda e:frn.set(frn.get()-1) )
root.bind("<Right>", lambda e:frn.set(frn.get()+1) )

root.bind("<Up>", lambda e:brth.set(brth.get()-0.5) )
root.bind("<Down>", lambda e:brth.set(brth.get()+0.5) )

root.mainloop()
