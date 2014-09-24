# This file is part of the analytic_optional_move module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond import backend
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.pyson import Eval, If, Bool

__all__ = ['Line']
__metaclass__ = PoolMeta


class Line:
    __name__ = 'analytic_account.line'

    @classmethod
    def __setup__(cls):
        super(Line, cls).__setup__()
        cls.move_line.required = False

        # Allow analytic accounts with company obtained from context
        domain = []
        for cond in cls.account.domain:
            if cond[0] == 'OR':
                cond.append(('company', '=',
                    Eval('context', {}).get('company', 0)))
            domain.append(cond)
        cls.account.domain = domain

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().cursor
        table = TableHandler(cursor, cls, module_name)

        super(Line, cls).__register__(module_name)

        table._field2module['move_line'] = 'analytic_optional_move'
        table.not_null_action('move_line', action='remove')

    company2 = fields.Many2One('company.company', 'Company',
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ],
        states={
            'invisible': Bool(Eval('move_line')),
            'required': Bool(~Eval('move_line')),
            },
        depends=['move_line'])

    @staticmethod
    def default_company2():
        return Transaction().context.get('company') or None

    def on_change_with_currency(self, name=None):
        if self.move_line:
            return super(Line, self).on_change_with_currency(name)
        elif self.company2:
            return self.company2.currency.id

    def on_change_with_company(self, name=None):
        if self.move_line:
            return super(Line, self).on_change_with_company(name)
        elif self.company2:
            return self.company2.id
