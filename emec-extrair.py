#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests, json, time, base64, io, random, os, codecs
from string import digits
from threading import Thread
from threading import Lock
from threading import BoundedSemaphore

def getCursoNome(cursos_ies, cursos_unidades, requi, unidades, cod64, semaforo_curso, semaforo_controle, mutex_cursos, qt_cursos, nome):
	cod64nome_curso = base64.b64encode(nome.encode('utf-8')).decode('utf-8')
	link2 = "http://emec.mec.gov.br/emec/consulta-curso/listar-curso-desagrupado/9f1aa921d96ca1df24a34474cc171f61/0/d96957f455f6405d14c6542552b0f6eb/"+cod64+"/c1b85ea4d704f246bcced664fdaeddb6/"+cod64nome_curso+"/list/5000"
	while True:
		try:
			r = s.get(link2)
			page_curso = BeautifulSoup(r.content, 'html.parser')

			if r.status_code != 200:
				requi["erros"] += 1
				time.sleep(30)
				continue

			requi["requisicoes"] += 1

			break
		except:
			requi["erros"] += 1

	id_cursos_prontos = {}
	cursos = page_curso.find_all("tr")[1::]
	for curso in cursos:
		td_curso = [x.text.strip() for x in curso.find_all("td")]
		
		if "Nenhum registro encontrado" in td_curso[0]:
			break

		codigo_curso = td_curso[0]

		if codigo_curso in id_cursos_prontos:
			continue

		id_cursos_prontos[codigo_curso] = True

		cod_curso64 = base64.b64encode(codigo_curso.encode('ascii')).decode('ascii')
		indice_historico_curso = []

		# DETALHES DO CURSO
		link2 = "http://emec.mec.gov.br/emec/consulta-curso/detalhe-curso-tabela/c1999930082674af6577f0c513f05a96/"+cod_curso64

		while True:
			try:
				r = s.get(link2)
				page_detalhes_curso = BeautifulSoup(r.content, 'html.parser')

				if r.status_code != 200:
					requi["erros"] += 1
					time.sleep(30)
					continue

				requi["requisicoes"] += 1

				break
			except:
				requi["erros"] += 1

		for x in page_detalhes_curso.find_all("tr", {"class": "avalLinhaCampos"}):
			td = x.find_all("td")
			for i in range(len(td)):
				if "Data de início de funcionamento:" in td[i].text:
					data_inicio = td[i+1].text.strip()
				elif "Carga horária mínima:" in td[i].text:
					carga_horaria = td[i+1].text.strip()
				elif "Situação de Funcionamento:" in td[i].text:
					situacao_curso = td[i+1].text.strip()
				elif "Periodicidade (Integralização):" in td[i].text:
					periodicidade = td[i+1].text.strip()
				elif "Vagas Anuais Autorizadas:" in td[i].text:
					vagas_anuais = td[i+1].text.strip()
		#####


		# HISTORICO INDICES CURSO
		link2 = "http://emec.mec.gov.br/emec/consulta-curso/listar-historico-indicadores-curso/c1999930082674af6577f0c513f05a96/"+cod_curso64+"/list/5000"

		while True:
			try:
				r = s.get(link2)
				page_hist_indice = BeautifulSoup(r.content, 'html.parser')

				if r.status_code != 200:
					requi["erros"] += 1
					time.sleep(30)
					continue

				requi["requisicoes"] += 1

				break
			except:
				requi["erros"] += 1


		for tr in page_hist_indice.find_all("tr")[1::]:
			hist = [x.text.strip() for x in tr.find_all("td")]

			if hist[0] != "Nenhum registro encontrado!":
				indice_historico_curso.append({
					'ano': hist[0],
					'enade': hist[1],
					'cpc': hist[2],
					'cc': hist[3],
					'idd': hist[4]
				})
		####


		# ASSOCIA CURSO A UNIDADE

		link2 = "http://emec.mec.gov.br/emec/consulta-curso/listar-endereco-curso/d96957f455f6405d14c6542552b0f6eb/0/c1999930082674af6577f0c513f05a96/"+cod_curso64+"/list/5000"
		
		while True:
			try:
				r = s.get(link2)
				page_end_unidades = BeautifulSoup(r.content, 'html.parser')

				if r.status_code != 200:
					requi["erros"] += 1
					time.sleep(30)
					continue

				requi["requisicoes"] += 1

				break
			except:
				requi["erros"] += 1

		for tbody in page_end_unidades.find_all("tbody"):
			td = [x.text.strip() for x in tbody.find_all("td")]
			if td[0] == "Nenhum registro encontrado.":
				break

			endereco = td[1]

			if len(td) == 5:
				curso = {
					'codigo': codigo_curso,
					'numero_vagas': vagas_anuais
				}
			else:
				curso = {
					'codigo': codigo_curso,
					'numero_vagas': td[5]
				}

			# Gambiarra pra dar match nos enderços e definir as unidades que oferecem o curso
			achou = False
			try:
				for idx, unidade in enumerate(unidades):
					if td[3].lower() == unidade['municipio'].lower() and td[4].lower() == unidade['uf'].lower() and td[0].lower() == unidade['denominacao'].lower():
						end_curso = [x.lower() for x in endereco.replace("S/N", " ").replace("s/n", " ").replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").translate(remove_digits).split(" ") if len(x) > 0]
						end_unidade = [x.lower() for x in unidade['endereco'].replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").translate(remove_digits).split(" ") if len(x) > 0]
						if end_curso[0].lower().replace("professor", "prof") == end_unidade[0].lower().replace("professor", "prof") and end_curso[1].lower().replace("professor", "prof") == end_unidade[1].lower().replace("professor", "prof"):
							cursos_unidades.append((idx, curso))
							achou = True
			except:
				try:
					for idx, unidade in enumerate(unidades):
						if td[3].lower() == unidade['municipio'].lower() and td[4].lower() == unidade['uf'].lower() and td[0].lower() == unidade['denominacao'].lower():
							end_curso = [x.lower() for x in endereco.replace("S/N", " ").replace("s/n", " ").replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").split(" ") if len(x) > 0]
							end_unidade = [x.lower() for x in unidade['endereco'].replace("/", " ").replace(",", " ").replace(".", " ").replace("-", " ").split(" ") if len(x) > 0]
							if end_curso[0].lower().replace("professor", "prof") == end_unidade[0].lower().replace("professor", "prof") and end_curso[1].lower().replace("professor", "prof") == end_unidade[1].lower().replace("professor", "prof"):
								cursos_unidades.append((idx, curso))
								achou = True
				except:
					for idx, unidade in enumerate(unidades):
						if td[3].lower() == unidade['municipio'].lower() and td[4].lower() == unidade['uf'].lower() and td[0].lower() == unidade['denominacao'].lower():
							cursos_unidades.append((idx, curso))
							achou = True

			# Para rastrear as que não deram match e corrigir
			if achou == False:
				for idx, unidade in enumerate(unidades):
					if td[3].lower() == unidade['municipio'].lower() and td[4].lower() == unidade['uf'].lower() and td[0].lower() == unidade['denominacao'].lower():
						cursos_unidades.append((idx, curso))
						achou = True

			if achou == False:
				mutex.acquire(1)
				mensagem = "Curso: "+nome+"\n"+"Código: "+codigo_curso+"\n""Endereço: "+td[1]+"   "+td[3]+"-"+td[3]+"\n"+"URL: http://emec.mec.gov.br/emec/consulta-cadastro/detalhamento/d96957f455f6405d14c6542552b0f6eb/"+cod64+"\n\n\n"
				arquivo = open('cursos_sem_unidades.txt', 'r')
				conteudo = arquivo.readlines()
				conteudo.append(mensagem)
				arquivo = open('cursos_sem_unidades.txt', 'w')
				arquivo.writelines(conteudo)
				arquivo.close()	
				mutex.release()
		#####

		cursos_ies.append({
			'codigo': td_curso[0],
			'nome': nome,
			'modalidade': td_curso[1],
			'data_inicio': data_inicio,
			'carga_horaria': carga_horaria,
			'situacao': situacao_curso,
			'periodicidade': periodicidade,
			'vagas_anuais': vagas_anuais,
			'grau': td_curso[2],
			'indice_historico': indice_historico_curso
		})

	mutex_cursos.acquire(1)
	qt_cursos["qt"] -= 1

	if qt_cursos["qt"] == 0:
		semaforo_controle.release()
	semaforo_curso.release()
	mutex_cursos.release()

def pegaTudo(TRA, IES, CURSOS, cont, mutex, semaforo, semaforo2, codigo_ies):
	erros = 0
	requisicoes = 0
	remove_digits = str.maketrans('', '', digits)

	field_1 = [x.text.strip() for x in TRA.find_all("td")][:-1]
	cod64 = base64.b64encode(codigo_ies.encode('ascii')).decode('ascii')
	unidades = []
	cursos = []
	unidade = {}
	telefone = ''
	emails = []
	tipos_credenciamento = []
	site = ''
	situacao = "Ativa"

	# Pega Historico de indice da IES
	while True:
		try:
			link2 = "http://emec.mec.gov.br/emec/consulta-ies/listar-historico-indicadores-ies/d96957f455f6405d14c6542552b0f6eb/"+cod64+"/list/5000"
			r = s.get(link2)
			
			if r.status_code != 200:
				erros += 1
				time.sleep(30)
				continue

			page_hist_ies = BeautifulSoup(r.content, 'html.parser')
			requisicoes += 1
			break
		except:
			erros += 1

	indice_historico = []

	for tr in page_hist_ies.find_all("tr")[1::]:
		hist_ies = [x.text.strip() for x in tr.find_all("td")]
		if "Nenhum registro encontrado" in hist_ies[0]:
			break

		indice_historico.append({
			'ano': hist_ies[0],
			'ci': hist_ies[1],
			'igc': hist_ies[2],
			'ci_ead': hist_ies[3]
		})
	#######	

	# PEga infos da IES
	while True:
		try:
			link2 = "http://emec.mec.gov.br/emec/consulta-ies/index/d96957f455f6405d14c6542552b0f6eb/"+cod64
			r = s.get(link2)
			page_ies = BeautifulSoup(r.content, 'html.parser')

			if r.status_code != 200:
				erros += 1
				time.sleep(30)
				continue

			requisicoes += 1
			break
		except:
			erros += 1

	for match in page_ies.findAll('div', {"style": "color:#FE773D"}):
		situacao = match.find("b").text.strip().replace(":", "")

	for x in page_ies.find_all("tr", {"class": "avalLinhaCampos"}):
		td = x.find_all("td")
		for i in range(len(td)):
			if "Telefone:" in td[i].text:
				telefone = td[i+1].text.strip().replace("  ", " ")
			elif "E-mail:" in td[i].text:
				emails = [e.strip() for e in td[i+1].text.split(";")]
			elif "Tipo de Credenciamento:" in td[i].text:
				tipos_credenciamento = [e.strip() for e in td[i+1].text.split("/")]
			elif "Sítio:" in td[i].text:
				site = td[i+1].text.strip()
	#####


	# Pega as unidades
	while True:
		try:
			link2 = "http://emec.mec.gov.br/emec/consulta-ies/listar-endereco/d96957f455f6405d14c6542552b0f6eb/"+cod64+"/list/5000"
			r = s.get(link2)
			page_end = BeautifulSoup(r.content, 'html.parser')
			
			if r.status_code != 200:
				erros += 1
				time.sleep(30)
				continue

			requisicoes += 1
			break
		except:
			erros += 1

	for body in page_end.find_all("tbody"):
		link_unidade = "http://emec.mec.gov.br"+body.find("tr")['onclick'].split("'")[3].strip()+"/list/5000"

		td = [x.text.strip() for x in body.find_all("td")]

		unidade = {
			'codigo': td[0],
			'denominacao': td[1],
			'endereco': td[2],
			'polo': td[3],
			'municipio': td[4],
			'uf': td[5],
			'cursos': []
		}

		unidades.append(unidade)
	#####

	while True:
		try:
			link2 = "http://emec.mec.gov.br/emec/consulta-ies/listar-curso-agrupado/d96957f455f6405d14c6542552b0f6eb/"+cod64+"/list/5000"
			r = s.get(link2)
			page_cursos = BeautifulSoup(r.content, 'html.parser')
			
			if r.status_code != 200:
				erros += 1
				time.sleep(30)
				continue

			requisicoes += 1
			break
		except:
			erros += 1


	if page_cursos.find("tfoot").text.strip() == "Nenhum registro encontrado.":
		nomes_cursos = []
	else:
		nomes_cursos = [x.find("a").text.strip() for x in page_cursos.find("tbody").find_all("tr")]


	total_cursos_ies = []

	cursos_ies = []
	cursos_unidades = []
	requi = []

	qt_cursos = {
		"qt": len(nomes_cursos)
	}

	for monta in range(len(nomes_cursos)):
		cursos_ies.append([])
		cursos_unidades.append([])
		requi.append({
			'requisicoes': 0,
			'erros': 0
		})

	semaforo_curso = BoundedSemaphore(20)
	semaforo_controle = BoundedSemaphore(1)
	mutex_cursos = Lock()

	semaforo_controle.acquire()
	for idx, nome in enumerate(nomes_cursos):
		if "Nenhum registro encontrado" in nome:
			semaforo_controle.release()
			break

		semaforo_curso.acquire()
		Thread(target=getCursoNome, args=(cursos_ies[idx], cursos_unidades[idx], requi[idx], unidades, cod64, semaforo_curso, semaforo_controle, mutex_cursos, qt_cursos, nome)).start()

	if len(nomes_cursos) == 0:
		semaforo_controle.release()

	semaforo_controle.acquire()

	for i in range(len(nomes_cursos)):
		requisicoes += requi[i]['requisicoes']
		erros += requi[i]['erros']

		for it in cursos_unidades[i]:
			unidades[it[0]]['cursos'].append(it[1])

		for it in cursos_ies[i]:
			total_cursos_ies.append(it)


	global num_ies
	global ini
	global erros_total
	global requisicoes_total

	mutex.acquire(1)
	IES.append({
		'codigo': codigo_ies,
		'nome': field_1[0].split(')')[1].strip(),
		'sigla': field_1[1],
		'telefone': telefone,
		'emails': emails,
		'tipos_credenciamento': tipos_credenciamento,
		'site': site,
		'municipio': field_1[2].split('/')[0].strip(),
		'estado': field_1[2].split('/')[1].strip(),
		'organizacao_academica': field_1[3],
		'categoria_administrativa': field_1[4],
		'icg': field_1[5],
		'ci': field_1[6],
		'ci_ead': field_1[7],
		'unidades': unidades,
		'indice_historico': indice_historico,
		'situacao': situacao,
		'url': "http://emec.mec.gov.br/emec/consulta-cadastro/detalhamento/d96957f455f6405d14c6542552b0f6eb/"+cod64
	})

	erros_total += erros
	requisicoes_total += requisicoes

	for x in total_cursos_ies:
		CURSOS.append(x)

	num_ies -= 1
	
	if num_ies%200 == 0 or num_ies <= 50:
		print("\n\nRequisições:", requisicoes_total+erros_total)
		print("Sucesso:", requisicoes_total)
		print("Erros:", erros_total)
		print("Restam:", num_ies)
		print("Tempo:", time.time()-ini)
		if num_ies%200 == 0:
			print("NÃO FECHAR")
			with io.open('IES.json', 'w', encoding='utf-8') as f:
				json.dump(IES, f, ensure_ascii=False)
			with io.open('CURSOS.json', 'w', encoding='utf-8') as f:
				json.dump(CURSOS, f, ensure_ascii=False)
			print("PODE FECHAR\n")

	if num_ies == 0:
		semaforo2.release()

	semaforo.release()

	mutex.release()



# Dados para buscar lista de IES
data = {
	'data[CONSULTA_AVANCADA][hid_template]':'listar-consulta-avancada-ies',
	'data[CONSULTA_AVANCADA][hid_order]':'ies.no_ies ASC',
	'data[CONSULTA_AVANCADA][hid_no_cidade_avancada]':'',
	'data[CONSULTA_AVANCADA][hid_no_regiao_avancada]':'',
	'data[CONSULTA_AVANCADA][hid_no_pais_avancada]':'',
	'data[CONSULTA_AVANCADA][hid_co_pais_avancada]':'',
	'data[CONSULTA_AVANCADA][rad_buscar_por]':'IES',
	'data[CONSULTA_AVANCADA][txt_no_ies]':'',
	'data[CONSULTA_AVANCADA][txt_no_ies_curso]':'',
	'data[CONSULTA_AVANCADA][txt_no_ies_curso_especializacao]':'',
	'data[CONSULTA_AVANCADA][txt_no_curso]':'',
	'data[CONSULTA_AVANCADA][sel_co_area_geral]':'',
	'data[CONSULTA_AVANCADA][sel_co_area_especifica]':'',
	'data[CONSULTA_AVANCADA][sel_co_area_detalhada]':'',
	'data[CONSULTA_AVANCADA][sel_co_area_curso]':'',
	'data[CONSULTA_AVANCADA][txt_no_especializacao]':'',
	'data[CONSULTA_AVANCADA][sel_co_area]':'',
	'data[CONSULTA_AVANCADA][sel_sg_uf]':'',
	'data[CONSULTA_AVANCADA][sel_st_gratuito]':'',
	'data[CONSULTA_AVANCADA][sel_no_indice_ies]':'',
	'data[CONSULTA_AVANCADA][sel_co_indice_ies]':'',
	'data[CONSULTA_AVANCADA][sel_no_indice_curso]':'',
	'data[CONSULTA_AVANCADA][sel_co_indice_curso]':'',
	'data[CONSULTA_AVANCADA][sel_co_situacao_funcionamento_ies]':'10035',
	'data[CONSULTA_AVANCADA][sel_co_situacao_funcionamento_curso]':'9',
	'data[CONSULTA_AVANCADA][sel_st_funcionamento_especializacao]':'',
	'captcha':''
}

s = requests.session()
s.keep_alive = False

ini = time.time()

r = s.post("http://emec.mec.gov.br/emec/nova-index/listar-consulta-avancada/list/5000", data=data)
page_ini = BeautifulSoup(r.content, 'html.parser')

print('Tempo para baixar lista de IES:', time.time()-ini)


for match in page_ini.findAll('span', {"style": "color:#FE773D"}):
	match.extract()


IES = []
CURSOS = []

ja_buscados = {}

mutex = Lock()
semaforo = BoundedSemaphore(15)
semaforo2 = BoundedSemaphore(1)

ini = time.time()
contador = 0
requisicoes_total = 0
erros_total = 0

semaforo2.acquire()


trs_ies = page_ini.find("tbody").find_all("tr")
num_ies = len(trs_ies)

if os.path.isfile("IES.json") and os.path.isfile("CURSOS.json"):
	IES = json.load(codecs.open('IES.json', 'r', 'utf-8'))
	CURSOS = json.load(codecs.open('CURSOS.json', 'r', 'utf-8'))

	for x in IES:
		ja_buscados[x["codigo"]] = True
		num_ies -= 1


if num_ies > 0:
	arquivo = open('cursos_sem_unidades.txt', 'w')
	arquivo.close()

	print("Buscar dados de", num_ies, "IES")

	random.shuffle(trs_ies)
	
	for idx, tr in enumerate(trs_ies):
		codigo_ies = tr.find("td").text.strip().split(')')[0].split('(')[1].strip()
		if codigo_ies not in ja_buscados:
			semaforo.acquire()
			Thread(target=pegaTudo, args=(tr, IES, CURSOS, idx, mutex, semaforo, semaforo2, codigo_ies)).start()

	semaforo2.acquire()

	print("NÃO FECHAR")
	with io.open('IES.json', 'w', encoding='utf-8') as f:
		json.dump(IES, f, ensure_ascii=False)
	with io.open('CURSOS.json', 'w', encoding='utf-8') as f:
		json.dump(CURSOS, f, ensure_ascii=False)
	print("PODE FECHAR\n")

	print("Tempo Total:", time.time()-ini)
	print("Requisições:", requisicoes_total+erros_total)
	print("Sucesso:", requisicoes_total)
	print("Erros:", erros_total)
else:
	print("Todos dados já foram baixados")