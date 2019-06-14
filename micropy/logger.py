# -*- coding: utf-8 -*-

"""Logging functionality"""

import logging
import re
from contextlib import contextmanager
from pathlib import Path

from click import clear, confirm, prompt, secho, style


class Log:
    """Borg for easy access to any Log from anywhere in the package"""
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.parent_logger = ServiceLog()
        self.loggers = [self.parent_logger]

    def add_logger(self, service_name, base_color="white", **kwargs):
        """Creates a new child ServiceLog instance"""
        parent = kwargs.get("parent", self.parent_logger)
        logger = ServiceLog(service_name, base_color,
                            parent=parent)
        self.loggers.append(logger)
        return logger

    def get_logger(self, service_name):
        """Retrieves a child logger by service name"""
        logger = next(
            (i for i in self.loggers if i.service_name == service_name))
        return logger


class ServiceLog:
    """Handles logging to stdout and micropy.log

    :param service_name: Active service to display
    :type service_name: str
    :param base_color: Color of name on output
    :type base_color: str

    """
    LOG_FILE = Path.home() / '.micropy' / 'micropy.log'

    def __init__(
            self, service_name='MicroPy', base_color='bright_green', **kwargs):
        self.parent = kwargs.get('parent', None)
        self.LOG_FILE.parent.mkdir(exist_ok=True)
        self.base_color = base_color
        self.service_name = service_name
        self.load_handler()
        self.info_color = kwargs.get('info_color', 'white')
        self.accent_color = kwargs.get('accent_color', 'yellow')
        self.warn_color = kwargs.get('warn_color', 'green')
        self.stdout = True

    @contextmanager
    def silent(self):
        self.stdout = False
        yield self
        self.stdout = True

    def load_handler(self):
        """Loads Logging Module Formatting"""
        self.log = logging.getLogger()
        if not self.log.hasHandlers():
            self.log.setLevel(logging.DEBUG)
            self.log_handler = logging.FileHandler(
                str(self.LOG_FILE), mode='a')
            self.log_handler.setLevel(logging.DEBUG)
            self.log.addHandler(self.log_handler)
        self.log_handler = self.log.handlers[0]
        parents = self.get_parents()
        log_head = f"%(levelname)s|{parents[0]}"
        if self.parent:
            log_head = f"{log_head}|{'|'.join(parents[1:])}"
        log_form = f"[{log_head}] %(message)s"
        self.log_handler.setFormatter(logging.Formatter(log_form))

    def parse_msg(self, msg, accent_color=None):
        """Parses any color codes accordingly.

        :param str msg:
        :param str accent_color:  (Default value = None)
        :return: Parsed Message
        :rtype: str

        """
        msg_special = re.findall(r'\$(.*?)\[(.*?)\]', msg)
        color = accent_color or self.accent_color
        clean = msg
        for w in msg_special:
            if w[0] == 'w':
                color = self.warn_color
            msg = msg.replace(f"${w[0]}[{w[1]}]", style(
                w[1], fg=color))
            clean = msg.replace(f"${w[0]}[{w[1]}]", w[1])
        clean = clean.encode('ascii', 'ignore').decode('unicode_escape')
        return (msg, clean)

    def get_parents(self, names=[]):
        """Retrieve all parents"""
        if len(names) == 0:
            names = [self.service_name]
        if self.parent:
            names.insert(0, self.parent.service_name)
            names = self.parent.get_parents(names)
        return names

    def get_service(self, **kwargs):
        """Retrieves formatted service title

        :param **kwargs:
        :return: formatted title
        :rtype: str

        """
        color = kwargs.pop('fg', self.base_color)
        title = style(
            f"[{self.service_name}] \u276f", fg=color, **kwargs)
        if self.parent is not None:
            title = f"{self.parent.get_service(bold=True)} {title}"
        return title

    def echo(self, msg, **kwargs):
        """Prints msg to stdout

        :param str msg: message to print
        :param **kwargs:

        """
        title_color = kwargs.pop('title_color', self.base_color)
        title_bold = kwargs.pop('title_bold', self.parent is None)
        accent_color = kwargs.pop('accent', self.accent_color)
        service_title = self.get_service(fg=title_color, bold=title_bold)
        message, clean = self.parse_msg(msg, accent_color)
        log_attr = kwargs.pop("log", None)
        if log_attr:
            self.load_handler()
            log_func = getattr(logging, log_attr)
            log_func(clean)
        if self.stdout:
            secho(f"{service_title} ", nl=False)
            secho(message, **kwargs)

    def info(self, msg, **kwargs):
        """Prints message with info formatting

        :param msg:
        :param **kwargs:
        :return: method to print msg
        :rtype: method

        """
        return self.echo(msg, log="info", **kwargs)

    def error(self, msg, exception=None, **kwargs):
        """Prints message with error formatting

        :param msg:
        :param **kwargs:
        :return: method to print msg
        :rtype: method

        """
        self.echo(msg, log="error", title_color='red', title_bold=True,
                  fg='red', underline=True, accent='red', **kwargs)
        if exception:
            return self.exception(exception)

    def warn(self, msg, **kwargs):
        """Prints message with warn formatting

        :param msg:
        :param **kwargs:
        :return: method to print msg
        :rtype: method

        """
        return self.echo(msg, log="warning",
                         title_color='red', title_bold=True)

    def exception(self, error, **kwargs):
        """Prints message with exception formatting

        :param error:
        :param **kwargs:
        :return: method to print msg
        :rtype: method

        """
        return self.echo(
            str(error),
            log="exception",
            title_color='red', title_bold=True, **kwargs)

    def success(self, msg, **kwargs):
        """Prints message with success formatting

        :param msg:
        :param **kwargs:
        :return: method to print msg
        :rtype: method
        :return: method to print msg
        :rtype: method

        """
        message = f"\u2714 {msg}"
        return self.echo(message, log="info", fg='green')

    def debug(self, msg, **kwargs):
        """Prints message with debug formatting

        :param msg:
        :param **kwargs:
        :return: method to log msg
        :rtype: method

        """
        if self.stdout:
            with self.silent():
                return self.debug(msg, **kwargs)
        self.echo(msg, log="debug")
        return msg

    def prompt(self, msg, **kwargs):
        """Prompts user with question.

        :param msg:
        :param **kwargs:
        :return: prompt
        :rtype: method

        """
        new_line = kwargs.pop('nl', False)
        nl_default = kwargs.get('default', None)
        msg = self.parse_msg(msg)
        msg = msg + style(f"\n Press Enter to Use: [{nl_default}]", dim=True)\
            if nl_default and len(nl_default) > 0 else msg
        title = self.get_service()
        suffix = style('\u27a4 ', fg=self.accent_color)
        secho(f"{title} ", nl=False)
        return prompt(msg + '\n' if new_line else msg,
                      prompt_suffix=suffix, **kwargs)

    def confirm(self, msg, **kwargs):
        """Prompts confirmation from user.

        :param msg:
        :param **kwargs:
        :return: click confirm
        :rtype: method

        """
        msg = self.parse_msg(msg)
        title = self.get_service()
        suffix = style('\u27a4 ', fg=self.accent_color)
        secho(f"{title} ", nl=False)
        return confirm(
            msg, show_default="[y/N] ", prompt_suffix=suffix, **kwargs)

    def clear(self):
        """Clears terminal screen"""
        return clear()
