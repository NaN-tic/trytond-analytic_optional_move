# This file is part of the analytic_optional_move module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .line import *

def register():
    Pool.register(
        Line,
        module='analytic_optional_move', type_='model')
