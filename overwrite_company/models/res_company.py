# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path

from random import randrange
from PIL import Image

_logger = logging.getLogger(__name__)

class Company(models.Model):
    _name = "res.company"
    _inherit = "res.company"

    empresa_copy_ldm = fields.Many2one('res.company', string='Compañía copia LdM', index=True)
    copy_ldm = fields.Many2many(string="Listas de materiales asociadas a Compañía copia LdM",
                    comodel_name='mrp.bom',
                    relation="bom_company_copy",
                    help="Selección de Listas de materiales asociadas a Compañía copia LdM.",
                    #domain="[('product_tmpl_id','=',sede_seleccionada)]",
                    #required=True,
                    readonly=True, states={'no_copy': [('readonly', False)]},)

    # Sistema de Estados
    state = fields.Selection([
        ('no_copy', 'LdM No copiada.'),
        ('copied', 'Ldm Copiada.')], string='Estado',
        copy=False, index=True, readonly=True,
        store=True, tracking=True, default='no_copy',
        help=" * LdM No copiada: La lista de materiales no se ha copiado.\n"
             " * LdM Copiada: La lista de materiales se ha copiado de la Compañía copia LdM seleccionada.")

    def action_copy_ldm(self):
        self.state = 'copied'
        _logger.critical("LdM Copiada.")
        return True