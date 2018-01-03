# Extrair dados de IES do [EMEC](http://emec.mec.gov.br/)

Dados de execução (Servidor gCloud southAmerica 8 núcleos):
 * Tempo de execução: 12312 segundos -> 3h e 35 minutos
 * Número de Requisições: 214750


Importante:
 * Python 3
 * Contem todas informações das IES e dos cursos, incluindo históricos de indicadores
 * Tempo de execução +- 4~5 horas, servidor BR da google, 8 cores
 * ans-extrair.py é o script que extrair os dados e salva como JSON
 * ans-leitura.py modelo para leitura do JSON
 * CURSOS.json dados extraído em 03/01/2017
 * IES.json dados extraído em 03/01/2017
 * Foi usado threads, mutex e semáforos para acelerar o processo e garantir integridade dos dados
 * Devido ao tempo elevado de execução é possível fechar a execução do script, na próxima vez ele irá ler o JSON salvo e buscar apenas o restante (nescessário ambos os JSON's estarem na pasta)
 * Recomendado uma boa internet
 * Alguns cursos não têm unidades cadastradas nas IES, esses cursos são salvos em um arquivo separado (cursos_sem_unidades.txt), caso queira trata-los manualmente

Dependencias:
 * pip install beautifulsoup4
 * pip install requests

Informações dos JSON:
* Foi separado em 2 arquivos, IES.json contém informações sobre as instituições, suas unidades juntamente com suas informações e para cada unidade também quais cursos são oferecidos e quantas vagas são permitidas, no arquivo CURSOS.json, contém informações referentes aos cursos. Ambos podem ser relacionados através do ID
* Modelo IES.json:
```json
{
    "codigo": "13796",
    "nome": "FACULDADE DE PORTO FELIZ",
    "sigla": "-",
    "telefone": "11 7542 0965",
    "emails": [],
    "tipos_credenciamento": [
      "Presencial - Superior"
    ],
    "site": "",
    "municipio": "Porto Feliz",
    "estado": "SP",
    "organizacao_academica": "Faculdade",
    "categoria_administrativa": "Privada com fins lucrativos",
    "icg": "3",
    "ci": "3",
    "ci_ead": "-",
    "unidades": [
      {
        "codigo": "1069978",
        "denominacao": "Jatobá",
        "endereco": "AV. Monsenhor Seckler, 1250 - V. América",
        "polo": "-",
        "municipio": "Porto Feliz",
        "uf": "SP",
        "cursos": [
          {
            "codigo": "1073877",
            "numero_vagas": "100"
          },
          {
            "codigo": "1073542",
            "numero_vagas": "100"
          },
          {
            "codigo": "1073879",
            "numero_vagas": "100"
          }
        ]
      },
      {
        "codigo": "1069977",
        "denominacao": "Jatobá - UNIDADE SEDE",
        "endereco": "Av. Monsenhor Seckler,1250, 1250 - V. América",
        "polo": "-",
        "municipio": "Porto Feliz",
        "uf": "SP",
        "cursos": []
      },
      {
        "codigo": "1043442",
        "denominacao": "Unidade SEDE",
        "endereco": "Praça Dr. José Sacramento e Silva, 13 - Centro",
        "polo": "-",
        "municipio": "Porto Feliz",
        "uf": "SP",
        "cursos": [
          {
            "codigo": "1073457",
            "numero_vagas": "150"
          },
          {
            "codigo": "1073875",
            "numero_vagas": "150"
          },
          {
            "codigo": "1072970",
            "numero_vagas": "150"
          }
        ]
      }
    ],
    "indice_historico": [
      [
        "2017",
        "3",
        "-",
        "-"
      ],
      [
        "2016",
        "-",
        "3",
        "-"
      ],
      [
        "2015",
        "-",
        "3",
        "-"
      ],
      [
        "2014",
        "-",
        "3",
        "-"
      ],
      [
        "2010",
        "3",
        "-",
        "-"
      ]
    ],
    "situacao": "Ativa",
    "url": "http://emec.mec.gov.br/emec/consulta-cadastro/detalhamento/d96957f455f6405d14c6542552b0f6eb/MTM3OTY="
  }
```
* Modelo CURSOS.json:
```json
    {
    "codigo": "1073877",
    "nome": "ADMINISTRAÇÃO",
    "modalidade": "1073877",
    "data_inicio": "01/08/2011",
    "carga_horaria": "3200 horas",
    "sitiacao": "Em atividade",
    "periodicidade": "Semestral (8.0)",
    "vagas_anuais": "100",
    "grau": "Bacharelado",
    "indice_historico": [
      {
        "ano": "2016",
        "enade": "-",
        "cpc": "-",
        "cc": "4",
        "idd": "-"
      },
      {
        "ano": "2015",
        "enade": "3",
        "cpc": "-",
        "cc": "-",
        "idd": "-"
      },
      {
        "ano": "2010",
        "enade": "-",
        "cpc": "-",
        "cc": "3",
        "idd": "-"
      }
    ]
  }
```

Autor: Felipe de Souza Dias
E-mail: felipe.s.dias@outlook.com