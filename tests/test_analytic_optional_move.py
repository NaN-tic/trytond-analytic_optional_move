# This file is part of the analytic_optional_move module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AnalyticOptionalMoveTestCase(ModuleTestCase):
    'Test Analytic Optional Move module'
    module = 'analytic_optional_move'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AnalyticOptionalMoveTestCase))
    return suite