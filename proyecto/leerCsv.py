'''
Created on 07/08/2013

@author: Pancho
'''
#!/usr/bin/env python
import csv
import sys

if __name__ == '__main__':
    
    reader = csv.reader(open("ejemplo2.csv", 'rb'), delimiter='\t')
    archivo = csv.writer(open("clasificador/weka.csv", "wb"), delimiter=',')
    palabras = csv.writer(open("analisis/palabras.csv", "wb"), delimiter='\t')
    
    for index,row in enumerate(reader):
        tweet=[]
        tweet.append(row[1])
        tweet.append(row[0])
        aux=row[0].replace('"','')
        aux=aux.split(" ")
        tweet.append(len(aux))
        max=0
        for i in range(len(aux)):
            if(len(aux[i])>max):
                max=len(aux[i])
        tweet.append(max)
        row[0]=str(row[0].replace('\n',''))    
        row[0]='"'+str(row[0].replace('"',''))+'"'

        if(row[3]=='2'):
            row[3]="Negativo"
        elif(row[3]=='1'):
            row[3]="Positivo"
        else:
            row[3]="Neutro"
        palabras.writerow(tweet)
        archivo.writerow(row)
    print "Archivo Listo"