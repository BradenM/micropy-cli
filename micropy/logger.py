#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from click import clear, confirm, prompt, secho, style


class ServiceLog:

    def __init__(self, service_name, base_color, **kwargs):
        self.is_root = kwargs.get('root', False)
        self.parent_name = style(
            f"[MicroPy] \u276f", fg='bright_green', bold=True)
        self.base_color = base_color
        self.service_name = service_name
        self.info_color = kwargs.get('info_color', 'white')
        self.accent_color = kwargs.get('accent_color', 'yellow')
        self.warn_color = kwargs.get('warn_color', 'green')

    def parse_msg(self, msg, accent_color=None):
        msg_special = re.findall(r'\$(.*?)\[(.*?)\]', msg)
        color = accent_color or self.accent_color
        for w in msg_special:
            if w[0] == 'w':
                color = self.warn_color
            msg = msg.replace(f"${w[0]}[{w[1]}]", style(
                w[1], fg=color))
        return msg

    def get_service(self, **kwargs):
        color = kwargs.pop('fg', self.base_color)
        title = style(
            f"[{self.service_name}] \u276f", fg=color, **kwargs)
        return title

    def echo(self, msg, **kwargs):
        title_color = kwargs.pop('title_color', self.base_color)
        title_bold = kwargs.pop('title_bold', False)
        accent_color = kwargs.pop('accent', self.accent_color)
        service_title = self.get_service(fg=title_color, bold=title_bold)
        title = f"{self.parent_name} {service_title if not self.is_root else ''}"
        message = self.parse_msg(msg, accent_color)
        secho(
            f"{title} ", nl=False)
        secho(message, **kwargs)

    def info(self, msg, **kwargs):
        return self.echo(msg, **kwargs)

    def error(self, msg, **kwargs):
        return self.echo(msg, title_color='red', title_bold=True, fg='red', underline=True, accent='red', **kwargs)

    def warn(self, msg, **kwargs):
        return self.echo(msg, title_color='red', title_bold=True)

    def exception(self, error, **kwargs):
        return self.echo(str(error), title_color='red', title_bold=True, **kwargs)

    def success(self, msg, **kwargs):
        message = f"\u2714 {msg}"
        return self.echo(message, fg='green')

    def prompt(self, msg, **kwargs):
        new_line = kwargs.pop('nl', False)
        nl_default = kwargs.get('default', None)
        msg = self.parse_msg(msg)
        msg = msg + \
            style(f"\n Press Enter to Use: [{nl_default}]", dim=True) if nl_default and len(
                nl_default) > 0 else msg
        title = self.get_service()
        suffix = style('\u27a4 ', fg=self.accent_color)
        secho(f"{self.parent_name} {title} ", nl=False)
        return prompt(msg + '\n' if new_line else msg,
                      prompt_suffix=suffix, **kwargs)

    def confirm(self, msg, **kwargs):
        msg = self.parse_msg(msg)
        title = self.get_service()
        suffix = style('\u27a4 ', fg=self.accent_color)
        secho(f"{self.parent_name} {title} ", nl=False)
        return confirm(msg, show_default="[y/N] ", prompt_suffix=suffix, **kwargs)


    def clear(self):
        """Clears terminal screen"""
        return clear()

