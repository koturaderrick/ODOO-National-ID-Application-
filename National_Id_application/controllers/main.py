import base64
import json
from odoo import http
from odoo.http import request, Response


class NationalIdController(http.Controller):

    #website form 
    @http.route('/apply_national_id', type='http', auth='public', website=True, sitemap=False)
    def id_form(self, **post):
        if post:
            vals = {
                'surname':          post.get('surname'),
                'given_name':       post.get('given_name'),
                'date_of_birth':    post.get('date_of_birth'),
                'sex':              post.get('sex'),
                'citizenship_type': post.get('citizenship_type', 'birth'),
                'mobile_number':    post.get('mobile_number'),
                'district':         post.get('district'),
                'village':          post.get('village'),
            }
            photo = post.get('applicant_photo')
            if photo and hasattr(photo, 'read'):
                vals['applicant_photo'] = base64.b64encode(photo.read())
                vals['applicant_photo_filename'] = photo.filename

            letter = post.get('lc_letter')
            if letter and hasattr(letter, 'read'):
                vals['lc_letter'] = base64.b64encode(letter.read())
                vals['lc_letter_filename'] = letter.filename

            application = request.env['national.id'].sudo().create(vals)
            return request.render('National_Id_application.thanks_template', {
                'application_id': application.id_number,
                'name': f'{application.given_name} {application.surname}',
            })

        return request.render('National_Id_application.apply_form_template')

    #Flutter API: Submit application ─────────────────────────────────────
    @http.route('/api/apply', type='http', auth='public', methods=['POST'], csrf=False)
    def api_submit(self, **post):
        """
        Accepts multipart/form-data from Flutter.
        Returns JSON: { "tracking_number": "000001" }
        """
        try:
            full_name = post.get('full_name', '')
            parts = full_name.strip().split(' ', 1)
            given_name = parts[0] if parts else ''
            surname = parts[1] if len(parts) > 1 else ''

            
            vals = {
                'given_name':       given_name,
                'surname':          surname,
                'date_of_birth':    post.get('date_of_birth'),
                'sex':              post.get('gender', '').lower(),
                'mobile_number':    post.get('phone'),
                'district':         post.get('district'),
                'village':          post.get('sub_county'),
                'citizenship_type': post.get('citizenship_type', 'birth'),
            }

            photo = post.get('applicant_photo')
            if photo and hasattr(photo, 'read'):
                vals['applicant_photo'] = base64.b64encode(photo.read())
                vals['applicant_photo_filename'] = photo.filename

           
            letter = post.get('lc_letter')
            if letter and hasattr(letter, 'read'):
                vals['lc_letter'] = base64.b64encode(letter.read())
                vals['lc_letter_filename'] = letter.filename

            application = request.env['national.id'].sudo().create(vals)

            return Response(
                json.dumps({
                    'success': True,
                    'tracking_number': application.id_number,
                    'name': f'{application.given_name} {application.surname}',
                }),
                content_type='application/json',
                status=200,
            )

        except Exception as e:
            return Response(
                json.dumps({'success': False, 'error': str(e)}),
                content_type='application/json',
                status=500,
            )
    @http.route('/api/track/<string:tracking_number>', type='http', auth='public', methods=['GET'], csrf=False)
    def api_track(self, tracking_number, **kwargs):
        """
        Returns JSON with the application stage for Flutter tracking screen.
        Odoo state → Flutter stage mapping:
            submitted  → Pending
            stage1     → Verified
            stage2     → Senior Approval
            approved   → Final Approval
            rejected   → Rejected
        """
        application = request.env['national.id'].sudo().search(
            [('id_number', '=', tracking_number)], limit=1
        )

        if not application:
            return Response(
                json.dumps({'success': False, 'error': 'Application not found.'}),
                content_type='application/json',
                status=404,
            )
        state_map = {
            'submitted':    'Pending',
            'stage1':    'Verified',
            'stage2':    'Senior Approval',
            'approved':  'Final Approval',
            'rejected':  'Rejected',
        }

        message_map = {
            'submitted':   'Your application has been received and is awaiting review.',
            'stage1':    'Your documents have been verified by our team.',
            'stage2':      'Your application is under senior officer review.',
            'approved':  'Your National ID has been approved and is being processed.',
            'rejected':    'Your application was rejected. Please contact the office.',
        }

        stage = state_map.get(application.state, 'Pending')
        message = message_map.get(application.state, 'Status unknown.')

        return Response(
            json.dumps({
                'success':          True,
                'tracking_number':  application.id_number,
                'stage':            stage,
                'message':          message,
                'applicant_name':   application.full_name,
                'submitted_date':   str(application.create_date.date()) if application.create_date else '',
                'last_updated':     str(application.write_date.date()) if application.write_date else '',
            }),
            content_type='application/json',
            status=200,
        )

    @http.route('/national_id/lc_letter/<int:record_id>', type='http', auth='user')
    def view_lc_letter(self, record_id, **kwargs):
        record = request.env['national.id'].browse(record_id)
        if not record.exists() or not record.lc_letter:
            return Response('LC Letter not found.', status=404)

        file_data = base64.b64decode(record.lc_letter)
        filename = record.lc_letter_filename or 'lc_letter'

        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith('.png'):
            content_type = 'image/png'
        else:
            content_type = 'image/jpeg'

        headers = [
            ('Content-Type', content_type),
            ('Content-Disposition', f'inline; filename="{filename}"'),
        ]
        return Response(file_data, headers=headers)
