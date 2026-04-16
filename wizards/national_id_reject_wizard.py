from odoo import models, fields, api

class NationalIdRejectWizard(models.TransientModel):
    _name = 'national.id.reject.wizard'
    _description = 'Reject Application Wizard'

    national_id_id = fields.Many2one('national.id', string='Application', required=True)
    rejection_reason = fields.Text(string='Reason for Rejection', required=True)

    def action_confirm_reject(self):
        national_id = self.national_id_id
        national_id.state = 'rejected'
        national_id.rejection_reason = self.rejection_reason

        # Log in chatter
        approver = self.env.user.name
        national_id.message_post(
            body=f"❌ Application REJECTED by: {approver}\n"
                 f"Reason: {self.rejection_reason}",
            message_type='notification'
        )
        return {'type': 'ir.actions.act_window_close'}
