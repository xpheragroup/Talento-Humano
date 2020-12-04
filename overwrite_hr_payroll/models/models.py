from odoo import models, fields, api
from odoo.tools import date_utils
from datetime import date, datetime, time
from collections import defaultdict


class overwrite_payroll_contract(models.Model):
    _inherit = 'hr.contract'
    tipo_de_contrato = fields.Selection(
        selection=[('1','Contrato a término indefinido'),
        ('2', 'Contrato integral'),
        ('3', 'Contrato a término fijo'),
        ('4', 'Contrato a término fijo SNH'),
        ('5', 'Contrato de aprendizaje'),
        ('6', 'Contrato de Obra o labor'),
        ('7', 'Contrato de relevantes'),
        ('8', 'Contrato de jornada tiempo parcial')]
    )

    eps = fields.Char(
        string='EPS',
        help='Ingrese la EPS'
    )

    caja_compensacion = fields.Char(
        string='Caja de compensación',
        help='Aquí se debe ingresar la caja de compensación'
    )

    fondo_pension = fields.Char(
        string='Fondo de pensiones',
        help='Aquí se debe ingresar la caja de compensación'
    )

    aseguradora_riesgo = fields.Char(
        string='Nombre de aseguradora ARL',
        help='Aquí se debe diligenciar el nombre de la aseguradora'
    )

    clase_riesgo = fields.Selection(
        string='Clase de riesgo',
        selection=[('1', 'Tipo I'),
                   ('2', 'Tipo II'),
                   ('3', 'Tipo III'),
                   ('4', 'Tipo IV'),
                   ('5', 'Tipo V')]
    )




class overwrite_payroll_employee(models.Model):
    _inherit = 'hr.employee'
#informacion personal
    ciudad_de_nacimiento = fields.Char()
    ciudad_actual = fields.Char()
    casa_propia = fields.Boolean(string='¿tiene casa propia?')
    carro_propio = fields.Boolean(string='¿tiene carro?')
    placas_carro =fields.Integer()

#informacion de documento
    tipo_de_documento = fields.Selection(
        string='Tipo de documento',
        selection=[('1', 'Cédula de ciudadanía'),
                   ('2', 'Cédula de extranjería'),
                   ('3', 'Pasaporte'),]
    )
    ciudad_de_expedicion = fields.Char()

#informacion de salud
    fuma = fields.Boolean(string='¿fuma?')
    estatura = fields.Integer(string="estatura en centimetros")
    anteojos = fields.Boolean(string='¿usa anteojos?')
    factor_rh = fields.Selection(
        string='Factor RH',
        selection=[('1', 'positivo'),
                   ('2', 'negativo'),]
    )
    grupo_sanguineo = fields.Selection(
        string='Grupo Sanguineo',
        selection=[('1', 'O'),
                   ('2', 'A'),
                   ('3', 'B'),
                   ('4', 'AB')]
    )
    embarazo = fields.Boolean(string='¿se encuentra en estado de embarazo?')

#informacion judicial
    libreta_militar = fields.Boolean(string='¿tiene libreta militar?')
    certificado_judicial = fields.Boolean()


class overwrite_payroll_payslip(models.Model):
    _inherit = 'hr.payslip'
    
    def _get_worked_day_lines(self):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            paid_amount = self._get_contract_wage()
            unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids.ids

            work_hours = contract._get_work_hours(self.date_from, self.date_to)
            total_hours = sum(work_hours.values()) or 1
            total_days = 30.0
            total_days_work = 30.0
            work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
            biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
            add_days_rounding = 0
            for work_entry_type_id, hours in work_hours_ordered:
                work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
                is_paid = work_entry_type_id not in unpaid_work_entry_types
                calendar = contract.resource_calendar_id
                days = round(hours / calendar.hours_per_day, 0) if calendar.hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    if((self.date_to.day == 30 or self.date_to.day == 31 
                    or ((self.date_to.day == 28 or self.date_to.day == 29) and self.date_to.month == 2))):
                        days  = total_days_work
                    days += add_days_rounding
                else:
                    total_days_work = total_days_work - days
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': day_rounded,
                    'number_of_hours': hours,
                    'amount': day_rounded * paid_amount / total_days if is_paid else 0,
                }
                res.append(attendance_line)
        return res