from odoo import models, fields

class NationalId(models.Model):
    _name = 'national.id'
    _description = 'National ID Registration'

    name = fields.Char(string='Full Name', required=True)
    id_number = fields.Char(string='ID Number', required=True)
    date_of_birth = fields.Date(string='Date of Birth')
    district = fields.Char(string='District')
