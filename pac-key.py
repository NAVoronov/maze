#http://www.ilnurgi1.ru/docs/python/modules/tkinter/canvas.html
#http://ideafix.name/wp-content/uploads/2012/07/Python-11.pdf
#https://ru.wikiversity.org/wiki/%D0%9A%D1%83%D1%80%D1%81_%D0%BF%D0%BE_%D0%B1%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B5_Tkinter_%D1%8F%D0%B7%D1%8B%D0%BA%D0%B0_Python#.D0.9F.D1.80.D0.B8.D0.B2.D1.8F.D0.B7.D0.BA.D0.B0_.D1.81.D0.BE.D0.B1.D1.8B.D1.82.D0.B8.D0.B9

from tkinter import *
import time
import random

random.seed() #запуск рандомайзера

window=Tk()
window.title("Эксперименты с ТК")
#window.geometry(str(window.winfo_screenwidth()-20)+"x"+str(window.winfo_screenheight()-80)+"+1+1")
window.wm_state('zoomed')
#window.attributes('-fullscreen',1)
window.minsize(width=800, height=600)

fr_color = 'green'

fr_up = Frame(window)
fr_up.pack(fill='both', side=TOP, expand='yes')

fr = Frame(fr_up)

txt = Text(fr_up)
txt["width"] = 50

fr.pack(fill='both', side=LEFT, expand='yes')
##txt.pack(fill='y', side=RIGHT)


c = Canvas(fr, bg=fr_color)#, width=WIDTH, height=HEIGHT, bg="#003300")
c.pack(fill='both', expand='yes')
c.focus_set()

#кол-во ячеек по Х и по У
kol_x=kol_y=0
#в какой ячейке ПАК
pac_x = pac_y=0
#ширина и высота фрейма
w=h=0

event=None

EXIT = -1

#check менюшка в попапе
check=BooleanVar()
check.set(True)

m_x=m_y=0
sn_color = 'yellow'

circ=0
eye=0
size=50

delta_x=delta_y=0

Key=0

# событие перемещения и его частота
aft=None
freq=200

# типы движений
md={'Left'  : {'start' : 200, 'move' : (-1, 0), 'arr' : "first"},
    'Right' : {'start' : 20 , 'move' : (1, 0 ), 'arr' : "last"},
    'Up'    : {'start' : 110, 'move' : (0, -1), 'arr' : "first"},
    'Down'  : {'start' : 290, 'move' : (0, 1 ), 'arr' : "last"},
    'mouse'  : {'start' : 20, 'move' : (0, 0 )}
    }

# сам лабиринт
maze=[]

# массив шагов ПАКа при прохождении лабиринта. когда я уже всё как следует в класс оформлю ???
steps=[]

#ячейка лабиринта
class cell:
    def __init__(self, up, down, left, right, x=0, y=0):
        self.m={'Left'  : left, 'Right' : right, 'Up'    : up, 'Down'  : down, 'mouse':0}
        self.s={'Left'  : left, 'Right' : right, 'Up'    : up, 'Down'  : down}
        self.x=x
        self.y=y
        self.rect=None
        self.intsecnum=self.x + (self.y-1)*kol_x

        self.type=0

    def summ(self):
        return int(not self.m["Left"]) + int(not self.m["Right"]) + int(not self.m["Up"]) + int(not self.m["Down"])

    def draw(self):
        s=size*2
        if self.m["Up"] == 0    : c.create_line(delta_x+(self.x-1)*s, delta_y+(self.y-1)*s, delta_x+self.x*s,     delta_y+(self.y-1)*s, tag='mesh')
        if self.m["Down"] == 0  : c.create_line(delta_x+(self.x-1)*s, delta_y+self.y*s,     delta_x+self.x*s,     delta_y+self.y*s,     tag='mesh')
        if self.m["Left"] == 0  : c.create_line(delta_x+(self.x-1)*s, delta_y+(self.y-1)*s, delta_x+(self.x-1)*s, delta_y+self.y*s,     tag='mesh')
        if self.m["Right"] == 0 : c.create_line(delta_x+self.x*s,     delta_y+(self.y-1)*s, delta_x+self.x*s,     delta_y+self.y*s,     tag='mesh')

        #c.create_text((self.x-1)*s+s/3, (self.y-1)*s+s/4, text = "y="+str(self.y), tag='mesh')
        #c.create_text((self.x-1)*s+s/3, (self.y-1)*s+s/1.5, text = "x="+str(self.x), tag='mesh')

##        c.create_text((self.x-1)*s+s/1.5, (self.y-1)*s+s/1.5, text = str(self.intsecnum), tag='mesh')
##
##        c.create_text((self.x-1)*s+s/1.5, (self.y-1)*s+s/4, text = self.s["Up"], tag='mesh')
##        c.create_text((self.x-1)*s+s/1.5, (self.y-1)*s+s/1, text = self.s["Down"], tag='mesh')
##        c.create_text((self.x-1)*s+s/3, (self.y-1)*s+s/1.5, text = self.s["Left"], tag='mesh')
##        c.create_text((self.x-1)*s+s/1.1, (self.y-1)*s+s/1.5, text = self.s["Right"], tag='mesh')

#--------порисуем лабиринт-------------------------------------------------------------------------------
def mesh():
    c.delete("mesh")
    for row in maze :
        for col in row : col.draw()
#-----------------------------------------------------------------        

#--------------сгенерировать лабиринт-------------------------------------------------------------------------
def aMAZeing():
    global maze

    try:
        txt.delete('1.0', END)
    except:
        pass
    
    c.delete("arr")
    #c.delete("mesh")
    maze.clear()

    #для начала проставим все перекрёстки и ограничим низ верх лево право
    wall=cell(0,0,0,0,0,0) #начальные ячейки непроходимы (up down left right)
    maze.append( [wall] * (kol_x+1) ) #это верхняя стена
    for y in range(1, kol_y+1):
        maze.append([]) #добавляем новую строку
        maze[y].append(wall)# слева там стена        
        for x in range(1, kol_x+1):
            l=u=0
            if x !=1 : l  = x-1 + (y-1)*kol_x
            if y !=1 : u  = x + (y-2)*kol_x
            d   = x + y*kol_x
            r = x+1 + (y-1)*kol_x
            maze[y].append( cell(u,d,l,r,x,y) )
        #у конечной клетки правая стена глухая
        maze[y][x].m["Right"]=0
    #у последнего ряда низ глухой
    for j in maze[y]: j.m["Down"]=0  

    #а теперь попробуем стен наставить
    for y in range(1, kol_y+1):
        for x in range(1, kol_x+1):
            d=r=0
            d = random.randint(0,1) #нижняя случайная
            # если 2 стены уже есть - вверху и слева, то внизу и справа не надо
            if (maze[y-1][x].m["Down"] == maze[y][x-1].m["Right"] == 0):
                d = x + y*kol_x # внизу ставим проход в узел
                r = x + (y-1)*kol_x + 1 # справа тоже узел открыт
            elif d == 0: #если верх или лево открыты, то можно попробовать снизу стенку прикрутить
                maze[y][x].m["Down"]=maze[y][x].s["Down"]=d
                if y!=kol_y: maze[y+1][x].m["Up"]=maze[y+1][x].s["Up"]=d
            else : # 
                r = random.randint(0,1)
                if r == 0: 
                    maze[y][x].m["Right"]=maze[y][x].s["Right"]=r
                    if x!=kol_x: maze[y][x+1].m["Left"]=maze[y][x+1].s["Left"]=r
    # и нарисуем        
    mesh()    
#-----------------------------------------------------------------

   
#--------------тут движуха Пака---------------------------------------------------------
def mov(where=''):
    #кнопки только нужные берём
    if where not in md.keys(): return
    
    global pac_x, pac_y, Key, aft, m_x, m_y, check

    #вычисляем куда бежать по мыши
    if (where == 'mouse'):
        if   m_x < pac_x : where = "Left"
        elif m_x > pac_x : where = "Right"
    if (where == 'mouse'):
        if   m_y < pac_y : where = "Up"
        elif m_y > pac_y : where = "Down"

    c.delete(eye)
    c.itemconfig(circ, start=md[where]['start'])

    #если стена - стопэ !
    if maze[pac_y][pac_x].m[where] == 0 :
        Key=0
        if aft!=None: window.after_cancel(aft)
        aft=None
        return 1

    #оставляем следы или нет
    if check.get() == 1:
        s=size*2
        if where in ["Left","Right"]:
            maze[pac_y][pac_x].rect = c.delete(maze[pac_y][pac_x].rect)
            maze[pac_y][pac_x].rect = c.create_line(delta_x+(pac_x-1)*s+size/2, delta_y+(pac_y-1)*s+size,
                                 delta_x+(pac_x-1)*s+size,   delta_y+(pac_y-1)*s+size, tag='arr', arrow=md[where]['arr'])        
        else:
            maze[pac_y][pac_x].rect =  c.delete(maze[pac_y][pac_x].rect)
            maze[pac_y][pac_x].rect = c.create_line(delta_x+(pac_x-1)*s+size, delta_y+(pac_y-1)*s+size/2,
                                 delta_x+(pac_x-1)*s+size, delta_y+(pac_y-1)*s+size, tag='arr', arrow=md[where]['arr'])
        
    pac_x+=md[where]['move'][0]
    pac_y+=md[where]['move'][1]
    
    window.update_idletasks()
    c.move(circ, md[where]['move'][0]*size*2, md[where]['move'][1]*size*2)

    #цель достигнута
    if (pac_x, pac_y) == (m_x, m_y) :
        if aft!=None : window.after_cancel(aft)
        aft=None
        m_x=m_y=0
        return 2

    return 0
#-------------------------------------------------------------------------    

#--------------нажали кнопку и пусть бежит-----------------------------------------------------------
def go_key():
    global aft
    aft=window.after(freq, go_key )
    mov(Key)
#-------------------------------------------------------------------------    
    
#-----------смотрим что нажато--------------------------------------------
def kp(e):
    global aft, Key

    if aft != None:
        window.after_cancel(aft)
        aft=None

    if e.keysym == "F5" : aMAZeing()

    #kl["text"]=" | чо нажали : keycode="+str(e.keycode)+" char="+str(e.char)+" keysym="+str(e.keysym)+" keysym_num="+str(e.keysym_num )
    Key = e.keysym
    go_key()
#-------------------------------------------------------------------------

#--------------тут попробуем побегать за мышкой-----------------------------------------------------------
def go():
    global aft
    aft=window.after(freq, go )
    mov("mouse")
#-------------------------------------------------------------------------

#-------------------отрабатываем движуху мышки----------------------------
def move(e):
    pass
#-------------------------------------------------------------------------

#----------------- генерация и Отрисовка лабиринта с ПАКом при изменении масштаба-------------------------------------------------------
def dr_m(width, height):
    global circ, eye, kol_x, kol_y, pac_x, pac_y, delta_x, delta_y
    
    c.delete('pac')
    c.delete('eye')
    c.delete('arr')

    kol_x, delta_x = divmod(width, (size*2))
    kol_y, delta_y = divmod(height,(size*2))

    delta_x //= 2
    delta_y //= 2
        
    aMAZeing()

    pac_x = pac_y = 1
##    pac_x = (kol_x//2)
##    pac_y = (kol_y//2)

    circ=c.create_arc(delta_x+(pac_x-1)*2*size, delta_y+(pac_y-1)*2*size, delta_x+pac_x*2*size, delta_y+pac_y*2*size, fill=sn_color, tags="pac", style='pieslice', start=20, extent=320)
#-------------------------------------------------------------------------
    
#------------------------изменения в размерах окна------------------------
def res(e):
    fr["width"] = e.width
    fr["height"] = e.height
    dr_m(e.width, e.height)  
#-------------------------------------------------------------------------

#--------------------Колесико крутим - меняем масштаб-----------------------------------------------------    
def mw(e):
    global size

    if e.delta < 0 and size > 10 :
        size-=1
        dr_m(fr["width"], fr["height"])    

    if e.delta > 0 and size < 50 :
        size+=1
        dr_m(fr["width"], fr["height"])
#-------------------------------------------------------------------------

#----------------простой алгоритм прохождения лабиринта---------------------------------------------------------
def TraverseMaze(intsecvalue, y, x):
  global maze

  if (intsecvalue > 0) :# // если не стенка
    if (intsecvalue == EXIT):
        txt.insert(INSERT, "Выход.\n")
        return 1
    else: #{ // налево        
        l = maze[y][x].s["Left"]        
        
##        maze[y][x-1].s["Right"] =0
        maze[y][x].s["Left"]=0
        
        if (TraverseMaze(l, y, x-1) == 1):
            txt.insert(INSERT, str(intsecvalue)+" перекрёсток - налево.\n")
            steps.append("Left")
            return 1

        else:# { // вверх
            u = maze[y][x].s["Up"]
            
##            maze[y-1][x].s["Down"] = 0
            maze[y][x].s["Up"]=0            
            
            if (TraverseMaze(u, y-1, x) == 1):
                txt.insert(INSERT, str(intsecvalue)+" перекрёсток - прямо.\n")
                steps.append("Up")
                return 1

            else: #{ // направо
                if x < kol_x:
                    r = maze[y][x].s["Right"]
                                        
##                    maze[y][x+1].s["Left"] = 0
                    maze[y][x].s["Right"]=0
                    
                    if (TraverseMaze(r, y, x+1) == 1):
                        txt.insert(INSERT, str(intsecvalue)+" перекрёсток - направо.\n")
                        steps.append("Right")
                        return 1

                    else: #{ // вниз
                      if y<kol_y:
                          d = maze[y][x].s["Down"]
                                                    
##                          maze[y+1][x].s["Up"] = 0
                          maze[y][x].s["Down"]=0                  
                          
                          if (TraverseMaze(d, y+1, x) == 1):
                              txt.insert(INSERT, str(intsecvalue)+" перекрёсток - назад.\n")
                              steps.append("Down")
                              return 1
                    
                # вниз сходили                
            #направо сходили                
        #вверх сходили                
      #налево сходили
                
  #проверка упора в стенку
  return 0

def MazeStart():
    global steps
    
    steps.clear()
    if TraverseMaze(maze[pac_y][pac_x].intsecnum, pac_y, pac_x) == 1 :
        steps.reverse() 
        for i in steps:
            mov(i)
            time.sleep(0.05)
    else :
        txt.insert(INSERT, "выхода нет.\n")

#-------------------------------------------------------------------------

#--------ворованная реализация прохождения у людей работало. не соображу как правда...-----------------------------------------------------------------
def setBlock(y, x):
    global maze
    
    k=maze[y][x].summ()    
    print(k)

    if maze[y][x].type==0:# чисто пока
        if k == 4: maze[y][x].type=2 # тупичок

        if k == 3:
            maze[y][x].type=2
            if maze[y-1][x].type==0: setBlock(y-1, x)
            if y < kol_y and maze[y+1][x].type==0: setBlock(y+1, x)
            if maze[y][x-1].type==0: setBlock(y, x-1)
            if x<kol_x and maze[y][x+1].type==0: setBlock(y, x+1)

def setallblocks():
    for y in range(1, kol_y):
        for x in range(1, kol_x):
            setBlock(y, x)

    mesh()
#-------------------------------------------------------------------------

#--------волны - странный алгоритм какойто полурабочий он...-----------------------------------------------------------------
def wave(y, x, w):
    global maze

    maze[y][x].type=w
    
    if x+1<=kol_x:
        if maze[y][x+1].type == 0 or (maze[y][x+1].m["Left"] !=0 and maze[y][x+1].type > w): wave(y, x+1, w+1)
        #if maze[y][x+1].type == 0 or maze[y][x+1].type > w : wave(y, x+1, w+1)

    if y+1<=kol_y:
        if maze[y+1][x].type == 0 or (maze[y+1][x].m["Up"] !=0 and maze[y+1][x].type > w): wave(y+1, x, w+1)
        #if maze[y+1][x].type == 0 or maze[y+1][x].type > w : wave(y+1, x, w+1)

    if y-1>0:
        if maze[y-1][x].type == 0 or (maze[y-1][x].m["Down"] !=0 and maze[y-1][x].type > w): wave(y-1, x, w+1)
        #if maze[y-1][x].type == 0 or maze[y-1][x].type > w : wave(y-1, x, w+1)

    if x-1>0:
        if maze[y][x-1].type == 0 or (maze[y][x-1].m["Right"] !=0 and maze[y][x-1].type > w): wave(y, x-1, w+1)
        #if maze[y][x-1].type == 0 or maze[y][x-1].type > w : wave(y, x-1, w+1)

def gowave():
    wave(pac_y,pac_x,1)
    mesh()

#-------------------------------------------------------------------------


#----------------------тык в клетку ЛКМ - там цель---------------------------------------------------        
def goal(e):    
    global m_x, m_y, Key, EXIT
    
    Key=0
    m_x=e.x//(size*2)+1
    m_y=e.y//(size*2)+1

    #номер перекрёстка для выхода
    EXIT = m_x + kol_x*(m_y-1)
    txt.insert (INSERT, "Выход ставим на "+str(EXIT)+"\n")

    if e.num==2: go()
    if e.num==1: MazeStart() #gowave()
#-------------------------------------------------------------------------
#---------------цель ПАКа - ставим через меню ПКМ----------------------------------------------------------
def target():
    global m_x, m_y, Key, EXIT
    Key=0
    m_x=event.x//(size*2)+1
    m_y=event.y//(size*2)+1

    #номер перекрёстка для выхода
    EXIT = m_x + kol_x*(m_y-1)
    txt.insert (INSERT, "Выход ставим на "+str(EXIT)+"\n")
#-------------------------------------------------------------------------
    
#---------------телепортация ПАКа ----------------------------------------------------------
def movPak():
    global pac_x, pac_y, circ
    c.delete('arr')

    c.delete(circ)
    
    pac_x=event.x//(size*2)+1
    pac_y=event.y//(size*2)+1

    circ=c.create_arc(delta_x+(pac_x-1)*2*size, delta_y+(pac_y-1)*2*size, delta_x+pac_x*2*size, delta_y+pac_y*2*size, fill=sn_color, tags="pac", style='pieslice', start=20, extent=320)
#-------------------------------------------------------------------------

#----------------удаляем стрелочки-направления---------------------------------------------------------
def delarr():
    command=c.delete("arr")
#-------------------------------------------------------------------------    

#-----popup менюшка---------------------------------------------------------------------------------
def pop1(e):
    global event, check

    event=e
   
    popup = Menu(fr, tearoff=0)
    popup.add_command(label="F5 - пересоздать лабиринт", command = aMAZeing)
    popup.add_command(label="Телепортировать Пака сюда", command = movPak)
    popup.add_command(label="Поставить тут цель для Пака", command = target)
    popup.add_command(label="Погулять по лабиринту",    command = MazeStart)
    popup.add_checkbutton(label="Оставлять следы", onvalue=1, offvalue=0, variable=check, command=delarr)
    popup.add_separator()
    popup.add_command(label="Alt+F4 - выход", command=window.destroy)
    
    #popup.tk_popup(e.x_root, e.y_root, 0)
    popup.post(e.x_root, e.y_root)
#-------------------------------------------------------------------------
  
frb = Frame(window)
frb["height"] = 1
frb.pack(fill='x', side=BOTTOM)

info = Label(frb)
info["text"] = "F5 - обновить лабиринт. стрелки, ПКМ, ЛКМ, колесо - управление действием. Alt+F4 - выход"
info.pack(side=LEFT)

#c.bind("<Motion>", move)#движка мышки
c.bind("<Configure>", res)#изменение размеров окна

window.bind("<KeyPress>", kp)#клава
#window.bind("<Activate>", res)
c.bind("<Button-3>", pop1) #ПКМ - менюшка
c.bind("<Button-2>", goal) #cКМ - просто побегаем за мышой
c.bind("<Button-1>", goal) #ЛКМ - зададим цель ПАКу
c.bind("<MouseWheel>", mw) # колесо

window.mainloop()
