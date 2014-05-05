
'''
Created on 23-11-2013


@author: pancho
'''
import csv
import procesar as p
import sys
import MySQLdb
from datetime import *



if __name__ == '__main__':
    archivo=str(sys.argv[1])
    opcion=str(sys.argv[2])
    reader = csv.reader(open(archivo, 'rb'), delimiter=',')
    archivo = csv.writer(open("normalizadoWeka.csv", "wb"), delimiter=',')
    #palabras = csv.writer(open("analisis/palabras.csv", "wb"), delimiter='\t')
    stopword = p.stopWords()
    db1 = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
    db1.names = "utf-8"
    c1 = db1.cursor()
    
    c1.execute("SELECT * FROM diccionario_clasificador")
    resultado=c1.fetchall()
    sopena={}
    for fila in resultado:
        sopena[fila[0]]=fila[1]
    
    for index,row in enumerate(reader):
        print index
        if(row[4]=='2'):
            row[4]="Negativo"
        elif(row[4]=='1'):
            row[4]="Positivo"
        else:
            row[4]="Neutro"
        
        emoticon = [0,0,0]
        tweetwords=[]
        tweet=str(row[2].replace('\n',' '))
        tweet=str(tweet.replace('"',''))
        leaves="s"
        tweet=tweet.decode('utf-8')
        tweet = p.reempEmoticon(tweet) 
        tweet = tweet.replace("RT"," ")
        tweet = tweet.lower()
        tweet = p.repChar(tweet)
        tweet = p.strChar(tweet)
        
        #print tweet
        
        tweet=tweet.split()    
        [emoticon,tweetwords] = p.procesarTweet(tweet,emoticon,opcion,tweetwords)           
        tweetwords = p.normalizar(tweetwords)
        tweetwords = p.sufijos(tweetwords,leaves)
        for i in range (len(tweetwords)):
            if tweetwords[i].encode("utf-8") not in stopword:
                tweetwords[i] = p.cambiarPalabraS(tweetwords[i],c1,sopena)
                #tweetwords[i] = p.cambiarPalabraS(tweetwords[i],c1)
        #row[0]='"'+str(row[0].replace('"',''))+'"'
        row[2]='"'+" ".join([x.encode('utf-8') for x in tweetwords])+'"'


        
        #palabras.writerow(tweet)
        
        archivo.writerow(row)
    print "Normalizado Terminado"