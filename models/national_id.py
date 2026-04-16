from odoo import models, fields, api
from odoo.exceptions import ValidationError

class NationalId(models.Model):
    _name = 'national.id'
    _description = 'National ID Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'full_name'
    _order = 'create_date desc'

    # Personal Information
    surname = fields.Char(string='Surname', required=True, tracking=True)
    given_name = fields.Char(string='Given Name', required=True, tracking=True)
    other_names = fields.Char(string='Other Names', tracking=True)

    @api.depends('surname', 'given_name', 'other_names')
    def _compute_full_name(self):
        for record in self:
            names = [record.given_name, record.other_names, record.surname]
            record.full_name = ' '.join([n for n in names if n])

    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)

    date_of_birth = fields.Date(string='Date of Birth', required=True, tracking=True)
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Sex', required=True, tracking=True)

    mobile_number = fields.Char(string='Mobile Number', required=True)
    email = fields.Char(string='Email Address')

    # Address
    district = fields.Char(string='District', required=True, tracking=True)
    village = fields.Char(string='Village', required=True)

    # Origin
    tribe = fields.Char(string='Tribe')
    clan = fields.Char(string='Clan')

    # Occupation
    occupation = fields.Char(string='Occupation')

    # Citizenship
    citizenship_type = fields.Selection([
        ('birth', 'By Birth'),
        ('registration', 'By Registration'),
        ('naturalisation', 'By Naturalisation'),
        ('dual', 'Dual Citizen')
    ], string='Citizenship', default='birth', required=True)

    # System generated ID
    id_number = fields.Char(string='Application ID', readonly=True, copy=False)

    # Attachments
    applicant_photo = fields.Binary(string='Passport Photo', attachment=True)
    lc_letter = fields.Binary(string='LC Reference Letter', attachment=True)
    lc_letter_filename = fields.Char(string='Letter Filename')

    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('stage1', 'Stage 1 - Verification'),
        ('stage2', 'Stage 2 - Final Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', string='Status', tracking=True)

    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        # Handle batch creation
        for vals in vals_list:
            if not vals.get('id_number'):
                seq = self.env['ir.sequence'].next_by_code('national.id.seq') or '0001'
                vals['id_number'] = f'NIRA/{seq}'
        return super(NationalId, self).create(vals_list)

    def action_submit_to_stage1(self):
        for record in self:
            if not record.applicant_photo or not record.lc_letter:
                raise ValidationError('Please upload both photo and LC letter')
            record.state = 'stage1'
            record.message_post(body=f'Application submitted to Stage 1 by {record.full_name}')

    def action_verify_documents(self):
        for record in self:
            record.state = 'stage2'
            approver = self.env.user.name
            record.message_post(body=f'Stage 1 Approved by: {approver}. Moving to Stage 2')

    def action_final_approve(self):
        for record in self:
            record.state = 'approved'
            approver = self.env.user.name
            record.message_post(body=f'FINAL APPROVAL by: {approver}. ID: {record.id_number}')

    def action_reject(self):
        return {
            'name': 'Reject Application',
            'type': 'ir.actions.act_window',
            'res_model': 'national.id.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_national_id_id': self.id}
        }

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'
            record.rejection_reason = False
            record.message_post(body='Application reset to Draft')
