import base64
from odoo import http
from odoo.http import request


class NationalIdController(http.Controller):

    @http.route('/apply_national_id', type='http', auth='public', website=True, sitemap=False)
    def id_form(self, **post):
        if post:
            vals = {
                'surname': post.get('surname'),
                'given_name': post.get('given_name'),
                'date_of_birth': post.get('date_of_birth'),
                'sex': post.get('sex'),
                'citizenship_type': post.get('citizenship_type', 'birth'),
                'mobile_number': post.get('mobile_number'),
                'district': post.get('district'),
                'village': post.get('village'),
                'email': post.get('email') or False,
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
