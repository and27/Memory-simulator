import sys
from time import time


#Clases para definir cada Instrucción
class Instruction:
    def __init__ (self,proc,dir1,dir2,act):
        self.process = proc
        self.dir1 = dir1
        self.dir2 = dir2
        self.act = act

#Estructura con el contenido de la Tabla de páginas, en este caso es una tabla de paginas invertida
class PageTable:
    def __init__ (self, proc = -1, page = -1, ref = -1, dirt = -1, clock = 0):
        self.process = proc
        self.page = page
        self.reference = ref
        self.dirty = dirt
        self.clock = clock

#Creamos una lista con todas las instrucciones ordenadas de acuerdo al quantum
def leer_proc(archivo1, archivo2, archivo3, archivo4, quantum, numPro):
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
    	print('Error al intentar leer el archivo', archivo)
    	return -1
    for linea in dataparametros:
        param.append(linea)

    global length, pages, quantum, numPro
    lenght=int(param[0])
    pages=int(param[1])
    quantum=int(param[2])
    numPro=int(param[3])

    listacomp=leer_proc(param[4].rstrip('\n'),param[5].rstrip('\n'),param[6].rstrip('\n'),param[7].rstrip('\n'),quantum,numPro)
    dataparametros.close

    return listacomp

#Crea una lista con "pages" número de objetos PageTable
def create_list():
    list = []
    for _ in range(pages):
        list.append(PageTable())
    return list

#Coloca el bit de referencia en 0
def reference_bit_to_0(list):
    for proc in list:
        proc.reference = 0
    return list

#Buscamos el numero de pagina de la instrucción

#Aqui busca las 2 direcciones de la intrucción estan en memoria (en las páginas)
def dir_search(list,P):
    find_dir1 = False
    find_dir2 = False
    i = 0
    while not find_dir1 and i < len(list):
        if list[i].process == P.process and list[i].page == int(P.dir1/length):
            find_dir1 = True
        else:
            i+=1
    j = 0
    while not find_dir2 and j < len(list):
        if list[j].process == P.process and list[j].page  == int(P.dir2/length):
            find_dir2 = True
        else:
            j+=1
    return  i, j , find_dir1 ,find_dir2

#Aqui comprueba que el frame[i] ==-1, si no, osea Comprueba si una pagina está llena o no
#Cuando encuentra el que está vacío, retorna el nro de pagina y el valor de full
def full_page(list):
    i = 0
    full = True
    while i<pages and full:
        if list[i].process == -1:
            full = False
        else:
            i+=1
    return i , full

#Contador de los bits de validación
def bits_cases(list):
    comb= [(0,0),(0,1),(1,0),(1,1)]
    val = False
    write = False
    i = 0
    while i < 4 and not val:
        j = 0
        while not val and j<len(list):
            if (list[j].reference,list[j].dirty) == comb[i]:
                val = True
                if list[j].dirty == 1:
                    write = True
            else:
                j+=1
        i+=1
    return j , write


def version_1(insList,mem,print1):
    pageFault = 0
    contClock = 1
    contInst = 1
    contW = 0
    for process in insList:
        i,j, find_dir1, find_dir2 = dir_search(mem,process)
        #Esto es para la dirección 1
        if not find_dir1:#Si no se encontró la dir 1
            pageFault+=1
            k , full= full_page(mem)
            if not full:#Si la página no está llena
                mem[k] = PageTable(process.process,int(process.dir1/length),1,0,0)
            else:#si está lleno (ver que está lleno)
                l, escritura = bits_cases(mem)
                if print1:
                    print ("| ",contClock,'\t',l,'\t',mem[l].process,'\t',mem[l].page,'\t',mem[l].dirty)
                if escritura:
                    contW+=1
                mem[l] = PageTable(process.process,int(process.dir1/length),1,0,0)
        else:
            mem[i] = PageTable(process.process,int(process.dir1/length),1,mem[i].dirty or 0,0)

        i,j, find_dir1, find_dir2 = dir_search(mem,process)

        #Esto es para la dirección 2
        if not find_dir2:#Se repite el proceso para la segunda direccion
            pageFault+=1
            k , full= full_page(mem)
            if not full:
                mem[k] = PageTable(process.process,int(process.dir2/length),1,process.act,0)
            else:
                l, escritura = bits_cases(mem)
                if print1:
                    print ("| ",contClock,'\t',l,'\t',mem[l].process,'\t',mem[l].page,'\t',mem[l].dirty)
                if escritura:
                    contW+=1
                mem[l] = PageTable(process.process,int(process.dir2/length),1,process.act,0)
        else:
            mem[j] = PageTable(process.process,int(process.dir2/length),1,mem[j].dirty or process.act,0)
        if contInst == 200:
            mem = reference_bit_to_0(mem)
            contInst = 0
        contClock+=1
        contInst+=1
    return pageFault, contW, mem

def clock(list):
    j = 0
    for i in range(len(list)):
        if list[i].clock < list[j].clock:
            j = i
    return j

def version_2(insList,mem,print1):
    pageFault = 0
    contInst = 1
    contClock = 1
    contW = 0
    for process in insList:
        i,j, find_dir1, find_dir2 = dir_search(mem,process)
        if not find_dir1:
            pageFault+=1
            k , full= full_page(mem)
            if not full:
                mem[k] = PageTable(process.process,int(process.dir1/length),1,0,contClock)
            else:
                pos = clock(mem)
                write = mem[pos].dirty or 0
                l, escritura = pos , write
                if print1:
                        print ("| ", contClock,'\t',l,'\t',mem[l].process,'\t',mem[l].page,'\t',mem[l].dirty)
                if escritura:
                    contW+=1
                mem[l] = PageTable(process.process,int(process.dir1/length),1,0,contClock)
        else:
            mem[i] = PageTable(process.process,int(process.dir1/length),1,mem[i].dirty or 0,contClock)

        i,j, find_dir1, find_dir2 = dir_search(mem,process)
        if not find_dir2:
            pageFault+=1
            k , full= full_page(mem)
            if not full:
                mem[k] = PageTable(process.process,int(process.dir2/length),1,process.act,contClock)
            else:
                pos = clock(mem)
                write = mem[pos].dirty or 0
                l, escritura = pos , write
                if print1:
                        print ("| ",contClock,'\t',l,'\t',mem[l].process,'\t',mem[l].page,'\t',mem[l].dirty)
                if escritura:
                    contW+=1
                mem[l] = PageTable(process.process,int(process.dir2/length),1,process.act,contClock)
        else:
            mem[j] = PageTable(process.process,int(process.dir2/length),1,mem[j].dirty or process.act,contClock)
        if contInst == 200:
            mem = reference_bit_to_0(mem)
            contInst = 0
        contInst+=1
        contClock+=1
    return pageFault, contW, mem

length=512
pages=32
numPro=0
def main(arguments):

    tam = len(arguments)
    if leer(arguments[1]) == -1:
        return 0
    if tam==3:
    	arguments.append('0')
    if (tam < 3 or tam > 4):
    	print ("\n Error, asegurece de que la estructura del comando es correcta: ")
    	print ("python <nombre_programa> <nombre_archivo> <version> <print> \n")
    else:
        start_time = time()
        InsList = leer(arguments[1])
        if arguments[2] == '1':
            pageFault, contWrites, _ =  version_1(InsList,create_list(),int(arguments[3]))
            print("\n\n-------------------------------------------------------------\n\n")
            print ('VERSION 1\n', 'Page Faults: ',pageFault,'\n','Escrituras: ',contWrites)
            print("\n\n-------------------------------------------------------------\n\n")
        elif arguments[2] == '2':
            pageFault, contWrites, _ =  version_2(leer(arguments[1]),create_list(),int(arguments[3]))
            print("\n\n-------------------------------------------------------------\n\n")
            print ('VERSION 2\n','Page Faults: ',pageFault,'\n','Escrituras: ',contWrites)
            print("\n\n-------------------------------------------------------------\n\n")

        else:
            print("Error al ingresar la version")

        elapsed_time = time() - start_time
        print("Elapsed time: %.10f seconds." % elapsed_time)

	

arguments = sys.argv
main(arguments)


