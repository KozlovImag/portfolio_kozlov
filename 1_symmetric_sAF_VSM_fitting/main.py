# -*- coding: utf-8 -*-
"""
@author: Алексей Козлов
"""
import numpy as np
import matplotlib.pyplot as plt
import math
from datetime import datetime



### ПОЧАТОК ІНТЕРФЕЙСУ

###ІМПОРТ ЕКСПЕРИМЕНТАЛЬНИХ ДАНИХ

#назва txt файла, який містить дві колонки експериментальних данних: 
#1-ша колонка зовнішне магнітне поле [Oe] 
#2-га колонка намагніченість [будь яка розмірність]
T="380" 


### ВАЖЛИВО 
# Якщо кількість експериментальних точок замала, то будуть артефакти (ламана лінія)
# У цьому разі потрібно задати параметр dot - кількість проміжних точок для обрахунку
dot=2 


### ВІДОМІ ПАРАМЕТРИ ЗРАЗКА
d=2 # товщина зразку в [nm]
M=1100.0235 # Намагніченість A/m


###ПАРАМЕТРИ ПЕРЕБОРУ
#їх можна задати як формулой так і перчисленням через кому
a=[-math.pi/5,-math.pi]   #кути одноосної анізотропії  [в радіанах]
Quad=[-8.5+i for i in range(3)]     # біквадратична [uJ/m^2]
Linear=[-74.25]   #білінійна константа [uJ/m^2]
KU=[21.25]  # анізотропія [uJ/m^3]

#точність в радіанах з якими будуть знаходиться кути намагніченості
# для швидкого перебору можна брати досить великі значення, а потім збільшувати деталізацію
dF=0.001

# ми генеруємо серію кривих кожна із яких оптимізується на різних частинах кривої
# наприклад тут ми оптимізуємо криву на ділянках (-2000mT,2000mT), (-75mT,75mT), (-15mT,15mT)
# можна прибирати зайві або додавати нові
para=[2000,200,75]

###ВИВІД ГРАФІКУ 

## ГРАНИЦІ ГРАФІКУ
xlim=150 #x компонента x є [-xlim, xlim] 
ylim=1  # y компонента y є [-ylim, ylim]

## CТИЛІ
# Експериментальні данні завжди суцільна блактина лінія

#Кольори змодельованих кривих
colors=["red","orange","black","green"] #кольори для серіх кривих 
#Типи ліній
linestyles=["dashed"]


#### КІНЕЦЬ ІНТЕРФЕЙСУ


#### РОЗРАХУНОК

# Час початку розрахунку
start_time = datetime.now()

### ФУНКЦІЇ

# Задаємо енергію системи
def Energy(x,B):
    Zeeman=-M*B*d*(math.cos(x[0])+math.cos(x[1]))
    Exchange= -math.cos(x[0]-x[1])*(J1+J2*math.cos(x[0]-x[1]))
    Anisotropy= -K*d*(math.cos(a1-x[0])*math.cos(a1-x[0])+math.cos(a2-x[1])*math.cos(a2-x[1]))
    return  (Zeeman+1e3*(Exchange+Anisotropy))

# Рахуємо точку в VSM з кутів намагніченості
def VSM(X):
    return((M*d*np.cos(X[0])+M*d*np.cos(X[1]))/(M*d+M*d))

# Повертаємо кут по модулю PI
def modPI(x): 
    if(abs(x)>math.pi):
        return (x-(abs(x)/x)*2*math.pi)
    else:
        return x

# Пошук мінімальної енергії у суідов в сітці    
def LookAround(stop,X,value,Field,step):
    neighbor=[(X[0]+dF,X[1]),(X[0]-dF,X[1]),(X[0],X[1]+dF),(X[0],X[1]-dF),(X[0]+dF,X[1]+dF),(X[0]-dF,X[1]+dF),(X[0]-dF,X[1]-dF),(X[0]+dF,X[0]-dF) ]
    for l in range(len(neighbor)):
       (x,y)=neighbor[l]
       neighbor[l]=(modPI(x),modPI(y))
    values=[Energy(neighbor[j],Field) for j in range(len(neighbor))]
    m=min(values);
    ind=values.index(m)
    if(value>m):
        (st,Y,v)=(False,neighbor[ind],m)
    else:
        (st,Y,v)=(True,X,value)
    return (st,Y,v)

# Порівнює дві криві y(x) та z(x) на проміжку [-a,a]    
def comp(x,y,z,a):
    suma=0
    for i in range(len(x)):
        if (x[i]<a and x[i]>-a):
            suma+=(y[i]-z[i])**2     
    return suma

# Кількість кривих які будуть оптимизовані
N=len(para)

### Імпорт експ кривої
z=np.loadtxt(T+'.txt')
#розділюємо стовпчики
left=[z[i][0]/10 for i in range(len(z))] # Oe в mT
right=[z[i][1] for i in range(len(z))]
# знахидимо намагніченость насиченості
Ms=max(right)
# рахуємо M/Ms
right=[i/Ms for i in right]

#МАСИВИ ДЛЯ ЗБЕРІГАННЯ

#стандартного відхилення
standart=[len(z) for i in range(N)]
#параметрів системи 
save=[(0,0,0,0,0) for i in range(N)]
#кривих намагніченості
MainVSM=[[] for i in range(N)]

#Розділяємо данні з експерименту на два масива
# в кожному з яких B монотонно (т.е на криву від насичення до -насичення та зворотній хід) 
B1=[]
B2=[]
Y1=[]
Y2=[]
for i in range(len(left)-1):
    if(left[i]>=left[i+1]):
        B2.append(left[i]);
        Y2.append(right[i])
    else:
        B1.append(left[i])
        Y1.append(right[i])    



### ПЕРЕБІР  по першій половині петлі
X0=(0,0)
for Ku in KU:
    K=Ku
    for Angl in a:
        a1=Angl
        for Angl2 in a:
            a2=Angl2
            for BiQuad in Quad :
                J2=BiQuad
                for BiLin in Linear :
                    J1=BiLin
                    VSM1=[0 for i in range(len(B1))]
                    # в початковий момент часу (при великих B) кути намагніченості орієнтовані по полю 
                    for i in range(len(B1)):
                       check=False
                       value=Energy(X0,B1[i])
                       while not check:
                           (check,X0,value)=LookAround(check,X0,value,B1[i],i) 
                       VSM1[i]=VSM(X0)
                       if i!= (len(B1)-1):
                           for bn in range(1,dot):
                               check=False
                               value=Energy(X0,bn*(B1[i]+B1[i+1])/dot)
                               while not check:
                                   (check,X0,value)=LookAround(check,X0,value,bn*(B1[i]+B1[i+1])/dot,i)
                    for j in range(N):
                        std=comp(B1, VSM1, Y1,para[j])
                        if(std<standart[j]):
                            standart[j]=std
                            save[j]=(Ku,Angl,Angl2,BiQuad, BiLin)
                            MainVSM[j]=VSM1
                    
### ДОБУДОВА ДРУГОЇ ПОЛОВИНИ ПЕТЛІ ДЛЯ КРАЩИХ
VSM2=[[0 for i in range(len(B2))] for j in range(N)]

for j in range(len(save)):
    (K,a1,a2,J2,J1)=save[j]
    for i in range(len(B2)):
       check = False
       value = Energy(X0, B2[i])
       while not check:
           (check, X0, value) = LookAround(check, X0, value, B2[i], i)
       VSM2[j][i] = VSM(X0)
       if i!= (len(B2)-1):
           for bn in range(1,dot):
               check=False
               value=Energy(X0,bn*(B2[i]+B2[i+1])/dot)
               while not check:
                   (check,X0,value)=LookAround(check,X0,value,bn*(B2[i]+B2[i+1])/dot,i)
        
print("Час повного пербору", datetime.now() - start_time)
plt.plot(B1,Y1 , color="blue", label="Exp")
plt.plot(B2, Y2, color="blue")
for i in range(len(para)):
    plt.plot(B1, MainVSM[i],color=colors[i%len(colors)], linestyle=linestyles[i%len(linestyles)], label=f'for [{-para[i]},{para[i]}] mT')
    plt.plot(B2, VSM2[i], color=colors[i%len(colors)],linestyle=linestyles[i%len(linestyles)]) 
plt.xlim(-xlim,xlim)
plt.ylim(-ylim,ylim)
plt.title("T="+T+"K")
plt.xlabel('B[mT]')
plt.ylabel('M(B)/Ms')
plt.legend()

for i in range(N):        
    print(f"На ділянці (-{para[i]}, {para[i]}) оптимальні параметри \n(Ku,a1,a2,J2, J1)={save[i]}\n" )

with open('fit'+T+'.txt', 'w') as file:
        for i in range(len(B1)):
            file.write(f"{B1[i]} {MainVSM[0][i]}\n")
        for i in range(len(B2)):
            file.write(f"{B2[i]} {VSM2[0][i]}\n")





    
