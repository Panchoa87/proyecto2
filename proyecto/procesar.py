#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

 ACA SE ENCUENTRA EL LISTADO DE TODAS LAS FUNCIONES UTILIZADAS
 PARA LA GENERACION DE LAS REDES DE PALABRAS DE LOS TWEETS

"""

import sys
import re
import MySQLdb
import networkx as nx
import numpy
import csv
from networkx.readwrite import json_graph as json
import logging

import time

# CAMBIA PALABRA #
def cambiarPalabra(palabra,c):
	
	c.execute("SELECT palabra,destino,aprobado FROM diccionario_clasificador WHERE palabra = '"+palabra+"' COLLATE utf8_bin")
	salida = c.fetchall()
	if len(salida) == 0:
		c.execute("INSERT INTO diccionario_clasificador (palabra,destino,aprobado) VALUES ('"+palabra+"','"+palabra+"','0')")
		c.execute("SELECT palabra,destino,aprobado FROM diccionario_clasificador WHERE palabra = '"+palabra+"' COLLATE utf8_bin")
		salida = c.fetchall()
	#print palabra,salida," salida"
	palabra = salida[0][1]
	
	return palabra


# CAMBIA PALABRA #
def cambiarPalabraS(palabra,c,sopena):
	#global word_nuevas
	#~ c.execute("SELECT palabra,destino,aprobado FROM diccionario_clasificador WHERE palabra = '"+palabra+"' COLLATE utf8_bin")
	#~ salida = c.fetchall()
	#~ if len(salida) == 0:
		#~ c.execute("INSERT INTO diccionario_clasificador (palabra,destino,aprobado) VALUES ('"+palabra+"','"+palabra+"','0')")
		#~ c.execute("SELECT palabra,destino,aprobado FROM diccionario_clasificador WHERE palabra = '"+palabra+"' COLLATE utf8_bin")
		#~ salida = c.fetchall()
	#~ #print palabra,salida," salida"
	#~ palabra = salida[0][1]
	word_destino=sopena.get(palabra)
	if word_destino is  None:
		#word_nuevas.append(palabra)
		#~ try:
			#~ print palabra," NUEVA!!!!!!!!!!!!!!!"
		#~ except:
			#~ pass
		return palabra
	else:
		word_destino=word_destino.replace("á".decode("utf-8"),"a")
		word_destino=word_destino.replace("é".decode("utf-8"),"e")
		word_destino=word_destino.replace("í".decode("utf-8"),"i")
		word_destino=word_destino.replace("ó".decode("utf-8"),"o")
		word_destino=word_destino.replace("ú".decode("utf-8"),"u")
		return word_destino
#stopwords
def stopWords():
	stopword = ["de","la","que","el","en","y","a","los","se","del","las","un","por","con","una","su","para","es","al","lo","como","mías","o","pero","sus","le","ha","me","sin","sobre","este","ya","entre","cuando","todo","esta","ser","son","dos","también","fue","era","muy","hasta","desde"]
	return stopword

# PROCESA EL CUERPO DE UN TWEET #
def procesarCuerpo(cuerpo):
	cuerpo = reempEmoticon(cuerpo)
	cuerpo=cuerpo.lower()
	cuerpo = repChar(cuerpo)
	cuerpo = strChar(cuerpo)
	cuerpo=cuerpo.split()
	return cuerpo

# TOKENIZA UN TWEET #
def tokenizar(cuerpo,leaves):
	palabras=[]
	for i in range (len(cuerpo)):
		#if cuerpo[i] not in stopwords.words('spanish') and len(cuerpo[i]) > 1:
		palabras.append(cuerpo[i])
	#print palabras
	#print "___________________"
	palabras = normalizar(palabras)
	palabras = sufijos(palabras,leaves)
	return palabras

# BLOQUE PESOS ENLACES #
def bloquePesos(palabras,c,id_perfil,tabenlaces,id_articulo,tipoEnlace,fecha_pub,sopena):
	cont = 0
	stopword = stopWords()
	db1 = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
	#db1.names = "utf-8"
	c1 = db1.cursor()
	pares=[]
	for i in range (len(palabras)+1):
		if i<len(palabras)-1:
			if palabras[i].encode("utf-8") not in stopword:
				palabras[i] = cambiarPalabraS(palabras[i],c1,sopena)
			if palabras[i+1].encode("utf-8") not in stopword:
				palabras[i+1] = cambiarPalabraS(palabras[i+1],c1,sopena)
			
			#print palabras[i] +" -> "+ palabras[i+1] + "\n"
			pares.append(palabras[i].encode("utf-8")+" "+palabras[i+1].encode("utf-8"))

	enlaces=[]
	for w in pares:
		#print w
		for w2 in pares:
			if w == w2:
				cont += 1
				#cont2=float(cont)
		#print str(w)+" "+str(cont)

		enlaces.append(w+" "+str(1/float(cont)))
		cont=0
	
	#print "escribo enlaces en la base de datos"
	for ed in range (len(enlaces)):
		#enlaces=enlaces2[ed]
		#print enlaces[ed].split(" ")
		links = enlaces[ed].split(" ")
		#~ c.execute("SELECT contador FROM "+str(tabenlaces)+" WHERE palabra_source = '"+str(links[0])+"' AND palabra_target = '"+str(links[1])+"' AND perfil = '"+str(id_perfil)+"' AND sentido_manual = '"+str(tipoEnlace)+"'")
		#~ salida = c.fetchall()
	#~ 
		#~ if len(salida) == 0:
			#~ salida = 0
		#~ else:
			#~ salida = salida[0]
			#~ salida = salida[0]
		#~ 
		#~ salida += 1
		#~ if salida == 1:
		if (links[0] in stopword) and (links[1] in stopword) :
			c.execute("INSERT INTO `"+str(tabenlaces)+"`(`palabra_source`,`palabra_target`,`sentido_manual`,`perfil`,`stop_word`,`id_perfil_articulo`,`fecha_articulo`) VALUES ('"+str(links[0])+"','"+str(links[1])+"','"+str(tipoEnlace)+"','"+str(id_perfil)+"','1','"+str(id_articulo)+"','"+str(fecha_pub)+"')")
		else:
			c.execute("INSERT INTO `"+str(tabenlaces)+"`(`palabra_source`,`palabra_target`,`sentido_manual`,`perfil`,`stop_word`,`id_perfil_articulo`,`fecha_articulo`) VALUES ('"+str(links[0])+"','"+str(links[1])+"','"+str(tipoEnlace)+"','"+str(id_perfil)+"','0','"+str(id_articulo)+"','"+str(fecha_pub)+"')")
		#~ else:
			#~ c.execute("UPDATE "+str(tabenlaces)+" SET contador = '"+str(salida)+"' WHERE palabra_source = '"+str(links[0])+"' AND palabra_target = '"+str(links[1])+"' AND perfil = '"+str(id_perfil)+"' AND sentido_manual = '"+str(tipoEnlace)+"'")
		
	return enlaces
	
# REEMPLAZA EMOTICONOS #
def reempEmoticon(cuerpo):
	emoticonpositivo =" emoticonpositivo "
	emoticonnegativo =" emoticonegativo "
	
	emoticonP = [":)","XD","(:",":D",":-)","(-:","=D","=)","(=",";-)",";)",";D","<3",":3"]
	emoticonN = [":(","):",":-(",")-:","D:","D=","=(",")=",":'(","='[",":_(","/T_T","TOT",";_;"]
	
	for i in range(len(emoticonP)):
		cuerpo=cuerpo.replace(emoticonP[i],emoticonpositivo)
	for i in range(len(emoticonN)):
		cuerpo=cuerpo.replace(emoticonN[i],emoticonnegativo)
	return cuerpo
	
# REEMPLAZA LETRAS REPETIDAS #
def repChar(cuerpo):

	cuerpo=re.sub("(http|www|htpt).+","<URL>",cuerpo)
	cuerpo=re.sub("á+","a",cuerpo)
	cuerpo=re.sub("é","e",cuerpo)
	cuerpo=re.sub("(í|ï)+","i",cuerpo)
	cuerpo=re.sub("ó","o",cuerpo)
	cuerpo=re.sub("(ú|ü)+","u",cuerpo)
	expReg = ["a","b","c","d","f","g","h","i","j","k","m","n","p","q","s","u","v","w","x","y","z"]
	for i in range(len(expReg)):
		cuerpo=re.sub(expReg[i]+'{2,}', expReg[i], cuerpo)
	return cuerpo

# ELIMINA CARACTERES RAROS #
def strChar(cuerpo):
	strangeChar = ["/","*","\\","\"","%",";",",",":",".",u"¡","?",u"¡","!","\'","_","-","(",")","]","[","//","<",">",u"“",u"”"]
	cuerpo=cuerpo.replace(","," ")
	cuerpo=cuerpo.replace("."," ")
	cuerpo=cuerpo.replace("-"," ")
	#se le quitara el signo igual
	cuerpo=cuerpo.replace("="," ")
	cuerpo=cuerpo.replace(u"¿"," ")
	cuerpo=cuerpo.replace(u"»"," ")
	cuerpo=cuerpo.replace(u"«"," ")
	cuerpo=cuerpo.replace(u"…"," ")
	for i in range(len(strangeChar)):		
		cuerpo=cuerpo.replace(strangeChar[i],"")
	cuerpo=re.sub(" {2,}"," ",cuerpo)	
	return cuerpo

# NORMALIZA SEGUN HASHTAGS, URLS, ETC #
def normalizar(palabras):

	for i in range (len(palabras)):
		if "@" in palabras[i]:
			palabras[i]="<MENCION>"
		if "#" in palabras[i]:
			palabras[i]="<HASHTAG>"
		if "www" in palabras[i] or "http" in palabras[i] or "htpt" in palabras[i] or "URL" in palabras[i]:
			palabras[i]="<URL>"
		if "$" in palabras[i]:
			palabras[i]="<MONEDA>"
		if palabras[i].isdigit():
			palabras[i]="<NUMERO>"
		if len(palabras[i])>= 40:
			aux = palabras[i]
			aux = aux[0:39]
			palabras[i] = aux
	return palabras

# MODIFICA PLURALES Y SUFIJOS #
def sufijos(palabras,leaves):
	#~ for leaf in leaves:
		#~ for i in range (len(palabras)):
			#~ if palabras[i][-len(leaf):] == leaf:
				#~ palabras[i]=palabras[i][:-len(leaf)]
	return palabras

# BALANCEAR #
def balancear(perfil,c,balan):
	balance=[]

	#0 neutro; 1 positivo; 2 negativo
	for i in range(3):
		#c.execute("SELECT COUNT(*) FROM `"+str(tabla)+"` WHERE `plataforma`=0 AND `clasificado`=1 AND `sentido_manual`="+str(i)+" AND id_articulo NOT IN ("+ides+")") #NESTLE
		#c.execute("SELECT COUNT(*) FROM `"+str(tabla)+"` WHERE `plataforma`=0 AND `clasificado`=1 AND `sentido_manual`="+str(i)+" AND `id_etiqueta`=1 AND id_articulo >2098") #BANCOS
		#c.execute("SELECT COUNT(*) FROM `"+str(tabla)+"` WHERE `plataforma`=0 AND `clasificado`=1 AND `sentido_manual`="+str(i)+" AND `id_etiqueta`=80 AND id_articulo <128961") #CONCHA Y TORO
		resultado=c.fetchall()
		for tipo in resultado:
			print tipo[0]
			balance.append(tipo[0])

	bal=sorted(balance)

	if balan=="1":
		min=bal[0]
	if balan=="0":
		min=bal[2]
	return min

# GENERA LA REDES #
def genRedes(c,leaves,tabenlaces,db,fecha_a,fecha_p,perfiles,sopena):
	mensaje="Comenzando la generación d elas redes"
	logging.info(mensaje)
	
	global fecha_ant, fecha_post
	fecha_ant = fecha_a
	fecha_post = fecha_p
	sql="SELECT id_perfil FROM perfiles where estado=0 and id_perfil IN ("+str(perfiles)+")"
	c.execute(sql)
	
	resultado=c.fetchall()
	for fila in resultado:
		id_perfil=fila[0]
		print "Trabajando con perfil " +str(id_perfil)
		logging.info( "Trabajando con perfil " +str(id_perfil))
		
		for i in range(3):
			print "##### GENERO LA REDES "+str(i)+ "#######"
			logging.info("##### Genero los enlaces de las redes"+str(i)+ "#######")
			
			#consulta qu eno pesca en windows  sql="SELECT a.cuerpo, pats.id_perfil_articulo, a.fecha_publicacion from perfiles_articulos pa JOIN articulos a ON pa.id_articulo = a.id_articulo JOIN perfiles_articulos_tipos_sentidos pats ON pats.id_perfil_articulo = pa.id_perfil_articulo WHERE a.id_plataforma = 0 AND pats.clasificado = 1 AND id_perfil="+str(id_perfil)+" AND pats.tipo_sentido = "+str(i)+" AND date(a.fecha_publicacion) <= '"+str(fecha_post)+"' AND date(a.fecha_publicacion) >= '"+str(fecha_ant)+"' order by a.fecha_publicacion desc Limit 1000"
			sql="SELECT cuerpo, id_perfil_articulo, fecha_publicacion from tweets WHERE id_perfil="+str(id_perfil)+" AND tipo_sentido = "+str(i)+" AND date(fecha_publicacion) <= '"+str(fecha_post)+"' AND date(fecha_publicacion) >= '"+str(fecha_ant)+"' order by fecha_publicacion desc Limit 1000"
			#print sql
			logging.info(sql)
			c.execute(sql)
			#print "SELECT a.cuerpo, pats.id_perfil_articulo, a.fecha_publicacion from perfiles_articulos pa JOIN articulos a ON pa.id_articulo = a.id_articulo JOIN perfiles_articulos_tipos_sentidos pats ON pats.id_perfil_articulo = pa.id_perfil_articulo WHERE a.id_plataforma = 0 AND pats.clasificado = 1 AND id_perfil="+str(id_perfil)+" AND pats.tipo_sentido = "+str(i)+" AND date(a.fecha_publicacion) <= '"+str(fecha_post)+"' AND date(a.fecha_publicacion) >= '"+str(fecha_ant)+"' order by a.fecha_publicacion desc Limit 1000"
			
			resultado = c.fetchone()
			
			cuerpo=[]
			id_articulo = []
			articulo_aux = []
			fecha_pub = []
			while resultado != None:
				aux1 = []
				aux1.append(resultado[0])
				aux1.append(resultado[1])
				aux1.append(resultado[2])
				articulo_aux.append(aux1)
				resultado = c.fetchone()

			tamano = len(articulo_aux)
			training = int(tamano*.7)
			testing = int(tamano-training)
			logging.info("tamaño de la red sentido: %s tamaño: %s testing:%s" %(i,tamano,testing))
			numpy.random.shuffle(articulo_aux)

			for j in range(tamano):
				if j < training:
					print j
					cuerpo.append(articulo_aux[j][0])
					id_articulo.append(articulo_aux[j][1])
					fecha_pub.append(articulo_aux[j][2])
					c.execute("INSERT INTO entrenamiento_fondecyt (id_tweet) VALUES ('"+str(articulo_aux[j][1])+"')")
					db.commit()
					#entrenamiento.writerow(['"'+articulo_aux[j][0].encode('utf-8')+'"',articulo_aux[j][1],articulo_aux[j][2],i])
				else:
					c.execute("INSERT INTO rand_fondecyt (id_tweet) VALUES ('"+str(articulo_aux[j][1])+"')")
					db.commit()
					#evaluacion.writerow(['"'+articulo_aux[j][0].encode('utf-8')+'"',str(articulo_aux[j][1]).encode('utf-8'),articulo_aux[j][2],i])
					
			#cuerpo = str(cuerpo)
			#print cuerpo[1]
			
			for j in range(len(cuerpo)):
				print "Tweet " + str(j) +" de "+str(len(cuerpo))
				cuerpo[j] = procesarCuerpo(cuerpo[j])
				palabras = tokenizar(cuerpo[j],leaves)
				bloquePesos(palabras,c,id_perfil,tabenlaces,id_articulo[j],i,fecha_pub[j],sopena)
				
			
# GENERA REDES PARA NETSENSE #
def genRedNetsense(i,g,balance,stpw,perfil,umbralpeso,c,fecha_ant,fecha_post):
	g = nx.DiGraph()
	global evaluacion,tiempo_entrenamiento
	tiempo_entrenamiento=time.time()
	stpw = str(evaluacion[3])
	contador = str(evaluacion[2])
	#revisar el efecto al haber mas de un perfil con fechas similares en la suma, ya que afectaria al peso
	sql="SELECT SUM(CONT) FROM (SELECT count(*) as CONT FROM analitic.enlaces_clasificador_FONDECYT WHERE date(fecha_articulo) >= '"+str(fecha_ant)+"' AND date(fecha_articulo) <= '"+str(fecha_post)+"' group by palabra_source , palabra_target) AS CONT"
	print sql
	c.execute(sql)
	suma_total = c.fetchone()
	suma_total = int(suma_total[0])
	print "suma total %d" %(suma_total)

	if stpw=="0":
		if balance=="0":
			#print " SELECT `palabra_source`,`palabra_target`,`weight` FROM `enlaces_clasificador_FONDECYT` WHERE `sentido_manual`="+str(i)+" AND `perfil`='"+str(perfil)+"' AND `stop_word`= '0' AND `contador`>'" + str(contador)+"' "
			sql= "SELECT palabra_source, palabra_target, count(*) AS CONT FROM `enlaces_clasificador_FONDECYT` WHERE `sentido_manual`="+str(i)+" AND `perfil`='"+str(perfil)+"' AND `stop_word`= '0' AND date(fecha_articulo) >= '"+str(fecha_ant)+"' AND date(fecha_articulo) <= '"+str(fecha_post)+"' group by palabra_source , palabra_target having CONT > "+str(contador)
			c.execute(sql)
			resultadoC=c.fetchall()			
			
	if stpw=="1":
		if balance=="0":
			#print "Estoy haciendo la red de positivos desde la perfil "+str(perfil)+" con stopwords y entrenados desbalanceados."
			#print "SELECT `palabra_source`,`palabra_target`,`weight` FROM `enlaces_clasificador_FONDECYT` WHERE `sentido_manual`="+str(i)+" AND `perfil`='"+str(perfil)+"'  AND `contador`>'"+str(contador)+"' "
			c.execute("SELECT palabra_source, palabra_target, count(*) AS CONT FROM `enlaces_clasificador_FONDECYT` WHERE `sentido_manual`="+str(i)+" AND `perfil`='"+str(perfil)+"' AND date(fecha_articulo) >= '"+str(fecha_ant)+"' AND date(fecha_articulo) <= '"+str(fecha_post)+"' group by palabra_source , palabra_target having CONT > "+str(contador))
			#c.execute(" SELECT `palabra_source`,`palabra_target`,`weight` FROM `enlaces_clasificador_FONDECYT` WHERE `sentido_manual`=1 ") # TOMA TODOS LOS ENLACES DE TODAS LAS TABLAS
			resultadoC=c.fetchall()
		
			
	for reg in resultadoC:
		peso_ind = float(1/float(reg[2]))
		peso_ind = peso_ind/float(suma_total)
		g.add_edge(reg[0],reg[1],weight=peso_ind)
		
	tiempo_entrenamiento=time.time()- tiempo_entrenamiento
	return g
	
def revisarAnew(tweetwords,c):		  
	global evaluacion
	anew = 0
	val = 0
	contval=1
	for j in range (len(tweetwords)):
		#print tweetwords[j]
		c.execute("SELECT valence FROM `anew` WHERE `word`='"+tweetwords[j]+"'")
		resultadoanew=c.fetchall()		
		if len(resultadoanew)==0:
			anew=0
		else:
			contval += 1
			for an in resultadoanew:
				anew=float(an[0])
				val=anew+val
				#print tweetwords[j]
	if evaluacion[1]==1 or contval == 1:
		valence=0
		#print "sin valence"
	else:
		valence=float(val/(contval-1))
		#print "valence "+str(valence)+ " por " +str(contval-1)+ " palabras"
		#if valence == 0:
		#       print "este tweet no cae dentro de anew"
	return valence,contval
	
def procesarTweet(tweet,emoticon,stpw,tweetwords):
	stopword = stopWords()
	for i in range (len(tweet)):
		#print tweet[i]
		if tweet[i]=="emoticonpositivo":
			emoticon[1] += 1
			#print ":)" 
		if tweet[i]=="emoticonegativo":
			emoticon[2] += 1
			#print ":("
		if stpw=="0":
			if tweet[i] not in stopword and len(tweet[i]) > 1:
				tweetwords.append(tweet[i])					
		if stpw=="1":
			tweetwords.append(tweet[i])
	return [emoticon,tweetwords]
	
# EVALUA REDES #  
def evaluarRed(tweetwords,nodes,analisis,i,g,ponderadis,ponderapares,emoticon,valence,contval,sopena):
	distancia=0
	pares=0

	#print "______EVALUO________"
	#print "palabras del tweet a evaluar: "+ str(len(tweetwords))
	db1 = MySQLdb.connect("127.0.0.1","root","","analitic",charset ="utf8",init_command="set names utf8",use_unicode=True)
	#db1.names = "utf-8"
	c1 = db1.cursor()
	stopword = stopWords()
	for k in range (len(tweetwords)-1):
		#print "Palabras " + str(tweetwords[k])+" y "+str(tweetwords[k+1]) +" en +"
		if tweetwords[k] not in stopword:
			tweetwords[k] = cambiarPalabraS(tweetwords[k],c1,sopena)
		if tweetwords[k+1] not in stopword:
			tweetwords[k+1] = cambiarPalabraS(tweetwords[k+1],c1,sopena)
		
		if (tweetwords[k] in nodes) and (tweetwords[k+1] in nodes):
			pares += 1
			print tweetwords[k] +" y "+tweetwords[k+1]  + " Estan presentes en G"+str(i)
			try:
				if analisis==0:
					dis=nx.shortest_path_length(g,source=tweetwords[k],target=tweetwords[k+1])
				if analisis==1: 
					try:
						dis=len(nx.shortest_path(g,source=tweetwords[k],target=tweetwords[k+1],weight='weight')) - 1
					except:
						dis = 0
				print "G" + str(i) + "-"+str(dis)
				distancia=distancia+dis
			except nx.NetworkXNoPath, e:
				pares -= 1
				#print dis
				#print "Entre "+ str(tweetwords[k])+" y "+str(tweetwords[k+1])+" no hay camino." #SI NO HAY CAMINO LA DISTANCIA DEBERIA SER INFINITA

	print "______RESULTADO ________"
	
	print "La suma de distancias es "+ str(distancia)
	print "Hubo: "+ str(pares) + " pares"
	#print "En promedio la distancia es "+ str(distancia/pares) 
	pares=float(pares)
	print "pares: "+str(pares)
	dis=float(distancia)
	if pares == 0:
		promdis = 0
	else:
		promdis=float((dis/pares)*float(ponderadis))
	print "promdis: "+str(promdis)
	print "pares: "+str(pares)
	print "emoticon: "+str(emoticon)
	costo = calculaCosto(promdis,pares,ponderapares,emoticon,valence,contval,i)
	return costo,pares

# DECISION POR PARES #
def decPar(paresneu,parespos,paresneg,id,c):
	if (parespos == 1) and (paresneu == 1) and (paresneg > 1):
		consultaDecision(2,id,c)
	if (paresneg == 1) and (paresneu == 1) and (parespos > 1):
		consultaDecision(1,id,c)
	if (paresneg == 1) and (parespos == 1) and (paresneu > 1):
		consultaDecision(0,id,c)
	if (parespos == 1) and (paresneg == 1) and (paresneu == 1):
		consultaDecision(5,id,c)

# DECISION POR COSTO DE PRODUCCION #     
def decCostoProd(costoneu,costopos,costoneg,id,c):
	if (costopos > costoneg) and (costoneu > costoneg):
		consultaDecision(2,id,c)
	if (costopos < costoneg) and (costopos < costoneu):
		consultaDecision(1,id,c)
	if (costoneu < costoneg) and (costoneu < costopos):
		consultaDecision(0,id,c)
	if (costoneu == costoneg) and (costoneg == costopos) and (costopos==costoneg):
		consultaDecision(0,id,c)
	if ((costoneu == costopos) and (costoneu < costoneg)) or ((costoneu == costoneg) and (costoneu < costopos)):
		consultaDecision(0,id,c)
	if (costoneu == costopos) and (costoneu > costoneg):
		consultaDecision(2,id,c)
	if (costoneu == costoneg) and (costoneu > costopos):
		consultaDecision(1,id,c)

# DECISION POR COSTOS SIMILARES #     
def decCostoSim(costoneu,costopos,costoneg,id,c):
	if (costopos < costoneu) and (costoneg < costoneu):
		if (costopos == costoneg):
			consultaDecision(0,id,c)
	if (costopos < costoneg) and (costoneu < costoneg):
		if costopos == costoneu:
			consultaDecision(0,id,c)
	if (costoneg < costopos) and (costoneu < costopos):
		if costoneg == costoneu:
			consultaDecision(0,id,c)

# DECISION POR COSTOS #		
def decCosto(paresneu,parespos,paresneg,costoneu,costopos,costoneg,id,c):
	if ((parespos == 0) and (paresneg > 0) and (paresneu > 0)) or ((parespos > 0) and (paresneg == 0) and (paresneu > 0)) or ((parespos > 0) and (paresneg > 0) and (paresneu == 0)) or ((parespos > 0) and (paresneg > 0) and (paresneu > 0)):
		decCostoProd(costoneu,costopos,costoneg,id,c)
		decCostoSim(costoneu,costopos,costoneg,id,c)
		
# DECISION #
def decision(paresneu,parespos,paresneg,costoneu,costopos,costoneg,id,c):
	#### DECISION POR PARES
	decPar(paresneu,parespos,paresneg,id,c)
	#### DECISION POR COSTOS
	decCosto(paresneu,parespos,paresneg,costoneu,costopos,costoneg,id,c)
	if costopos==0:
		if costoneg==costoneu:
			consultaDecision(0,id,c)
		else:
			if costoneg>costoneu:
				consultaDecision(0,id,c)
			else:
				consultaDecision(2,id,c)
	if costoneg==0:
		if costopos==costoneu:
			consultaDecision(0,id,c)
		else:
			if costopos>costoneu:
				consultaDecision(0,id,c)
			else:
				consultaDecision(1,id,c)
	if costoneu==0:
		if costopos==costoneg:
			consultaDecision(0,id,c)
		else:
			if costopos>costoneg:
				consultaDecision(2,id,c)
			else:
				consultaDecision(1,id,c)
	if (costoneu==0) and (costoneg==0) and (costopos>0):
		consultaDecision(1,id,c)
	if (costoneu==0) and (costopos==0) and (costoneg>0):
		consultaDecision(2,id,c)
	if (costoneg==0) and (costopos==0) and (costoneu>0):
		consultaDecision(0,id,c)
	if (costoneu==0) and (costopos==0) and (costoneg==0):
		consultaDecision(5,id,c)

def consultaDecision(tipo_sentido,id,c):
	global tipo, tipo_ev
	if tipo_sentido == 0:
		print "el tweet es neutro"
	if tipo_sentido == 1:
		print "el tweet es positivo"
	if tipo_sentido == 2:
		print "el tweet es negativo"
	if tipo_sentido == 5:
		print "el tweet es no se puede clasificar"
	if tipo == 0:
		c.execute("UPDATE `perfiles_articulos_tipos_sentidos` SET `tipo_sentido`='"+str(tipo_sentido)+"', `clasificado`='2' WHERE `id_perfil_articulo`='"+str(id)+"'")
	if tipo == 1:
		c.execute("UPDATE `evaluador_netsense_SENTIDO_FONDECYT` SET `"+str(tipo_ev)+"`='"+str(tipo_sentido)+"' WHERE `id_perfil_articulo`='"+str(id)+"'")
	
	
def procesaNetsense(db, perfil,tpo,ev,fecha_a,fecha_p,fecha_e,sopena,leaves ="s",  stpw="1", balance="0",
		ponderapares=2, ponderadis=1, umbralpeso=1):
	global tipo,tipo_ev,evaluacion, fecha_post,tiempo_inicio
	tiempo_inicio=time.time()
	fecha_post = fecha_p
	evaluacion = ev
	analisis = evaluacion[0]
	stpw= str(evaluacion[3])
	g = [0,0,0]
	enlaces = [0,0,0]
	nodes = [0,0,0]
	nod = [0,0,0]
	nodos = []
	tipo = tpo
	c = db.cursor()
	print '_*_*_*_*_*_*_*_*_*_*\n'
	print 'perfil: '+str(perfil)
	#print 'tipo de analisis: '+str(w)
	print 'stopwords: '+str(stpw)
	print 'balance: '+str(balance)
	print 'ponderapares: '+str(ponderapares)
	print 'ponderadis: '+str(ponderadis)
	print 'umbral peso: '+str(umbralpeso)
	print 'tipo: '+str(tipo)
	if analisis == 0:
		tipo_ev = "netsense"
	if analisis == 1:
		tipo_ev = "netsense_w"
	# SE GENERAN LAS REDES #
	for i in range(3):
		
		g[i] = genRedNetsense(i,g[i],balance,stpw,perfil,umbralpeso,c,fecha_a,fecha_p)  
		#save(g[i],"json/Red"+str(i)+"-"+str(datetime.today())+".json")  
		enlaces[i] = g[i].edges()
		nodes[i] = g[i].nodes()
		nodos.append(len(nodes[i]))
	bal=sorted(nodos)
	
	#float(ponderapares)
	#balpos=1-(float(len(nodes)))/bal[2]
	#balneg=1-(float(len(nodes2)))/bal[2]
	#balneu=1-(float(len(nodes3)))/bal[2]   
	
	if len(nodes[0]) != 0 and  len(nodes[1]) != 0 and  len(nodes[2]) != 0:

		print "Datos de la red"
		for i in range(3):
			print "Nodos +: "+str(len(nodes[i]))+" Enlaces +: "+str(len(enlaces[i]))
			nod[i]=float(len(nodes[i]))
		
		##### ESCOJO TWEETS A EVALUAR #######
		resultadotweet=escogerTweetsEvaluar(c,perfil,db,fecha_e)
		
		id=[]
		tweet=[]
		contweet=0
		for regtweet in resultadotweet:
			#print regtweet
			twe = regtweet[0].replace("'","''")
			c.execute("INSERT INTO evaluador_netsense_SENTIDO_FONDECYT (id_perfil_articulo,cuerpo,sentido_manual,fecha) VALUES ('"+str(regtweet[1])+"','"+twe+"','"+str(regtweet[2])+"','"+str(regtweet[3])+"')")
			db.commit()
			
			emoticon = [0,0,0]
			costo = [0,0,0]
			pares = [0,0,0]	
			tweetwords=[]	
			contweet += 1
			tweet=regtweet[0]
			id=str(regtweet[1])

			
			#hay qye cambiarloprint str(contweet)+") " + tweet + "-> id:" +str(id)
			
			tweet = reempEmoticon(tweet) 
			tweet = tweet.replace("RT"," ")
			tweet = tweet.lower()
			tweet = repChar(tweet)
			tweet = strChar(tweet)
			
			#print tweet
			
			tweet=tweet.split()	
			[emoticon,tweetwords] = procesarTweet(tweet,emoticon,stpw,tweetwords)
			[valence,contval] = revisarAnew(tweetwords,c)			
			tweetwords = normalizar(tweetwords)
			tweetwords = sufijos(tweetwords,leaves)
			for i in range(3):
				if i == 0:
					[costo[i],pares[i]] = evaluarRed(tweetwords,nodes[i],analisis,i,g[i],ponderadis,ponderapares,emoticon[i],0,0,sopena)
				else:
					[costo[i],pares[i]] = evaluarRed(tweetwords,nodes[i],analisis,i,g[i],ponderadis,ponderapares,emoticon[i],valence,contval,sopena)

			
			print "Costo de produccion: [0] ->"+str(costo[0])+ " [+] ->"+str(costo[1])+ " [-] ->"+str(costo[2])
			
			decision(pares[0],pares[1],pares[2],costo[0],costo[1],costo[2],id,c)
				
			##print "_____________________________________________"             
			print '_*_*_*_*_*_*_*_*_*_*\n'

			tweet=[]
			#sql="SELECT tipo_sentido FROM perfiles_articulos_tipos_sentidos WHERE `id_perfil_articulo`='"+str(id)+"'"
			sql="SELECT tipo_sentido FROM tweets WHERE `id_perfil_articulo`='"+str(id)+"'"
			c.execute(sql)
			resultado=c.fetchone()
			c.execute("INSERT INTO log_clasificacion_FONDECYT (tipo_sentido, fecha, id_perfil_articulo, clasificado) VALUES ("+str(resultado[0])+",now(),"+str(id)+",2)")

	else:
		print "El tweet no se clasifico por no tener nodos"
	if tipo == 1:
		
		calculosFinales(c,perfil,nodes,enlaces,db)

	db.commit()
#Salvar La red			
def save(G, fname):
	json.dump(dict(nodes=[[n, G.node[n]] for n in G.nodes()],
                   edges=[[u, v, G.edge[u][v]] for u,v in G.edges()]),
              open(fname, 'w',), indent=2)

# ESCOGER TWEETS A EVALUAR #
def escogerTweetsEvaluar(c,perfil,db,fecha_ev):
	
	global tipo
	tw = ""
	c.execute("SELECT * FROM rand_FONDECYT")
	resultado = c.fetchone()
	
	while resultado != None:
		tw = tw + str(resultado[0])
		resultado = c.fetchone()
		if resultado != None:
			tw = tw + ","
		
	if tipo==1:
		#sql="SELECT a.cuerpo, pats.id_perfil_articulo, pats.tipo_sentido, a.fecha_publicacion FROM perfiles_articulos pa JOIN articulos a ON pa.id_articulo = a.id_articulo JOIN perfiles_articulos_tipos_sentidos pats ON pats.id_perfil_articulo = pa.id_perfil_articulo WHERE a.id_plataforma = 0 AND pats.clasificado = 1 AND id_perfil="+str(perfil)+" AND pats.id_perfil_articulo IN ("+str(tw)+") "
		sql="SELECT cuerpo, id_perfil_articulo, tipo_sentido, fecha_publicacion FROM tweets WHERE id_perfil="+str(perfil)+" AND id_perfil_articulo IN ("+str(tw)+") "
		print (sql)
		c.execute(sql) # order by rand() limit 10")
		#c.execute("SELECT a.cuerpo, pats.id_perfil_articulo, pats.tipo_sentido, a.fecha_publicacion FROM perfiles_articulos pa JOIN articulos a ON pa.id_articulo = a.id_articulo JOIN perfiles_articulos_tipos_sentidos pats ON pats.id_perfil_articulo = pa.id_perfil_articulo WHERE a.id_plataforma = 0 AND pats.clasificado = 1 AND id_perfil="+str(perfil)+" AND date(a.fecha_publicacion) = date(DATE_SUB(now(),INTERVAL 1 DAY))")
	
	if tipo==0:
	 
		c.execute("SELECT a.cuerpo, pats.id_perfil_articulo, pats.tipo_sentido FROM perfiles_articulos pa JOIN articulos a ON pa.id_articulo = a.id_articulo JOIN perfiles_articulos_tipos_sentidos pats ON pats.id_perfil_articulo = pa.id_perfil_articulo WHERE a.id_plataforma = 0 AND pats.tipo_sentido = -1 AND id_perfil="+str(perfil)+" AND pats.id_perfil_articulo IN ("+str(tw)+")")    
	resultadotweet=c.fetchall()
	
	return resultadotweet

def calculaCosto(promdis,pares,ponderapares,emoticon,valence,contval,i):
	global evaluacion
	valaux = 0
	if pares == 0:
		costo = 0
	else:
		costo=((promdis)/(pares**float(ponderapares))) - (emoticon)
	if i == 1:
		valaux = valence -5
		
	if i == 2:
		valaux = 4-valence
	
	if i == 0 or evaluacion[1]==1:
		valaux=0
	#print contval
	print "valaux : "+ str(valaux)
	#valaux=0
	if pares !=0:
		costo=costo-((valaux)*(contval-1)/1000)
	
	
	return costo

def calculosFinales(c,perfil,nodes,enlaces,db):
	global tipo_ev,evaluacion,tiempo_inicio,tiempo_entrenamiento
	#print "SELECT COUNT(*) FROM evaluador_netsense_SENTIDO en JOIN perfiles_articulos pa USING (id_perfil_articulo) WHERE `"+str(w)+"`!= 5 AND pa.id_perfil="+str(perfil)+""
	#sql="SELECT COUNT(*) FROM evaluador_netsense_SENTIDO_FONDECYT en JOIN perfiles_articulos pa USING (id_perfil_articulo) WHERE  pa.id_perfil="+str(perfil)+""
	sql="SELECT COUNT(*) FROM evaluador_netsense_SENTIDO_FONDECYT en JOIN tweets t USING (id_perfil_articulo) WHERE  id_perfil="+str(perfil)+""
	c.execute(sql)
	consulta=c.fetchall()
	for reg in consulta:
		#print "Tweets totales evaluados: "+str(reg[0])
		Total=reg[0]
	#print "SELECT COUNT(*) FROM evaluador_netsense_SENTIDO en JOIN perfiles_articulos pa USING (id_perfil_articulo) WHERE `"+str(w)+"`= 5 AND pa.id_perfil="+str(perfil)+""
	#sql="SELECT COUNT(*) FROM evaluador_netsense_SENTIDO_FONDECYT en JOIN perfiles_articulos pa USING (id_perfil_articulo) WHERE "+str(tipo_ev)+"= 5 AND pa.id_perfil="+str(perfil)+" ") #AND date(fecha) = date(DATE_SUB(now(),INTERVAL 1 DAY))"
	sql="SELECT COUNT(*) FROM evaluador_netsense_SENTIDO_FONDECYT en JOIN tweets t USING (id_perfil_articulo) WHERE "+str(tipo_ev)+"= 5 AND id_perfil="+str(perfil)+" "
	print sql
	c.execute(sql)
	consulta=c.fetchall()
	for reg in consulta:
		sineva=reg[0]
	
	if Total !=0:
		print "Tweets sin clasificar: "+str((float(sineva)/float(Total))*100)+"%" +", "+ str(sineva) + " de " + str(Total)
		menciones_evaluadas=100-((float(sineva)/float(Total))*100)
		#c.execute("INSERT INTO evaluacion_historica_netsense_SENTIDO(menciones_evaluadas) VALUES ("+str((float(sineva)/float(Total))*100)+")")

		TP_u=0
		TP = [0,0,0]
		FP_u=0
		FP = [0,0,0]
		FN_u=0
		FN = [0,0,0]
		TN = [0,0,0]
		accu = [0,0,0]
		pre = [0,0,0]
		rec = [0,0,0]
		
		#print "PERFORMANCE"
		for i in range(3):
			print i
			sql="SELECT COUNT(*) FROM `evaluador_netsense_SENTIDO_FONDECYT` WHERE `sentido_manual`="+str(i)+" and "+str(tipo_ev)+"= "+str(i)+" AND "+str(tipo_ev)+"!= 5 "
			c.execute(sql)
			consulta=c.fetchall()
			print consulta


			for reg in consulta:
				#print "TPn: "+str(reg[0])
				TP[i]=float(reg[0])
				TP_u += TP[i]
			sql="SELECT COUNT(*) FROM `evaluador_netsense_SENTIDO_FONDECYT` WHERE `sentido_manual`!= "+str(i)+" and "+str(tipo_ev)+"= "+str(i)+" AND "+str(tipo_ev)+"!= 5 "	
			c.execute(sql)
			consulta=c.fetchall()
		
			for reg in consulta:
				#print "FPn: "+str(reg[0])
				FP[i]=float(reg[0])
				FP_u += FP[i]
			sql="SELECT COUNT(*) FROM `evaluador_netsense_SENTIDO_FONDECYT` WHERE `sentido_manual`= "+str(i)+" and "+str(tipo_ev)+"!= "+str(i)+" AND "+str(tipo_ev)+"!= 5 "	
			c.execute(sql)
			consulta=c.fetchall()
			
			for reg in consulta:
				#print "FNn: "+str(reg[0])
				FN[i]=float(reg[0])
				FN_u += FN[i]
					
			#print "TNn: "+str(Total-(TPn+FPn+FNn))
			TN[i] = float(Total-(TP[i]+FP[i]+FN[i]))
			
			#print "_*_*_*_*_*_*_*_*_*_*"
			if (TP[i]+FP[i]+FN[i]+TN[i]) !=0:
				accu[i]=float((TP[i]+TN[i])/(TP[i]+FP[i]+FN[i]+TN[i]))
				#print "Accuracy: " + str(accun)
			else:
				#print "Accuracy: No definido (/0)"
				accu[i]=0
			
			if (TP[i]+FP[i]) !=0:
				pre[i]=float((TP[i])/(TP[i]+FP[i]))     
				print "Precission: " + str(pre[i])
			else:
				#print "Precission: No definido (/0)"
				pre[i]=0
			
			if (TP[i]+FN[i]) !=0:
				rec[i]=float((TP[i])/(TP[i]+FN[i]))
				print "Recall: " + str(rec[i])
			else:
				#print "Recall: No definido (/0)"
				rec[i]=0
			#try:
			#    print "F-1: "+str( 2*pren*recn/(pren+recn) )
			#    f.write("F-1: "+str( 2*pren*recn/(pren+recn) ))
			#except:
			#    pass
			print "_*_*_*_*_*_*_*_*_*_*"
			#f.write("\n_*_*_*_*_*_*_*_*_*_*\n")
		print "_*_*_*_*_*_*"
		print "microaverage"
		print "_*_*_*_*_*_*"
		
		#print str(TP_u)+" kkakaka"
		#print str(FP_u)+" kkakaka"
		#print str(FN_u)+" kkakaka"
		
	
		print "Precision: " + str(float(TP_u/(TP_u+FP_u)))
		microPRE=float(TP_u/(TP_u+FP_u))
		print "Recall: " + str(float(TP_u/(TP_u+FN_u)))
		microREC=float(TP_u/(TP_u+FN_u))
		print "F-measure: " + str(2*microPRE*microREC/(microPRE+microREC))
		print "_*_*_*_*_*_*"
		print "MACROaverage"
		print "_*_*_*_*_*_*"
		print "Precision: " + str(float(pre[0]+pre[1]+pre[2])/3)
		MACROPRE=float((pre[0]+pre[1]+pre[2])/3)
		print "Recall: " + str(float(rec[0]+rec[1]+rec[2])/3)
		MACROREC=float((rec[0]+rec[1]+rec[2])/3)
		print "F-measure: " + str(2*MACROPRE*MACROREC/(MACROPRE+MACROREC))
		#Se imprime la matriz de confusion de la evaluacion
		
		sql="SELECT sentido_manual,"+str(tipo_ev)+",count(*) FROM analitic.evaluador_netsense_sentido_fondecyt where "+str(tipo_ev)+" != 5 group by sentido_manual,"+str(tipo_ev)+""
		print sql
		c.execute(sql)
		matriz=[[0,0,0],[0,0,0],[0,0,0]]
		
		resultado=c.fetchall()
		for reg in resultado:
			matriz[reg[0]][reg[1]]=reg[2]
		
		
		minu=int(tiempo_entrenamiento/60)  
		seg=(tiempo_entrenamiento-(minu*60)) 
		tiempoEntrenamiento=str(minu)+"m "+str(seg)+"s"
		tiempoTotal=time.time()-tiempo_inicio
		minu=int(tiempoTotal/60)  
		seg=(tiempoTotal-(minu*60)) 
		tiempo=str(minu)+"m "+str(seg)+"s"
		comentario = "Analisis: "+str(evaluacion[0])+" - Valence:"+str(evaluacion[1])+" - Stopword: "+str(evaluacion[3])+" - Contador: "+str(evaluacion[2])
		sql="INSERT INTO evaluacion_historica_netsense_SENTIDO_FONDECYT(comentario,fecha,porcentaje_clasificado,perfil,tipo_evaluacion,prec_micro, recall_micro,prec_macro, recall_macro,f1_micro,f1_macro,pre_pos,rec_pos,pre_neg,rec_neg,pre_neu,rec_neu,tweets_ev,tiempo_evaluacion,tiempo_entrenamiento) VALUES('"+str(comentario)+"',now(),"+str(menciones_evaluadas)+","+str(perfil)+",'"+str(tipo_ev)+"',"+str(microPRE)+","+str(microREC)+","+str(MACROPRE)+","+str(MACROREC)+","+str(2*microPRE*microREC/(microPRE+microREC))+","+str(2*MACROPRE*MACROREC/(MACROPRE+MACROREC))+","+str(pre[1])+","+str(rec[1])+","+str(pre[2])+","+str(rec[2])+","+str(pre[0])+","+str(rec[0])+","+str(Total)+",'"+str(tiempo)+"','"+str(tiempoEntrenamiento)+"')"
		print sql
		c.execute(sql)
		
		id_evaluacion_historica=db.insert_id()
		
		sql="INSERT INTO matriz_confusion(id_evaluacion_historica,neutro_neutro,neutro_positivo,neutro_negativo,positivo_neutro,positivo_positivo,positivo_negativo,negativo_neutro,negativo_positivo,negativo_negativo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" %(id_evaluacion_historica,int(matriz[0][0]),int(matriz[0][1]),int(matriz[0][2]),int(matriz[1][0]),int(matriz[1][1]),int(matriz[1][2]),int(matriz[2][0]),int(matriz[2][1]),int(matriz[2][2]))
		print sql
		c.execute(sql)
		c.execute("INSERT INTO tamano_entrenamiento_SENTIDO_FONDECYT(id_evaluacion_historica,nodos_positivos,nodos_negativos,nodos_neutros,enlaces_positivos,enlaces_negativos,enlaces_neutros) VALUES ("+str(id_evaluacion_historica)+","+str(len(nodes[1]))+","+str(len(nodes[2]))+","+str(len(nodes[0]))+","+str(len(enlaces[1]))+","+str(len(enlaces[2]))+","+str(len(enlaces[0]))+")")
		
		sql="insert into log_clasificacion(select *,%s,%s from evaluador_netsense_sentido_fondecyt)" %(str(perfil),str(id_evaluacion_historica))
		c.execute(sql)
		
		'''print "Neutros", TP[0],FN[0],FP[0],TN[0]
		print "Positivos", TP[1],FN[1],FP[1],TN[1]
		print "Negativos", TP[2],FN[2],FP[2],TN[2]'''
		db.commit()
		
