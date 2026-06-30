#import matplotlib.pyplot as plt #para testar no exercicio 1
import random #utilizado para o exercicio 3 e 4 

#exercicio 1- Criar um histograma com uma frase de um ficheiro.

#procurar se existe ficheiro
try:
    f = open('TESTE.txt','r') #abrir o ficheiro 'TESTE.txt' em modo leitura
    texto = f.readlines() #pega  no ficheiro 'TESTE.txt' le e manda para a variavel texto 
    f.close()
except:
    print('O arquivo não existe!')
dicionario = {}

for linhas in texto: #percorrer cada linha do texto
    for letra in linhas: #percorrer cada letra da linha
        if letra.isalpha(): #verificar se é letra
            if letra in dicionario.keys(): #verificar se a letra está no dicionario
                dicionario[letra] += 1 #nº de vezes que a letra está no dicionario
            else:
                dicionario[letra] = 1 

def histograma(dicionario):  #chama dicionario 
    for letra in sorted(dicionario.keys()): #retorna lista de objetos especificos
        print(letra + "=" + "*"*dicionario[letra]) #coloca um * vezes a quantidade que existe no dicionario 

#para testar graficamente o histograma pode testar este codigo aqui é onde é usado o primeiro import 
# plt.title("Histograma de Letras")
# plt.xlabel('Letras')
# plt.ylabel('Numero de Letras')
# plt.bar(list(dicionario.keys()), dicionario.values(), color='#7eb54e')
# plt.show()

#exercicio 2- Encripta uma frase a partir de uma chave e desencripta a mesma.

def encriptaçao(frase, chave):
    alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWYZ' 
    novafrase = '' #frase vazia que irá ser retornada com texto no final
    for letra in frase: #percorrer cada letra da frase
        indice = alfabeto.find(letra) #encontra uma letra no alfabeto e coloca-a no indice
        if letra in alfabeto:
            if indice == -1: #se não encontrar o caracter presente no alfabeto ele adiciona esse caracter à nova frase 
                novafrase = novafrase + letra
            else:
                novoindice = indice + chave   #isto avança no indice criando um novo alfabeto
                novoindice = novoindice % len(alfabeto) #garante que a conta não passa o nº total do nosso alfabto, ou seja, o valor está dentro do intervalo
                novafrase += alfabeto[novoindice:novoindice+1] #calcula a nova string
    return novafrase

#exatamente igual ao 'def encriptaçao(frase, chave):' mas desencripta
def desencriptaçao(frase, chave):
    alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWYZ'
    novafrase = ''
    for letra in frase:
        indice = alfabeto.find(letra) 
        if letra in alfabeto:
            if indice == -1:
                novafrase = novafrase + letra
            else:
                novoindice = indice - chave #desencriptar
                novoindice = novoindice % len(alfabeto) 
                novafrase += alfabeto[novoindice:novoindice+1] 
    return novafrase



#exercicio 3- Permite codificar e descodificar um texto, utilizando um alfabeto misturado. 

alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#------------------------------- criar chave
def criar_chave():
    lista = []
    contador1 = 0
    chave = ""
    while contador1 < 26: #garante o nº do alfabeto
        contador1 = contador1 + 1 #conta o nº de vezes que fazemos o ciclo while
        num=random.randint(1,26) #dá um numero entre 1 e 26
        flag=0
        for x in lista:      #verificar a lista toda uma a uma
            if x==num:
                contador1 = contador1 - 1
                flag = 1
        if flag == 0:
            lista.append(num) #adiciona à lista a variavel (num)
            contador2 = 0
            for y in alfabeto:  #percorre alfabeto
                contador2 = contador2 + 1
                if contador2==num: #quando o contador for igual ao aleatorio, a letra que está no alfabeto vai ser igual ao nº aleatorio (o num corresponde a uma letra aleatoria do alfabeto)
                    chave = chave + y #adiciona a letra à nova chave
    return(chave) 

chave1 = criar_chave() #armazena a chave aleatoria

def encode_ale(x, chave):
    contador3 = -1
    contador4 = -1
    if x == " ":
        return x
    else:
        for y in alfabeto:
            contador3 = contador3 + 1
            if x == y:
                for z in chave:
                    contador4 = contador4 + 1
                    if contador3 == contador4:
                        return z

def decode_ale(x, chave):
    contador3 = -1
    contador4 = -1
    if x == " ":
        return x
    else:
        for y in chave:
            contador3 = contador3 + 1
            if x==y:
                
                for z in alfabeto:
                    contador4 = contador4 + 1
                    if contador4 == contador3:
                        return z

def encode1(frasedescodificada):
    contador3 = 0
    codificada = ""  # decifrar segundo a chave
    for x in frasedescodificada:         #A
        a= encode_ale(x, chave1)
        codificada = codificada + a
        contador3 = contador3 + 1
    return codificada

def decode1(frasecodificada):               
    contador3=0
    descodificada= ""

    for x in frasecodificada:
        a = decode_ale(x, chave1)
        descodificada = descodificada + a
        contador3 = contador3 + 1
    return descodificada




#exercicio 4- Codificar e descodificar um ficheiro de texto utilizando duas strings com o alfabeto numa ordem pré-estabelecida.

alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
chavep="ZSBTRQLAMUWDVPNCXGEIFYJHOK"     #igual ao criar_chave
chavei="CBHDIGPXWJVQANETORYKZUFSLM"  #igual ao criar_chave

#faz exatamente o mesmo que a criar_chave1()
def criar_chave2():
    lista = []
    contador3 = 0
    chavex = ""
    while contador3 < 26:
        contador3 = contador3 + 1
        num=random.randint(1,26)
        flag=0
        for x in lista:      #verificar a lista toda uma a uma
            if x==num:
                contador3 = contador3 - 1
                flag = 1
        if flag == 0:
            lista.append(num) #[1,4,6,2,5,8]
            contador4 = 0
            for y in alfabeto:  #ABCDEFGHIJKLMNOPQRSTUVWXYZ
                contador4 = contador4 + 1
                if contador4==num:
                    chavex = chavex + y
    return(chavex)

chave3 = criar_chave2()
chave2 = criar_chave2()

try:
    file1 = open("ProjetoFile.txt" , "r") #abrir o ficheiro 'ProjetoFile.txt' em modo leitura
    frasedescodificada1 = file1.read()
    frasedescodificada1 = ''.join(char for char in frasedescodificada1 if char.isalnum()) #deteta qualquer valor alfa númerico junta tudo
    frasedescodificada1 = frasedescodificada1.upper() #coloca em maiusculo
    f.close()
except:
    print('O arquivo não existe!')

def encode_par_impar(x, chavex):  #chave par
    contador3 = -1
    contador4 = -1
    if x == " ":
        return x
    else:
        for y in alfabeto:
            contador3 = contador3 + 1
            if x == y:
                for z in chavex:
                    contador4 = contador4 + 1
                    if contador3 == contador4:
                        return z

def decode_par_impar(x, chavex):
    contador3 = -1
    contador4 = -1
    if x == " ":
        return x
    else:
        for y in chavex:
            contador3 = contador3 + 1
            if x==y:
                for z in alfabeto:
                    contador4 = contador4 + 1
                    if contador4 == contador3:
                        return z



def encode2(frasedescodificada1):
    contador3 = 0
    codificada = ""  # decifrar segundo a chave
    for x in frasedescodificada1:         #A
        if contador3 % 2 == 0:                   #par
            a= encode_par_impar(x, chave3)
            codificada = codificada + a
            contador3 = contador3 + 1
        else:                                   #impar
            a = encode_par_impar(x, chave2)
            codificada = codificada + a
            contador3 = contador3 + 1
    return codificada

def decode2(frasedescodificada1, chave3, chave2):
    descodificada = ""
    contador = 0
    for x in frasedescodificada1:
        if contador == 0 or 0 == contador % 2:
            a = decode_par_impar(x, chave3)
        else:
            a = decode_par_impar(x, chave2)
        descodificada += a
        contador += 1
    return descodificada



#menu
print("----------------------------------MENU----------------------------------")                                      
print("|                            CIFRA DE CESAR                            |")      
print("| Escolha uma das seguintes opções:                                    |")       
print("|                                                                      |")       
print("| 0) Para encerrar o programa.                                         |")
print("| 1) Criar um histograma com uma frase de um ficheiro.                 |")
print("| 2) Encripta uma frase a partir de uma chave e desencripta a mesma.   |")
print("| 3) Permite codificar e descodificar um texto, utilizando um          |") 
print("| alfabeto misturado.                                                  |")
print("| 4) Codificar e descodificar um ficheiro de texto utilizando duas     |")
print("| strings com o alfabeto numa ordem pré-estabelecida.                  |")
print("| 5) Autores                                                           |") 
print("------------------------------------------------------------------------")


#cada opção do menu
while True:
    escolha = input("Introduza uma opção do menu: ")
    match escolha:
        case '0':
            print("Programa encerrado")
            break 
        case '1':
            print(dicionario)
            print(histograma(dicionario))      
        case '2':
            escolha1 = (int)(input("Digite 1 para encriptar ou digite 2 para desencriptar: "))
            chave = (int)(input("Coloque a quantidade de casas que quer avançar no alfabeto: "))
            original = (str)(input("Introduze uma frase: "))
            original = original.upper()    
            
            while True:
                if escolha1 == 1:
                    encode = encriptaçao(original, chave)
                    print('Encriptada:', encode)
                    break
                elif escolha1 == 2:
                    decode = desencriptaçao(original, chave)
                    print('Descriptada:', decode)
                    break 
                else:
                    escolha1 = (int)(input("Erro!! Por favor, coloque um número entre 1 e 2 para escolher a opção de encriptar e desencriptar. Introduza novamente: "))
        case '3':
            escolha2  = (int)(input("Digite 1 para encriptar ou digite 2 para desencriptar: "))
            while True:
                if escolha2 == 1:

                    frasedescodificada = (str)(input("Frase: "))
                    frasedescodificada = frasedescodificada.upper()
                    print("Frase: " , encode1(frasedescodificada))
                    break
                elif escolha2 == 2:
                    frasecodificada=(str)(input("Frase: "))
                    frasecodificada = frasecodificada.upper()
                    print("Frase: " , decode1(frasecodificada))
                    break 
                else:
                    escolha2 = (int)(input("Erro!! Por favor, coloque um número entre 1 e 2 para escolher a opção de encriptar e desencriptar. Introduza novamente: "))
        case '4':
            chave3 = criar_chave()
            chave2 = criar_chave()
            codificada = encode2(frasedescodificada1)     
            print("Codificada: ", codificada)
            print("Descodificada: ", decode2(codificada, chave3, chave2))
        case '5':
            print("Trabalho de Laboratório de Programação: ") 
            print(" Projeto Final- Encriptação")
            print("     Diogo Vieira al76191")
            print("     João Monteiro al76117")
            print("     Jorge Pereira al14023")
            print("     Tiago Moreira al76741")
        case _:
            print("Opçao indisponivel")