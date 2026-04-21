from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NationalId(models.Model):
    _name = 'national.id'
    _description = 'National ID Registration'
    _rec_name = 'full_name'
    _order = 'create_date desc'

    # user input fields
    surname = fields.Char(string='Surname', required=True)
    given_name = fields.Char(string='Given Name', required=True)
    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    sex = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string='Sex', required=True
    )
    mobile_number = fields.Char(string='Mobile Number', required=True)
    district = fields.Char(string='District', required=True)
    village = fields.Char(string='Village', required=True)
    citizenship_type = fields.Selection([
        ('birth', 'By Birth'),
        ('registration', 'By Registration'),
        ('naturalisation', 'By Naturalisation'),
        ('dual', 'Dual Citizen'),
    ], string='Citizenship', default='birth', required=True)
    applicant_photo = fields.Binary(string='Passport Photo', attachment=True)
    applicant_photo_filename = fields.Char()
    lc_letter = fields.Binary(string='LC Reference Letter', attachment=True)
    lc_letter_filename = fields.Char(string='Letter Filename')

    # system fields
    id_number = fields.Char(string='Application ID', readonly=True, copy=False)
    state = fields.Selection([
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='submitted', string='Status')
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)

    @api.depends('surname', 'given_name')
    def _compute_full_name(self):
        for record in self:
            record.full_name = f"{record.given_name or ''} {record.surname or ''}".strip()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('id_number') or vals.get('id_number') == 'New':
                seq = self.env['ir.sequence'].next_by_code('national.id.seq') or '000001'
                vals['id_number'] = f'{seq}'
        return super().create(vals_list)

    def action_approve(self):
        for record in self:
            record.state = 'approved'

    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'national.id.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_national_id_id': self.id},
        }