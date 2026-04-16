from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class NationalId(models.Model):
    _name = 'national.id'
    _description = 'National ID Registration'
    _inherit = ['mail.thread']   # mail.thread only – no activity mixin (removes the noise logs)
    _rec_name = 'full_name'
    _order = 'create_date desc'

    # ── 10 Application Fields ────────────────────────────────────────────────

    # Field 1
    surname = fields.Char(string='Surname', required=True, tracking=True)

    # Field 2
    given_name = fields.Char(string='Given Name', required=True, tracking=True)

    # Computed – not a separate field
    full_name = fields.Char(string='Full Name', compute='_compute_full_name', store=True)

    @api.depends('surname', 'given_name')
    def _compute_full_name(self):
        for r in self:
            r.full_name = ' '.join(n for n in [r.given_name, r.surname] if n)

    # Field 3
    date_of_birth = fields.Date(string='Date of Birth', required=True, tracking=True)

    # Field 4
    sex = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string='Sex', required=True, tracking=True
    )

    # Field 5
    citizenship_type = fields.Selection(
        [
            ('birth', 'By Birth'),
            ('registration', 'By Registration'),
            ('naturalisation', 'By Naturalisation'),
            ('dual', 'Dual Citizen'),
        ],
        string='Citizenship', default='birth', required=True, tracking=True
    )

    # Field 6
    mobile_number = fields.Char(string='Mobile Number', required=True, tracking=True)

    # Field 7
    district = fields.Char(string='District', required=True, tracking=True)

    # Field 8
    village = fields.Char(string='Village', required=True, tracking=True)

    # Field 9
    applicant_photo = fields.Binary(string='Passport Photo', attachment=True)
    applicant_photo_filename = fields.Char()

    # Field 10
    lc_letter = fields.Binary(string='LC Reference Letter', attachment=True)
    lc_letter_filename = fields.Char(string='LC Letter Filename')

    # ── System fields ────────────────────────────────────────────────────────

    email = fields.Char(string='Email Address (for notifications)')

    id_number = fields.Char(string='Application ID', readonly=True, copy=False)

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('stage1', 'Stage 1 - Verification'),
            ('stage2', 'Stage 2 - Final Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='draft', string='Status', tracking=True
    )

    rejection_reason = fields.Text(string='Rejection Reason', readonly=True)

    # ── Create ───────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('id_number') or vals.get('id_number') == 'New':
                seq = self.env['ir.sequence'].next_by_code('national.id.seq') or '000000'
                vals['id_number'] = f'NIRA/{seq}'
        return super().create(vals_list)

    # ── Workflow ─────────────────────────────────────────────────────────────

    def action_submit_to_stage1(self):
        for record in self:
            if not record.applicant_photo or not record.lc_letter:
                raise ValidationError(
                    'Please upload both a Passport Photo and an LC Reference Letter before submitting.'
                )
            record.state = 'stage1'
            record.message_post(
                body=f'Application submitted for Stage 1 Verification by {self.env.user.name}',
                message_type='notification',
            )

    def action_verify_documents(self):
        for record in self:
            record.state = 'stage2'
            record.message_post(
                body=f'Stage 1 – Documents verified and approved by {self.env.user.name}',
                message_type='notification',
            )

    def action_final_approve(self):
        for record in self:
            record.state = 'approved'
            record.message_post(
                body=f'Final Approval granted by {self.env.user.name}',
                message_type='notification',
            )
            # Send approval notifications to the applicant
            record._send_approval_notifications()

    def action_reject(self):
        self.ensure_one()
        return {
            'name': 'Reject Application',
            'type': 'ir.actions.act_window',
            'res_model': 'national.id.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_national_id_id': self.id},
        }

    def action_reset_to_draft(self):
        for record in self:
            record.state = 'draft'
            record.rejection_reason = False
            record.message_post(
                body=f'Application reset to Draft by {self.env.user.name}',
                message_type='notification',
            )

    # ── Notification helpers ─────────────────────────────────────────────────

    def _send_approval_notifications(self):
        """Send SMS and/or email to the applicant on final approval."""
        for record in self:
            name = record.full_name
            ref  = record.id_number

            # ── SMS via Odoo SMS gateway ──────────────────────────────────
            if record.mobile_number:
                sms_body = (
                    f"Dear {name}, your National ID application ({ref}) has been APPROVED. "
                    f"Please visit your nearest NIRA office to collect your ID. "
                    f"Thank you."
                )
                try:
                    self.env['sms.sms'].sudo().create({
                        'number': record.mobile_number,
                        'body': sms_body,
                        'state': 'outgoing',
                    })
                    record.message_post(
                        body=f'SMS notification sent to {record.mobile_number}',
                        message_type='notification',
                    )
                except Exception as e:
                    _logger.warning('Could not send SMS for %s: %s', ref, e)
                    record.message_post(
                        body=f'SMS could not be sent to {record.mobile_number}. Please notify the applicant manually.',
                        message_type='notification',
                    )

            # ── Email ─────────────────────────────────────────────────────
            if record.email:
                try:
                    mail_values = {
                        'subject': f'National ID Application {ref} – APPROVED',
                        'email_to': record.email,
                        'body_html': f"""
                            <p>Dear <strong>{name}</strong>,</p>
                            <p>We are pleased to inform you that your National ID application
                            with reference number <strong>{ref}</strong> has been
                            <span style="color:green;"><strong>APPROVED</strong></span>.</p>
                            <p>Please visit your nearest <strong>NIRA office</strong> with this
                            reference number to collect your National ID card.</p>
                            <br/>
                            <p>Thank you,<br/>National Identification &amp; Registration Authority (NIRA)</p>
                        """,
                    }
                    self.env['mail.mail'].sudo().create(mail_values).send()
                    record.message_post(
                        body=f'Email notification sent to {record.email}',
                        message_type='notification',
                    )
                except Exception as e:
                    _logger.warning('Could not send email for %s: %s', ref, e)
                    record.message_post(
                        body=f'Email could not be sent to {record.email}. Please notify the applicant manually.',
                        message_type='notification',
                    )
