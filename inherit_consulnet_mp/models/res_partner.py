# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
import requests
from odoo.exceptions import UserError


import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import csv, operator

#token_local = "62276c75-66ef-48dc-8984-26f93ab4b3de-f15f8d58-7972-4945-9b43-e06a16009390" #Usar en maquina Desarrollo
#token_local =  "0e16a951-fc8d-42c1-8531-c659759ebb97-f47e90f3-15fe-4730-a4d2-9c9373db0470"#Usar en SERVER prueba
#token_local =  #Usar en SERVER Produccion

#------------
import logging
_logger = logging.getLogger(__name__)
#--------------------------


    
class res_partner(models.Model):
    _inherit = 'res.partner'
    
    
    def find_between_r(self, s, first, last):
        try:
            start = s.rindex(first) + len(first)
            end = s.rindex(last, start)
            return s[start:end]
        except ValueError:
            return ""

    
    @api.depends('vat')
    @api.onchange('vat')
    def onchange_name_company(self):
        print("IMPORTANTE DOCUMENT NUMBER")
        if self.vat:
            vat = self.vat
            rut = vat.replace(".","")
            try:
                if rut[:1] == "0":
                    rut = rut[1:]
                url = "http://api.konos.cl:8000/sii/index.php?id=%s" % rut
                response = requests.get(url, params="nombre")
            except Exception:
                response = False

            if response and response.status_code != 200:
                _logger.warning("error %s" % (response))
                vals = {"detail": "Not found."}  
            else:
                vals = response.text
                _logger.warning("paso %s - Tamaño: %s " % (vals, len(vals)))
                if len(vals) > 40:
                    # En caso de encontrar registro en la API
                    # separo las funcionalidades.
                    # 1. Grabo la info obtenida en variables

                    csx_nombre = self.find_between_r(
                        vals, "[nombre] => ", "[resolucion]"
                    ).rstrip()
                    csx_correoDTE = self.find_between_r(
                        vals, "[correo_dte] => ", "[url]"
                    ).rstrip()
                    city = self.find_between_r(
                        vals, "[cuidad] => ", "[comuna]"
                    ).rstrip()
                    csx_web = self.find_between_r(vals, "[url] => ",
                                                  "[fcreado]")
                    csx_pais_id = self.env["res.country"].search(
                        [("code", "=", "CL")], limit=1
                    )
                    csx_dir = (
                        self.find_between_r(vals, "[calle] => ",
                                            "[numero]").rstrip()
                        + " "
                        + self.find_between_r(vals, "[numero] => ",
                                              "[bloque]").rstrip()
                    )
                    csx_dir2 = (
                        self.find_between_r(vals, "[bloque] => ",
                                            "[depto]").rstrip()
                        + " "
                        + self.find_between_r(vals, "[depto] => ",
                                              "[villa]").rstrip()
                    )
                    # 2. Para homologar la comuna, se creo una funcion que
                    # encapsule las validaciones
                    busca_comuna = self._verificar_comuna(vals)
                    self.l10n_cl_activity_description = self.find_between_r(vals, "[giro] => ",
                                            "[acteco]").rstrip()
                    
                        
                    if len(csx_nombre) > 0:
                        # En algunos casos el nombre viene en blanco
                        # No pude reproducir cuando el nombre viene en blanco
                        # pero con esta opción no se debe tener problemas
                        self.name = csx_nombre
                    if len(csx_correoDTE) > 0:
                        self.l10n_cl_dte_email = csx_correoDTE
                    if len(csx_web) > 0:
                        self.website = csx_web
                    self.country_id = csx_pais_id
                    if len(city) > 0:
                        self.city = city
                    # En la data solo hay empresas jurídicas. De todas maneras
                    # por defecto usaremos empresas ya que es lo común
                    self.company_type = "company"
                    # Va contra len > 1 porque aunque no se encuentra
                    # direccion, en la concatenación de las variables,
                    # se agrega un espació en blanco
                    if len(csx_dir) > 1:
                        self.street = csx_dir
                    if len(csx_dir2) > 1:
                        self.street2 = csx_dir2
                    if busca_comuna:
                        self.city_id = busca_comuna.id
                        
                # else:
                #     print("No es empresa")
                                
                #     try:
                #             with open('/home/server1/carpeta_sii_csv/ce_empresas_dwnld_20190806.csv', encoding = "ISO-8859-1") as csvarchivo:

                #     #        with open('/home/consulnet/Descargas/ce_empresas_dwnld_20190806.csv', encoding = "ISO-8859-1") as csvarchivo:
                #                     entrada = csv.reader(csvarchivo, delimiter=';')
                #                     numero_rut = str(self.vat).replace(".", "")
                #                     if numero_rut[0] == "0":
                #                         print("ES 0 el primer numero: ", numero_rut)
                #                         numero_rut = numero_rut[1:]
                #                     print("Numero RUT: ", numero_rut)
                #                     for linea in entrada:
                                        
                #                         if numero_rut == linea[0]:
                #                             self.dte_email = linea[4]
                #                             print(linea)  # Cada línea se muestra como una lista de campos
                                    
                #     except:
                            
                #             with open('/home/consulnet/Descargas/ce_empresas_dwnld_20190806.csv', encoding = "ISO-8859-1") as csvarchivo:

                #     #        with open('/home/consulnet/Descargas/ce_empresas_dwnld_20190806.csv', encoding = "ISO-8859-1") as csvarchivo:
                #                     entrada = csv.reader(csvarchivo, delimiter=';')
                #                     numero_rut = str(self.vat).replace(".", "")
                #                     if numero_rut[0] == "0":
                #                         print("ES 0 el primer numero: ", numero_rut)
                #                         numero_rut = numero_rut[1:]
                #                     print("Numero RUT Home: ", numero_rut)
                #                     for linea in entrada:
                                        
                #                         if numero_rut == linea[0]:
                #                             self.dte_email = linea[4]
                #                             print(linea)  # Cada línea se muestra como una lista de campos


        print("Terminado ")

    # Para apoyar el codigo de busqueda de la comuna con respecto a la API_RUT
    def _verificar_comuna(self, registro):
        comuna = (
            self.find_between_r(registro, "[comuna] => ",
                                "[region]").rstrip().lstrip()
        )

        if comuna == "NUNOA":
            comuna = "Ñuñoa"
        elif comuna == "CAMINA":
            comuna = "Camiña"
        elif comuna == "PENALOLEN":
            comuna = "Peñalolén"
        elif comuna == "PENAFLOR":
            comuna = "Peñaflor"
        elif comuna == "VIVUNA":
            comuna = "Vicuña"
        elif comuna == "VINA DEL MAR":
            comuna = "Viña del Mar"
        elif comuna == "DONIHUE":
            comuna = "Doñihue"
        elif comuna == "HUALANE":
            comuna = "Hualañé"
        elif comuna == "CANETE":
            comuna = "Cañete"
        elif comuna == "NIQUEN":
            comuna = "Ñiquén"
        elif comuna == "RIO IBANEZ":
            comuna = "Río Ibáñez"
        elif comuna == "CONCEPCION":
            comuna = "Concepción"
        elif comuna == "CONCHALI":
            comuna = "Conchalí"
        elif comuna == "PUERTO NATALES":
            comuna = "Natales"

        busca_comuna = self.env["res.city"].search(
            [("name", "=", comuna.title())], limit=1
        )
        _logger.warning(
            "Comuna a ser buscada: (%s) - Se encontro: %s"
            % (comuna.title(), busca_comuna)
        )

        return busca_comuna


