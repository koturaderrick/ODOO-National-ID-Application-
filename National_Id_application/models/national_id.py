from odoo import models, fields, api
from odoo.exceptions import AccessError


class NationalId(models.Model):
    _name = 'national.id'
    _description = 'National ID Registration'
    _rec_name = 'full_name'
    _order = 'create_date desc'

    surname = fields.Char(string='Surname', required=True)
    given_name = fields.Char(string='Given Name', required=True)
    full_name = fields.Char(
        string='Full Name', compute='_compute_full_name', store=True
    )
    date_of_birth = fields.Date(string='Date of Birth', required=True)
    sex = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string='Sex', required=True
    )
    mobile_number = fields.Char(string='Mobile Number', required=True)
    district = fields.Char(string='District', required=True)
    village = fields.Char(string='Village', required=True)
    citizenship_type = fields.Selection([
        ('birth',          'By Birth'),
        ('registration',   'By Registration'),
        ('naturalisation', 'By Naturalisation'),
        ('dual',           'Dual Citizen'),
    ], string='Citizenship', default='birth', required=True)

    applicant_photo = fields.Binary(string='Passport Photo', attachment=True)
    applicant_photo_filename = fields.Char()
    lc_letter = fields.Binary(string='LC Reference Letter', attachment=True)
    lc_letter_filename = fields.Char(string='Letter Filename')


    id_number = fields.Char(string='Application ID', readonly=True, copy=False)

    state = fields.Selection([
        ('submitted', 'Submitted'),
        ('stage1',    'Stage 1 - Verification'),
        ('stage2',    'Stage 2 - Final Approval'),
        ('approved',  'Approved'),
        ('rejected',  'Rejected'),
    ], default='submitted', string='Status')

    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)

    approval_log = fields.Text(
        string='Approval History', readonly=True,
        default='No actions yet.'
    )


    @api.depends('surname', 'given_name')
    def _compute_full_name(self):
        for r in self:
            r.full_name = f"{r.given_name or ''} {r.surname or ''}".strip()


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('id_number'):
                seq = (
                    self.env['ir.sequence'].next_by_code('national.id.seq')
                    or '000001'
                )
                vals['id_number'] = f'NIRA/{seq}'
        return super().create(vals_list)


    def _check_group(self, xml_id):
        if not self.env.user.has_group(xml_id):
            raise AccessError(
                'You do not have the required rights to perform this action.'
            )

    def _add_log(self, record, message):
        from datetime import datetime
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        new_entry = f'[{ts}]  {message}'
        existing = record.approval_log or ''
        if existing == 'No actions yet.':
            existing = ''
        record.approval_log = existing + new_entry + '\n'

    def action_verify_documents(self):
        """Stage 1 Verifier only: approve documents and move to Stage 2."""
        self._check_group('National_Id_application.group_nira_stage1')
        for rec in self:
            rec.state = 'stage2'
            self._add_log(
                rec,
                f'STAGE 1 APPROVED — documents verified by {self.env.user.name}'
            )

    def action_final_approve(self):
        """Stage 2 Approver only: grant final approval."""
        self._check_group('National_Id_application.group_nira_stage2')
        for rec in self:
            rec.state = 'approved'
            self._add_log(
                rec,
                f'STAGE 2 FINAL APPROVAL granted by {self.env.user.name}'
            )

    def action_reject(self):
        """Stage 1 Verifier or above: open the rejection wizard."""
        self._check_group('National_Id_application.group_nira_stage1')
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'national.id.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_national_id_id': self.id},
        }

    def action_reset_to_draft(self):
        """Manager only: reset a rejected application back to Submitted."""
        self._check_group('National_Id_application.group_nira_manager')
        for rec in self:
            rec.state = 'submitted'
            rec.rejection_reason = False
            self._add_log(
                rec,
                f'Reset to Submitted by {self.env.user.name}'
            )

    def action_view_lc_letter(self):
        """Open the LC letter in a new browser tab."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/national_id/lc_letter/{self.id}',
            'target': 'new',
        }
