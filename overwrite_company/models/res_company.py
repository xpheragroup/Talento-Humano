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

    empresa_copy_ldm = fields.Many2one('res.company', string='Compañía copia LdM', index=True,
                    readonly=True, states={'no_copy': [('readonly', False)]},)

    copy_ldm = fields.Many2many(string="Listas de materiales asociadas a Compañía copia LdM",
                    comodel_name='mrp.bom',
                    relation="bom_company_copy",
                    help="Selección de Listas de materiales asociadas a Compañía copia LdM.",
                    domain="[('company_id','=',empresa_copy_ldm)]",
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

        if self.copy_ldm:
            for ldm in self.copy_ldm:
                new_copy_ldm = ldm.copy({
                            'company_id': self.company_id,
                            'picking_type_id': self.warehouse_1.manu_type_id.id,
                            'cost_center': None,
                            'bom_line_ids': [(6, 0, [p.id for p in ldm.bom_line_ids])],
                        })
                
        else:
            raise UserError(_("No se encuentra ninguna lista de materiales asociada a la companía seleccionada."))



        return True


    @api.onchange('empresa_copy_ldm')
    def _onchange_empresa_copy_ldm(self):
        self.copy_ldm = None

        if self.empresa_copy_ldm:
            self.copy_ldm = self.env['mrp.bom'].search([('company_id', '=', self.empresa_copy_ldm.id)])
            _logger.critical("self.copy_ldm")
            _logger.critical(self.copy_ldm)
