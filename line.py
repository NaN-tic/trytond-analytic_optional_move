# This file is part of the analytic_optional_move module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond import backend
from trytond.pool import PoolMeta
from trytond.transaction import Transaction

__all__ = ['Line']
__metaclass__ = PoolMeta


class Line:
    __name__ = 'analytic_account.line'

    @classmethod
    def __setup__(cls):
        cls.move_line.required = False
        super(Line, cls).__setup__()

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().cursor
        table = TableHandler(cursor, cls, module_name)

        super(Line, cls).__register__(module_name)

        table._field2module['move_line'] = 'analytic_optional_move'
        table.not_null_action('move_line', action='remove')
