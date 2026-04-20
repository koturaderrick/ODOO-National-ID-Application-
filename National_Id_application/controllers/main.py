import base64
from odoo import http
from odoo.http import request, Response


class NationalIdController(http.Controller):

    # application form

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

    # LC Letter viewer 

    @http.route('/national_id/lc_letter/<int:record_id>', type='http', auth='user')
    def view_lc_letter(self, record_id, **kwargs):
        """Serve the LC letter binary so it opens in the browser."""
        record = request.env['national.id'].browse(record_id)
        if not record.exists() or not record.lc_letter:
            
            return Response('LC Letter not found.', status=404)

        file_data = base64.b64decode(record.lc_letter)
        filename = record.lc_letter_filename or 'lc_letter'

        # filename extension
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
