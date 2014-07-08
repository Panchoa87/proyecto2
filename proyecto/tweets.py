# -*- coding: utf-8 -*-
'''
Created on 26/04/2014

@author: Pancho
'''
import MySQLdb
import csv
if __name__ == '__main__':
    db = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
    db.names = "utf-8"
    archivo = csv.writer(open("rand381.csv", "wb"), delimiter=',')
            
    # prepare a cursor object using cursor() method
    c = db.cursor()
    #Se crea el diccionario para intercambiar las palabras        
    c.execute("select t.cuerpo,t.tipo_sentido,id_perfil from rand_fondecyt e inner join tweets t ON t.id_perfil_articulo=e.id_tweet where id_perfil=381")
    resultado=c.fetchall()
    for res in resultado:
        row=[res[0],res[1]]
        row[0]=row[0].replace('"','')
        row[0]=row[0].replace("'",'')
        row[0]=row[0].replace('\n','')
        row[0]=row[0].replace("\r",'')
        row[0]=row[0].replace("\r\n",'')
        row[0]='"'+row[0].encode('utf-8')+'"'
        archivo.writerow(row)
    c.execute("select t.cuerpo,t.tipo_sentido,id_perfil from entrenamiento_fondecyt e inner join tweets t ON t.id_perfil_articulo=e.id_tweet where id_perfil=1")
    resultado=c.fetchall()
    for res in resultado:
        row=[res[0],res[1]]
        row[0]=row[0].replace('"','')
        row[0]=row[0].replace("'",'')
        row[0]=row[0].replace('\n','')
        row[0]=row[0].replace("\r",'')
        row[0]=row[0].replace("\r\n",'')
        row[0]='"'+row[0].encode('utf-8')+'"'
        archivo.writerow(row)
    print("archivo Listo")