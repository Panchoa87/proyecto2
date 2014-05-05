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
    archivo = csv.writer(open("377.csv", "wb"), delimiter=',')
            
    # prepare a cursor object using cursor() method
    c = db.cursor()
    #Se crea el diccionario para intercambiar las palabras        
    c.execute("SELECT cuerpo,tipo_sentido FROM tweets Where id_perfil=377")
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