import sys

#Estructura con la información referente a cada instrucción
class Instruction:
    def __init__ (self, a, b, c, d):
        self.process = a
        self.di = b
        self.dm = c
        self.type = d
#Estructura con el contenido de la Tabla de páginas
class Table_entry:
    def __init__ (self, a = -1, b = -1, c = -1, d = -1, e = 0):
        self.process = a
        self.logicPage = b
        self.reference = c
        self.dirty = d
        self.clock = e

#Creamos una lista con todas las instrucciones ordenadas de acuerdo al quantum
def leerproc(archivo1, archivo2, archivo3, archivo4, quantum, numPro):
    #En lista vamos a añadir todas las instrucciones en forma de objetos de la clase Instruction
    lista = []
    fileInstruction1 = open(archivo1,'r')
    fileInstruction2 = open(archivo2,'r')
    fileInstruction3 = open(archivo3,'r')
    fileInstruction4 = open(archivo4,'r')
    lines1=fileInstruction1.readlines()
    lines2=fileInstruction2.readlines()
    lines3=fileInstruction3.readlines()
    lines4=fileInstruction4.readlines()

    linesList=[lines1,lines2,lines3,lines4]

    #Creamos una lista con el numero de instrucciones de cada proceso
    lenList = []
    for i in range (numPro):
        lenList.append(len(linesList[i]))
    #El archivo con mayor cantidad de lineas determina el maximo de lineas que recorremos en total
    maxLen=(max(lenList))
    #El numero de veces que recorreremos "quantum numero" de instrucciones
    cicles=maxLen/quantum
    #Contador para recorrer las instrucciones
    c=0
    #Para cada proceso recorremos desde minimo a maximo las instrucciones para copiarlas en un solo lugar
    minimo=0
    maximo=quantum
    while (c<cicles):
        for i in range(numPro):
            #Recorremos el numero de instrucciones determinadas por el quantum
            for j in range(minimo,maximo):
                if(j<len(linesList[i])):
                    linesList[i][j]=linesList[i][j][:-1].split(' ')
                    d=0
                    if linesList[i][j][3] == 'W':
                        d=1
                    lista.append(Instruction(int(linesList[i][j][0]),int(linesList[i][j][1]),int(linesList[i][j][2]),d))
        minimo=minimo+quantum
        maximo=maximo+quantum

        c=c+1
    fileInstruction1.close
    fileInstruction2.close
    fileInstruction3.close
    fileInstruction4.close

    return lista

def leer(archivo):
    param=[]
    try:
        dataparametros = open(archivo,'r')
    except :
    	print('Error al leer el archivo ', archivo)
    	return -1
    for linea in dataparametros:
        param.append(linea)

    global length, pages, quantum, numPro
    lenght=int(param[0])
    pages=int(param[1])
    quantum=int(param[2])
    numPro=int(param[3])

    listacomp=leerproc(param[4].rstrip('\n'),param[5].rstrip('\n'),param[6].rstrip('\n'),param[7].rstrip('\n'),quantum,numPro)
    dataparametros.close

    return listacomp

	#0 tamano de pagina, 1 tamano de la memoria en frames, 2 quantum, 3 numero de procesos
	#4,5,6,7 son los indices de los archivos de texto

#Crea una lista con "pages" número de objetos Table_entry
def create_list():
    lis = []
    for _ in range(pages):
        lis.append(Table_entry())
    return lis

#Coloca el bit de referencia en 0
def reference_bit_to_0(lis):
    for proc in lis:
        proc.reference = 0
    return lis

#Buscamos el numero de pagina de la instrucción
def search(lis,P):
    find1 = False
    find2 = False
    i = 0
    while not find1 and i < len(lis):
        if lis[i].process == P.process and lis[i].logicPage == P.di // length:
            find1 = True
        else:
            i+=1
    j = 0
    while not find2 and j < len(lis):
        if lis[j].process == P.process and lis[j].logicPage  == P.dm // length:
            find2 = True
        else:
            j+=1
    return  i, j , find1 ,find2

def complete(lis):
    i = 0
    full = True
    while i<pages and full:
        if lis[i].process == -1:
            full = False
        else:
            i+=1
    return i , full

#Funciones de busqueda version 1
def searchNotExistV1(lis):
    find = False
    write = False
    case = [(0,0),(0,1),(1,0),(1,1)]
    i = 0
    while i < 4 and not find:
        pos = 0
        while not find and pos<len(lis):
            if (lis[pos].reference,lis[pos].dirty) == case[i]:
                find = True
                if lis[pos].dirty == 1:
                    write = True
            else:
                pos+=1
        i+=1
    return pos , write

#Funciones de busqueda version 2
def lowerClock(lis):
    j = 0
    for i in range(len(lis)):
        if lis[i].clock < lis[j].clock:
            j = i
    return j

def searchNotExistV2(lis):
    pos = lowerClock(lis)
    write = lis[pos].dirty or 0
    return pos , write


#Funciones de Actualizacion version 1
def updateWithVersion1(instruction_list,mem,debug):
    contIns = 1
    cont = 1
    contFails = 0
    contEscritura = 0
    for process in instruction_list:
        pos1,pos2, find1, find2 = search(mem,process)
        if not find1:
            contFails+=1
            pos3 , full= complete(mem)
            if not full:
                mem[pos3] = Table_entry(process.process,process.di//length,1,0,cont)
            else:
                pos4, escritura = searchNotExistV1(mem)
                if debug:
                    print ("---",'\t', cont,'\t',pos4,'\t',mem[pos4].process,'\t',mem[pos4].logicPage,'\t',mem[pos4].dirty,'\t', "---")
                if escritura:
                    contEscritura+=1
                mem[pos4] = Table_entry(process.process,process.di//length,1,0,cont)
        else:
            mem[pos1] = Table_entry(process.process,process.di//length,1,mem[pos1].dirty or 0,cont)

        pos1,pos2, find1, find2 = search(mem,process)
        if not find2:
            contFails+=1
            pos3 , full= complete(mem)
            if not full:
                mem[pos3] = Table_entry(process.process,process.dm//length,1,process.type,cont)
            else:
                pos4, escritura = searchNotExistV1(mem)
                if debug:
                    print ("---",'\t', cont,'\t',pos4,'\t',mem[pos4].process,'\t',mem[pos4].logicPage,'\t',mem[pos4].dirty,'\t', "---")
                if escritura:
                    contEscritura+=1
                mem[pos4] = Table_entry(process.process,process.dm//length,1,process.type,cont)
        else:
            mem[pos2] = Table_entry(process.process,process.dm//length,1,mem[pos2].dirty or process.type,cont)
        if contIns == 200:
            mem = reference_bit_to_0(mem)
            contIns = 0

        contIns+=1
        cont+=1
    return contFails, contEscritura, mem

#Funciones de Actualizacion version 2
def updateWithVersion2(instruction_list,mem,debug):
    contIns = 1
    cont = 1
    contFails = 0
    contEscritura = 0
    for process in instruction_list:
        pos1,pos2, find1, find2 = search(mem,process)
        if not find1:
            contFails+=1
            pos3 , full= complete(mem)
            if not full:
                mem[pos3] = Table_entry(process.process,process.di//length,1,0,cont)
            else:
                pos4, escritura = searchNotExistV2(mem)
                if debug:
                        print ("---",'\t', cont,'\t',pos4,'\t',mem[pos4].process,'\t',mem[pos4].logicPage,'\t',mem[pos4].dirty,'\t', "---")
                if escritura:
                    contEscritura+=1
                mem[pos4] = Table_entry(process.process,process.di//length,1,0,cont)
        else:
            mem[pos1] = Table_entry(process.process,process.di//length,1,mem[pos1].dirty or 0,cont)

        pos1,pos2, find1, find2 = search(mem,process)
        if not find2:
            contFails+=1
            pos3 , full= complete(mem)
            if not full:
                mem[pos3] = Table_entry(process.process,process.dm//length,1,process.type,cont)
            else:
                pos4, escritura = searchNotExistV2(mem)
                if debug:
                        print ("---",'\t', cont,'\t',pos4,'\t',mem[pos4].process,'\t',mem[pos4].logicPage,'\t',mem[pos4].dirty,'\t', "---")
                if escritura:
                    contEscritura+=1
                mem[pos4] = Table_entry(process.process,process.dm//length,1,process.type,cont)
        else:
            mem[pos2] = Table_entry(process.process,process.dm//length,1,mem[pos2].dirty or process.type,cont)
        if contIns == 200:
            mem = reference_bit_to_0(mem)
            contIns = 0
        contIns+=1
        cont+=1
    return contFails, contEscritura, mem

length=512
pages=32
quantum=0
numPro=0
def main():

    Parameter = sys.argv
    l = len(Parameter)

    if leer(Parameter[1]) == -1:
        return 0

    if l==3:
        Parameter.append('0')

    elif l < 3:
        print ('Error: La estructura es la siguiente, el tercer parametro es opcional')
        print ("""Menu:
Parametro 1 : Nombre archivo
Parametro 2 : Version(1/2)
Parametro 3 : Debug(1/0) """)

    else:
        InsList = leer(Parameter[1])
        if Parameter[2] == '1':
            contFails, contWrites, _ =  updateWithVersion1(InsList,create_list(),int(Parameter[3]))
            print ('Version: ',Parameter[2],'\nFallos: ',contFails,'\nEscrituras: ',contWrites)
        elif Parameter[2] == '2':
            contFails, contWrites, _ =  updateWithVersion2(leer(Parameter[1]),create_list(),int(Parameter[3]))
            print ('Version: ',Parameter[2],'\nFallos: ',contFails,'\nEscrituras: ',contWrites)
        else:
            print ('Version Desconocida')


main()
