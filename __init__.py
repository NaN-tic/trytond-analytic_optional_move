# This file is part of the analytic_optional_move module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .account import *
from .line import *

def register():
    Pool.register(
        Account,
        Line,
        module='analytic_optional_move', type_='model')
