"""
ESTA NUEVA VERSION CONSIDERA LA NORMALIZACION DE LOS MENSAJES

CLASIFICADOR QUE LEE TWEETS A CLASIFICAR DESDE LA TABLA CLASIFICAR+TABLA 
Y DESDE ENLACES_CLASIFICADOR SACA LAS REDES G

RECIBE 4 ARGUMENTOS:

-TABLA,
-TIPO DE ANALISIS (NO-WEIGHT,WEIGHT),
-STOP-WORDS (SI=1, NO=0),
-BALANCE (SI=1, NO=0)
"""

import MySQLdb
import sys
import re
import procesar
import os
import logging
import time

def netsense(fecha_ant,fecha_post,fecha_ev,perfiles,sopena,config=-1):
	#analisis,valence,contador,stopword,
	#vector = [[0,0,0,0],[0,0,0,1],[0,0,1,0],[0,0,1,1],[0,1,0,0],[0,1,0,1],[0,1,1,0],[0,1,1,1],[1,0,0,0],[1,0,0,1],[1,0,1,0],[1,0,1,1],[1,1,0,0],[1,1,0,1],[1,1,1,0],[1,1,1,1]]
	#vector = [[1,0,0,0],[1,0,0,1],[1,0,1,0],[1,0,1,1],[1,1,0,0],[1,1,0,1],[1,1,1,0],[1,1,1,1]]
	#vector = [[0,0,0,0],[1,0,0,1],[1,0,1,0]]
	vector = [[0,0,0,0],[1,0,0,0],[0,0,0,1],[1,0,0,1]]
	#vector = [[0,0,0,0],[1,0,0,0]]
	#vector = [[0,0,0,0]]
	if config != -1:
		aux = vector[config]
		vector = []
		vector.append(aux)
	print vector
	estado = 0
	# analisis=1 con peso
	#analisis=1
	
	for evaluacion in vector:

		print evaluacion
		db = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
		c = db.cursor()
		c.execute("TRUNCATE evaluador_netsense_SENTIDO_FONDECYT")
		c.execute("SELECT id_perfil FROM perfiles WHERE estado="+str(estado)+" and id_perfil IN ("+str(perfiles)+")")
		
		resultado=c.fetchall()
		print "ids:",resultado
	
		print evaluacion
		#por cada perfil se realizara la evaluacion
		for fila in resultado:
				procesar.procesaNetsense(db, fila[0],1,evaluacion,fecha_ant,fecha_post,fecha_ev,sopena,perfiles)
		
		print evaluacion
		