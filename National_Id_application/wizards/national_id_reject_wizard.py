from odoo import models, fields


class NationalIdRejectWizard(models.TransientModel):
    _name = 'national.id.reject.wizard'
    _description = 'Reject Application Wizard'

    national_id_id = fields.Many2one('national.id', string='Application', required=True)
    rejection_reason = fields.Text(string='Reason for Rejection', required=True)

    def action_confirm_reject(self):
        record = self.national_id_id
        record.state = 'rejected'
        record.rejection_reason = self.rejection_reason
        record.message_post(
            body=f'REJECTED by {self.env.user.name} — Reason: {self.rejection_reason}'
        )
        return {'type': 'ir.actions.act_window_close'}
