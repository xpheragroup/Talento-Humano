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
