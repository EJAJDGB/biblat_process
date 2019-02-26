#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import os
import json
import logging

from biblat_schema.catalogs import (
    Pais,
    Idioma,
    TipoDocumento,
    EnfoqueDocumento,
    Disciplina,
    SubDisciplina
)
from mongoengine import connect

from biblat_process.settings import config

logger = logging.getLogger('claper_dump')

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
LOGGER_FMT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

connect(db=config.MONGODB_NAME, host=config.MONGODB_HOST)


class PopulateCatalog:
    def __init__(self):
        self.data_dir = os.path.join(SCRIPT_PATH, '../datos')
        self.files = {
            'Pais': 'Pais.json',
            'Idioma': 'Idioma.json',
            'TipoDocumento': 'TipoDocumento.json',
            'EnfoqueDocumento': 'EnfoqueDocumento.json',
            'Disciplina': 'Disciplina.json',
            'SubDisciplina': 'SubDisciplina.json',
            'NombreGeografico': 'NombreGeografico.tsv',
            'LicenciaCC': 'LicenciaCC.json',
            'SherpaRomeo': 'SherpaRomeo.json'
        }

    def pais(self):
        with open(os.path.join(self.data_dir, self.files['Pais']),
                  encoding="utf-8") as jsonf:
            paises = json.load(jsonf)
            for pais_data in paises:
                try:
                    pais = Pais(**pais_data)
                    pais.save()
                except Exception as e:
                    logging.error('Error al procesar %s' % str(pais_data))
                    logging.error('%s' % str(e))

    def idioma(self):
        with open(os.path.join(self.data_dir, self.files['Idioma']),
                  encoding="utf-8") as jsonf:
            idiomas = json.load(jsonf)
            for idioma_data in idiomas:
                try:
                    idioma = Idioma(**idioma_data)
                    idioma.save()
                except Exception as e:
                    logging.error('Error al procesar %s' % str(idioma_data))
                    logging.error('%s' % str(e))

    def tipo_documento(self):
        with open(os.path.join(self.data_dir, self.files['TipoDocumento']),
                  encoding="utf-8") as jsonf:
            tipos_documento = json.load(jsonf)
            for tipo_documento_data in tipos_documento:
                try:
                    tipo_documento = TipoDocumento.objects(
                        nombre__es=tipo_documento_data['nombre']['es']
                    ).first()
                    if tipo_documento:
                        tipo_documento_data['_id'] = tipo_documento.id
                    tipo_documento = TipoDocumento(**tipo_documento_data)
                    tipo_documento.save()
                except Exception as e:
                    logging.error('Error al procesar %s' % str(tipo_documento_data))
                    logging.error('%s' % str(e))

    def enfoque_documento(self):
        with open(os.path.join(self.data_dir, self.files['EnfoqueDocumento']),
                  encoding="utf-8") as jsonf:
            enfoques_documento = json.load(jsonf)
            for enfoque_tipo_documento_data in enfoques_documento:
                try:
                    enfoque_documento = EnfoqueDocumento.objects(
                        nombre__es=enfoque_tipo_documento_data['nombre']['es']
                    ).first()
                    if enfoque_documento:
                        enfoque_tipo_documento_data['_id'] = tipo_documento.id
                    enfoque_documento = EnfoqueDocumento(**enfoque_tipo_documento_data)
                    enfoque_documento.save()
                except Exception as e:
                    logging.error('Error al procesar %s' % str(enfoque_tipo_documento_data))
                    logging.error('%s' % str(e))

    def disciplina(self):
        with open(os.path.join(self.data_dir, self.files['Disciplina']),
                  encoding="utf-8") as jsonf:
            disciplinas = json.load(jsonf)
            for disciplina_data in disciplinas:
                try:
                    disciplina = Disciplina.objects(
                        nombre__es=disciplina_data['nombre']['es']
                    ).first()
                    if disciplina:
                        disciplina_data['_id'] = disciplina.id
                    disciplina = Disciplina(**disciplina_data)
                    disciplina.save()
                except Exception as e:
                    logging.error('Error al procesar %s' % str(disciplina_data))
                    logging.error('%s' % str(e))

    def subdisciplina(self):
        with open(os.path.join(self.data_dir, self.files['SubDisciplina']),
                  encoding="utf-8") as jsonf:
            subdisciplinas = json.load(jsonf)
            for subdisciplina_data in subdisciplinas:
                try:
                    subdisciplina = SubDisciplina.objects(
                        nombre__es=subdisciplina_data['nombre']['es']
                    ).first()
                    if subdisciplina:
                        subdisciplina_data['_id'] = subdisciplina.id

                    disciplina = Disciplina.objects(
                        nombre__es=subdisciplina_data['disciplina']
                    ).first()
                    subdisciplina_data['disciplina'] = disciplina
                    subdisciplina = SubDisciplina(**subdisciplina_data)
                    subdisciplina.save()
                except Exception as e:
                    logging.error('Error al procesar %s' % str(subdisciplina_data))
                    logging.error('%s' % str(e))


def main():
    parser = argparse.ArgumentParser(
        description="Llenado de catálogos de biblat_schema"
    )

    parser.add_argument(
        '--logging_level',
        '-l',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level'
    )

    parser.add_argument(
        '--catalog',
        '-c',
        default='all',
        choices=['pais',
                 'idioma',
                 'tipo_documento',
                 'enfoque_documento',
                 'disciplina',
                 'subdisciplina',
                 'all'],
        help='Seleccione proceso a ejecutar'
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.logging_level.upper(), 'INFO'),
        format=LOGGER_FMT)

    populate_catalog = PopulateCatalog()

    if args.catalog in ('pais', 'all'):
        populate_catalog.pais()

    if args.catalog in ('idioma', 'all'):
        populate_catalog.idioma()

    if args.catalog in ('tipo_documento', 'all'):
        populate_catalog.tipo_documento()

    if args.catalog in ('enfoque_documento', 'all'):
        populate_catalog.enfoque_documento()

    if args.catalog in ('disciplina', 'all'):
        populate_catalog.disciplina()

    if args.catalog in ('subdisciplina', 'all'):
        if not Disciplina.objects.count():
            populate_catalog.disciplina()
        populate_catalog.subdisciplina()


if __name__ == "__main__":
    main()
