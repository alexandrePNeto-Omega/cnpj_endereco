# !/usr/bin/python
# vi: fileencoding=latin1
# coding: latin1

import os
import sys
import json
import copy
import requests
import datetime
from time import sleep

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from log import Log
from window import WindowFile

# 1. Valida se tem CNPJ repetido;
# 2. Validar o tempo nencessário para a consulta e limitaçãoo da api pública.

# Uso -> https://publica.cnpj.ws/cnpj/cnpj_da_empresa
API_LINK = "https://publica.cnpj.ws/cnpj/"

class Main():
    def __init__(self):
        self.log = Log().log
        self.user_email = ""

    def run(self):
        file_name = ""
        W = WindowFile()
        while True:
            W.show()
            if self.valida_tipagem_arquivo(W.file_name):
                break

        self.user_email = W.email_usuario or "suporte9@omegaautomacao.com"
        cnpj_list = self.monta_lista_by_arquivo_list(W.file_name)

        # Backup da lista resgatada de cnpj
        cnpj_path = os.path.join(os.getcwd(), "cnpj")
        if not os.path.isdir(cnpj_path):
            os.mkdir(cnpj_path)

        arquivo_backup = open(os.path.join(cnpj_path, "cnpj.csv"), "wb")
        arquivo_backup.writelines("CNPJ,NOME,PAIS,ESTADO,CIDADE,RUA,NUMERO\r\n".encode(encoding="utf-8"))

        # Envio do email
        destinatarios = [self.user_email]
        conteudo = ""\
            "Olá, dado o inicio da geração do arquivo cnpj.\n"\
            "Tempo de espera estimado pela de entrega....: %s\n"\
            "Seu arquivo de backup para caso ocorra algum imprevisto: %s"\
            "" % (str(datetime.timedelta(seconds=(24*len(cnpj_list)))), str(os.path.join(cnpj_path, "cnpj.csv")))
        self.evnia_email(titulo="Inicio da Consulta CNPJ's", conteudo=conteudo, destinatarios=destinatarios)

        # Geração do arquivo
        cnpj_info_retono_list = []
        self.log.info("Iniciando Validação e busca dos cnpj's")
        self.log.info("Tempo de espera estimado em....: %s" % str(datetime.timedelta(seconds=(24*len(cnpj_list)))))
        try:
            self.log.info("|_____ INÍCIO DAS CONSULTAS _____|")
            for cnpj in cnpj_list:
                cnpj_dict = self.consulta_api(cnpj)
                if cnpj_dict:
                    cnpj_info_retono_list.append(cnpj_dict) 
                    arquivo_backup.writelines("%s\r\n" % ",".join([
                        self.formata_cnpj(cnpj_dict.get("cnpj_empresa")) or "N/t",
                        cnpj_dict.get("nome_empresa") or "N/t",
                        cnpj_dict.get("pais") or "N/t",
                        cnpj_dict.get("estado") or "N/t",
                        cnpj_dict.get("cidade") or "N/t",
                        cnpj_dict.get("logradouro") or "N/t",
                        cnpj_dict.get("numero") or "N/t"
                    ]).encode(encoding="utf-8"))
                sleep(21)
                break
            arquivo_backup.close()

            conteudo = ""\
                "Olá, seu arquivo sobre a consulta dos cnpj's informados já está pronto! \n>"\
                "Consulta localmente em sua máquina o seguinte endereço: %s \n"\
                "Ou confira o mesmo em anexo.\n>" % str(os.path.join(cnpj_path, "cnpj.csv"))

            self.evnia_email(conteudo, destinatarios, titulo="Finalização Endereços", file_path=os.path.join(cnpj_path, "cnpj.csv"))

        except Exception as e:
            conteudo = ""\
                "Olá, aparentemente ocorreu algum problema com a consulta de seus cnpj's!\n"\
                "Confira o seu backup de arquivo localmente em: %s \n"  % str(os.path.join(cnpj_path, "cnpj.csv"))
            self.evnia_email(conteudo, destinatarios)
            self.log.error("Ocorreu um erro na realização das consultas.")
            self.log.error(str(e))

        finally:
            self.log.info("|_____ FIM DAS CONSULTAS ______|")

    def formata_cnpj(self, cnpj):
        '''
         - Objetivo..: Formatar o cnpj
         - Parâmetro.: cnpj -> string com o cnpj
         - Retorno...: String
        '''
        try:
            new_cnpj = str(cnpj)
            return "%s.%s.%s/%s-%s" % (new_cnpj[:2],new_cnpj[2:5],new_cnpj[5:8],new_cnpj[8:12],new_cnpj[12:])

        except Exception as e:
            self.log.error(str(e))
            return cnpj

    def consulta_api(self, empresa_cnpj):
        '''
        - Objetivo..: Consulta a empresa na api
        - Parâmetro.: empresa_cnpj -> inteiro com o cnpj da empresa.
        - Retorno...: Dict
        '''
        try:
            self.log.info("+ ------------------------------")
            self.log.info("+ Método.: GET")
            self.log.info("+ Path...: %s" % API_LINK + str(empresa_cnpj))

            empresa_response = requests.get(API_LINK + str(empresa_cnpj))

            self.log.info("+ Result.: %s" % str(empresa_response.status_code))
            if empresa_response.status_code not in range(200, 300):
                return {}

            empresa_response.encoding = "utf-8"
            empresa_response_dict = json.loads(empresa_response.text) or {}
            return {
                "nome_empresa": empresa_response_dict.get("razao_social") or "",
                "cnpj_empresa": empresa_response_dict.get("estabelecimento").get("cnpj") or "",
                "pais":         empresa_response_dict.get("estabelecimento").get("pais").get("nome") or "",
                "estado":       empresa_response_dict.get("estabelecimento").get("estado").get("nome") or "",
                "cidade":       empresa_response_dict.get("estabelecimento").get("cidade").get("nome") or "",
                "logradouro":   empresa_response_dict.get("estabelecimento").get("logradouro") or "",
                "numero":       empresa_response_dict.get("estabelecimento").get("numero") or -1
            }

        except Exception as e:
            return {}

        finally:
            self.log.info("+ ------------------------------")

    def valida_tipagem_arquivo(self, arquivo_path):
        self.log.info("Validando tipo do arquivo")
        arquivo_valido = False
        for tipo in [".xls", ".csv"]:
            if tipo not in arquivo_path:
                continue
            arquivo_valido = True
        return arquivo_valido

    def monta_lista_by_arquivo_list(self, arquivo_path=""):
        self.log.info("Organizando a lista de cnpjs's retornados")
        cnpj_list = []
        try:
            cnpj_list = [str(linha).replace("\r", "").replace("\n", "").replace(".", "").replace("/", "").replace("-", "") for linha in open(arquivo_path, "rb").readlines()]
            for cnpj in copy.copy(cnpj_list):
                if cnpj_list.count(cnpj) <= 1:
                    continue
                cnpj_list.remove(cnpj)

        except Exception as e:
            self.log.error(str(e))
            sys.exit()
        return cnpj_list or []

    def evnia_email(self, titulo="", conteudo="", destinatarios=[], file_path=""):
        '''
         - Objetivo..: Enviar o email para o usuário
         - Parâmetro.: 
         - Retorno...: Boolean
        '''
        try:
            self.log.info("Enviado email para...: %s." % ", ".join(destinatarios))
            # Configurações do servidor SMTP
            smtp_server = 'smtp-mail.outlook.com'
            smtp_port = 587
            sender_email = 'smtpdetesteomega@outlook.com'
            sender_password = '$_0()#!@SenhaMuit0Gr@d3!_'

            mail_message = "Subject: Omega - %s\n\n%s" % (titulo or "CNPJ e Endereço", conteudo)

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(from_addr=sender_email, to_addrs=destinatarios, msg=mail_message)

            self.log.info("Status do envio......: Sucesso.")

        except Exception as e:
            self.log.error(str(e))
            self.log.info("Status do envio......: Erro.")

if __name__ == '__main__':
    Main().run()