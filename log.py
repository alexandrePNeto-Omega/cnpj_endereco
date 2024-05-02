#!/usr/bin/python
# vi: fileencoding=utf-8

import os
import logging
from logging import *

class Log():
    def __init__(self, arquivo_log="app.log"):
        self.arquivo_log = arquivo_log
        self.log = self.get_log()

    def get_log(self):
        log = logging
        log_path = os.path.join(os.getcwd(), "log")
        if not os.path.isdir(log_path):
            os.mkdir(log_path)

        log.basicConfig(
            level = INFO,
            format = "%(asctime)s - %(levelname)s	: '%(message)s'",
            filename = str(os.path.join(log_path, self.arquivo_log))
        )

        return log