"""

 ESTE CODIGO RELLENA LA BASE DE DATOS CON LOS ENLACES Y SUS RESPECTIVOS PESOS PARA
 LUEGO USARLOS CON NETSENSE PARA CONSTRUIR LOS GRAFOS (G).
 
 RECIBE 2 ARGUMENTOS: LA TABLA DE LA QUE SACA LOS ENTRENADOS Y UN BOOLEANO POR SI ESTA 
 EXTRACCION ES BALANCEADA (1) O DESBALANCEADA (0)

"""
import MySQLdb
import sys
import procesar
import os
import netsense
import time

if __name__ == "__main__":
	fechas = []
	
	
	fecha = str(sys.argv[1])
	fechas.append(fecha)
	fecha = str(sys.argv[2])
	fechas.append(fecha)
	fecha = str(sys.argv[3])
	fechas.append(fecha)
	
	perfiles = str(sys.argv[4])
	#0 no llena, 1 llena
	llena_enlace = int(sys.argv[5])
	#por defecto -1, debes elegir dentro del vector de configuraciones
	if len(sys.argv) == 5:
		config = int(sys.argv[6])  
	else:
		config = -1
	#fechas = ['2012-09-01','2012-09-02','2012-09-03','2012-09-04','2012-09-05']

	leaves = "s"
	tabenlaces = "enlaces_clasificador_FONDECYT"

	# Open database connection
	db = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
	db.names = "utf-8"
			
	# prepare a cursor object using cursor() method
	c = db.cursor()
	#Se crea el diccionario para intercambiar las palabras		
	c.execute("SELECT * FROM diccionario_clasificador")
	resultado=c.fetchall()
	sopena={}
	for fila in resultado:
		sopena[fila[0]]=fila[1]
		
	c.execute("SELECT fecha FROM ultimo_entrenamiento_FONDECYT where idperfil IN ('"+str(perfiles)+"')")
	aux = c.fetchone()
	fecha_fr = fechas[0]
	
	#Se generan los grafos de entrenamientos	
	if llena_enlace == 1 or llena_enlace == 2:
		procesar.genRedes(c,leaves,tabenlaces,db,fecha_fr,fechas[1],perfiles,sopena)
		
	db.close()
	
	#evaluacion del clasificador
	if llena_enlace != 2:
		print netsense
		netsense.netsense(fechas[0],fechas[1],fechas[2],perfiles,sopena,config)
		
