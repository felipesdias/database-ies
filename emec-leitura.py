#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import io
import codecs

# Usar uprin para imprimir os dados
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
	enc = file.encoding
	if enc == 'UTF-8':
		print(*objects, sep=sep, end=end, file=file)
	else:
		f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
		print(*map(f, objects), sep=sep, end=end, file=file)


IES = json.load(codecs.open('IES.json', 'r', 'utf-8'))
CURSOS = json.load(codecs.open('CURSOS.json', 'r', 'utf-8'))

