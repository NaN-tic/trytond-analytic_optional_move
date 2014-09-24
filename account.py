#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from decimal import Decimal
from sql import Column
from sql.aggregate import Sum
from sql.conditionals import Coalesce

from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = ['Account']
__metaclass__ = PoolMeta


class Account:
    __name__ = 'analytic_account.account'

    @classmethod
    def get_balance(cls, accounts, name):
        res = {}
        pool = Pool()
        Line = pool.get('analytic_account.line')
        MoveLine = pool.get('account.move.line')
        Account = pool.get('account.account')
        Company = pool.get('company.company')
        Currency = pool.get('currency.currency')
        cursor = Transaction().cursor
        table = cls.__table__()
        line = Line.__table__()
        move_line = MoveLine.__table__()
        a_account = Account.__table__()
        company = Company.__table__()

        ids = [a.id for a in accounts]
        childs = cls.search([('parent', 'child_of', ids)])
        all_ids = {}.fromkeys(ids + [c.id for c in childs]).keys()

        id2account = {}
        all_accounts = cls.browse(all_ids)
        for account in all_accounts:
            id2account[account.id] = account

        line_query = Line.query_get(line)
        account_sum = {}
        id2currency = {}

        # Get analytic lines with account move lines
        cursor.execute(*table.join(line, 'LEFT',
                condition=table.id == line.account
                ).join(move_line, 'LEFT',
                condition=move_line.id == line.move_line
                ).join(a_account, 'LEFT',
                condition=a_account.id == move_line.account
                ).join(company, 'LEFT',
                condition=company.id == a_account.company
                ).select(table.id,
                Sum(Coalesce(line.debit, 0) - Coalesce(line.credit, 0)),
                company.currency,
                where=(table.type != 'view')
                & table.id.in_(all_ids)
                & table.active & line_query & (line.move_line != None),
                group_by=(table.id, company.currency)))

        for account_id, sum, currency_id in cursor.fetchall():
            account_sum.setdefault(account_id, Decimal('0.0'))
            if currency_id != id2account[account_id].currency.id:
                currency = None
                if currency_id in id2currency:
                    currency = id2currency[currency_id]
                else:
                    currency = Currency(currency_id)
                    id2currency[currency.id] = currency
                account_sum[account_id] += Currency.compute(currency, sum,
                        id2account[account_id].currency, round=True)
            else:
                account_sum[account_id] += \
                    id2account[account_id].currency.round(sum)

        # Get analytic lines without account move lines
        cursor.execute(*table.join(line, 'LEFT',
                condition=table.id == line.account
                ).join(company, 'LEFT',
                condition=company.id == line.company2
                ).select(table.id,
                Sum(Coalesce(line.debit, 0) - Coalesce(line.credit, 0)),
                company.currency,
                where=(table.type != 'view')
                & table.id.in_(all_ids)
                & table.active & line_query & (line.move_line == None),
                group_by=(table.id, company.currency)))

        for account_id, sum, currency_id in cursor.fetchall():
            account_sum.setdefault(account_id, Decimal('0.0'))
            if currency_id != id2account[account_id].currency.id:
                currency = None
                if currency_id in id2currency:
                    currency = id2currency[currency_id]
                else:
                    currency = Currency(currency_id)
                    id2currency[currency.id] = currency
                account_sum[account_id] += Currency.compute(currency, sum,
                        id2account[account_id].currency, round=True)
            else:
                account_sum[account_id] += \
                    id2account[account_id].currency.round(sum)

        for account_id in ids:
            res.setdefault(account_id, Decimal('0.0'))
            childs = cls.search([
                    ('parent', 'child_of', [account_id]),
                    ])
            to_currency = id2account[account_id].currency
            for child in childs:
                from_currency = id2account[child.id].currency
                res[account_id] += Currency.compute(from_currency,
                        account_sum.get(child.id, Decimal('0.0')), to_currency,
                        round=True)
            res[account_id] = to_currency.round(res[account_id])
            if id2account[account_id].display_balance == 'credit-debit':
                res[account_id] = - res[account_id]
        return res

    @classmethod
    def get_credit_debit(cls, accounts, name):
        res = {}
        pool = Pool()
        Line = pool.get('analytic_account.line')
        MoveLine = pool.get('account.move.line')
        Account = pool.get('account.account')
        Company = pool.get('company.company')
        Currency = pool.get('currency.currency')
        cursor = Transaction().cursor
        table = cls.__table__()
        line = Line.__table__()
        move_line = MoveLine.__table__()
        a_account = Account.__table__()
        company = Company.__table__()

        if name not in ('credit', 'debit'):
            raise Exception('Bad argument')

        id2account = {}
        ids = [a.id for a in accounts]
        for account in accounts:
            res[account.id] = Decimal('0.0')
            id2account[account.id] = account

        line_query = Line.query_get(line)
        id2currency = {}

        # Get analytic lines with account move lines
        cursor.execute(*table.join(line, 'LEFT',
                condition=table.id == line.account
                ).join(move_line, 'LEFT',
                condition=move_line.id == line.move_line
                ).join(a_account, 'LEFT',
                condition=a_account.id == move_line.account
                ).join(company, 'LEFT',
                condition=company.id == a_account.company
                ).select(table.id,
                Sum(Coalesce(Column(line, name), 0)),
                company.currency,
                where=(table.type != 'view')
                & table.id.in_(ids)
                & table.active & line_query & (line.move_line != None),
                group_by=(table.id, company.currency)))

        for account_id, sum, currency_id in cursor.fetchall():
            if currency_id != id2account[account_id].currency.id:
                currency = None
                if currency_id in id2currency:
                    currency = id2currency[currency_id]
                else:
                    currency = Currency(currency_id)
                    id2currency[currency.id] = currency
                res[account_id] += Currency.compute(currency, sum,
                        id2account[account_id].currency, round=True)
            else:
                res[account_id] += id2account[account_id].currency.round(sum)

        # Get analytic lines without account move lines
        cursor.execute(*table.join(line, 'LEFT',
                condition=table.id == line.account
                ).join(company, 'LEFT',
                condition=company.id == line.company2
                ).select(table.id,
                Sum(Coalesce(Column(line, name), 0)),
                company.currency,
                where=(table.type != 'view')
                & table.id.in_(ids)
                & table.active & line_query & (line.move_line == None),
                group_by=(table.id, company.currency)))

        for account_id, sum, currency_id in cursor.fetchall():
            if currency_id != id2account[account_id].currency.id:
                currency = None
                if currency_id in id2currency:
                    currency = id2currency[currency_id]
                else:
                    currency = Currency(currency_id)
                    id2currency[currency.id] = currency
                res[account_id] += Currency.compute(currency, sum,
                        id2account[account_id].currency, round=True)
            else:
                res[account_id] += id2account[account_id].currency.round(sum)

        return res
