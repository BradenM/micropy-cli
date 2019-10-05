# -*- coding: utf-8 -*-

"""Logging functionality"""

import logging
import re
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler

import click

from micropy import data


class Log:
    """Borg for easy access to any Log from anywhere in the package"""
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.parent_logger = ServiceLog()
        self.loggers = [self.parent_logger]

    @classmethod
    def add_logger(cls, service_name, base_color="white", **kwargs):
        """Creates a new child ServiceLog instance"""
        _self = cls()
        parent = kwargs.pop("parent", _self.parent_logger)
        logger = ServiceLog(service_name, base_color,
                            parent=parent, **kwargs)
        _self.loggers.append(logger)
        return logger

    @classmethod
    def get_logger(cls, service_name):
        """Retrieves a child logger by service name"""
        _self = cls()
        logger = next(
            (i for i in _self.loggers if i.service_name == service_name))
        return logger


class ServiceLog:
    """Handles logging to stdout and micropy.log

    :param service_name: Active service to display
    :type service_name: str
    :param base_color: Color of name on output
    :type base_color: str

    """
    LOG_FILE = data.LOG_FILE

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
        self.show_title = kwargs.get("show_title", True)
        self.stdout = kwargs.get('stdout', True)

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
            self.log_handler = RotatingFileHandler(
                str(self.LOG_FILE), mode='a', maxBytes=2*1024*1024,
                backupCount=2, encoding=None, delay=0)
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
        special = {"fg": color, "bold": True}
        clean = msg
        _parts = re.split(r'\$.*?\[(.*?)\]', msg)
        parts = [(p, None) for p in _parts]
        for w in msg_special:
            if w[0] == 'w':
                special['fg'] = self.warn_color
            if w[0] == 'B':
                special.pop('fg')
            sindex = _parts.index(w[1])
            parts[sindex] = (w[1], special)
            clean = msg.replace(f"${w[0]}[{w[1]}]", w[1])
        clean = clean.encode('ascii', 'ignore').decode('utf-8')
        return (parts, clean)

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
        if not self.show_title:
            return f"{self.parent.get_service(bold=True)}"
        color = kwargs.pop('fg', self.base_color)
        title = click.style(
            f"{self.service_name}", fg=color, **kwargs)
        title = f"{title}{click.style(' ', fg=color)}"
        if self.parent is not None:
            title = f"{self.parent.get_service(bold=True)} {title}"
        return title

    def iter_formatted(self, message, **kwargs):
        """Iterate formatted message tuple into styled string

        Args:
            message (tuple): tuple as (msg, style)
        """
        if isinstance(message, str):
            message, _ = self.parse_msg(message)
        for msg in message:
            text, mstyle = msg
            mstyle = mstyle or kwargs
            yield click.style(text, **mstyle)

    def echo(self, msg, **kwargs):
        """Prints msg to stdout

        :param str msg: message to print
        :param **kwargs:

        """
        title_color = kwargs.pop('title_color', self.base_color)
        title_bold = kwargs.pop('title_bold', True)
        accent_color = kwargs.pop('accent', self.accent_color)
        service_title = self.get_service(fg=title_color, bold=title_bold)
        message, clean = self.parse_msg(msg, accent_color)
        log_attr = kwargs.pop("log", None)
        if log_attr:
            self.load_handler()
            log_func = getattr(logging, log_attr)
            log_func(clean)
        if self.stdout:
            init_msg, init_style = message[0]
            first_part, nl_part, _ = init_msg.partition("\n")
            fp_clean = first_part.encode(
                'ascii', 'ignore').decode('unicode_escape')
            if not fp_clean.strip() and nl_part == "\n":
                init_msg = init_msg.replace("\n", "")
                message[0] = (init_msg, init_style)
                click.secho("")
            click.secho(f"{service_title} ", nl=False)
            post_nl = kwargs.pop('nl', None)
            formatted = list(self.iter_formatted(message, **kwargs))
            for msg in formatted:
                do_nl = (msg == formatted[-1])
                click.echo(msg, nl=do_nl)
            if post_nl:
                click.echo("")

    def info(self, msg, **kwargs):
        """Prints message with info formatting

        :param msg:
        :param **kwargs:
        :return: method to print msg
        :rtype: method

        """
        return self.echo(msg, log="info", **kwargs)

    def title(self, msg, **kwargs):
        """Prints bolded info message

        Args:
            msg (str): Message

        """
        return self.info(f"\n{msg}", bold=True)

    def error(self, msg, exception=None, **kwargs):
        """Prints message with error formatting

        :param msg:
        :param **kwargs:
        :return: method to print msg
        :rtype: method

        """
        self.echo(msg, log="error", title_color='red', title_bold=True,
                  fg='red', accent='red', **kwargs)
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
        return self.echo(message, log="info", fg='green', **kwargs)

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
