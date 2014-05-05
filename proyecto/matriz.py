'''
Created on 25/04/2014

@author: Pancho
'''
import MySQLdb

if __name__ == '__main__':
    db = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
    c = db.cursor()
    tipo="netsense"
    sql="SELECT sentido_manual,netsense,count(*) FROM analitic.evaluador_netsense_sentido_fondecyt where "+tipo+" != 5 group by sentido_manual,netsense"
    c.execute(sql)
        
    resultado=c.fetchall()
    matriz=[[0,0,0],[0,0,0],[0,0,0]]
    for reg in resultado:
        matriz[reg[0]][reg[1]]=reg[2]
    
    print("     0    1    2")    
    for i in range(3):
        print "%s    %s    %s    %s" %(i,matriz[i][0],matriz[i][1],matriz[i][2])
    id_evaluacion_historica=1
    sql="INSERT INTO matriz_confusion(id_evaluacion_historica,neutro_neutro,neutro_positivo,neutro_negativo,positivo_neutro,positivo_positivo,positivo_neutro,negativo_neutro,negativo_positivo,negativo_negativo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" %(id_evaluacion_historica,int(matriz[0][0]),int(matriz[0][1]),int(matriz[0][2]),int(matriz[1][0]),int(matriz[1][1]),int(matriz[1][2]),int(matriz[2][0]),int(matriz[2][1]),int(matriz[2][2]))
    print sql
        