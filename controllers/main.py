import base64
from odoo import http
from odoo.http import request

class NationalIdController(http.Controller):

    @http.route('/apply_national_id', type='http', auth="public", website=True, sitemap=False)
    def id_form(self, **post):
        """Display or process the National ID application form"""
        if post:
            # Prepare values from form submission
            vals = {
                'surname': post.get('surname'),
                'given_name': post.get('given_name'),
                'other_names': post.get('other_names'),
                'date_of_birth': post.get('date_of_birth'),
                'sex': post.get('sex'),
                'mobile_number': post.get('mobile_number'),
                'email': post.get('email'),
                'district': post.get('district'),
                'village': post.get('village'),
                'sub_county': post.get('sub_county'),
                'plot_house_number': post.get('plot_house_number'),
                'birth_district': post.get('birth_district'),
                'indigenous_community': post.get('indigenous_community'),
                'clan': post.get('clan'),
                'occupation': post.get('occupation'),
                'citizenship_type': post.get('citizenship_type'),
                'marital_status': post.get('marital_status'),
                'religion': post.get('religion'),
                'education_level': post.get('education_level'),
            }

            # Handle Applicant Photo
            if post.get('applicant_photo'):
                photo = post.get('applicant_photo')
                vals['applicant_photo'] = base64.b64encode(photo.read())
                vals['applicant_photo_filename'] = photo.filename

            # Handle LC Reference Letter
            if post.get('lc_letter'):
                letter = post.get('lc_letter')
                vals['lc_letter'] = base64.b64encode(letter.read())
                vals['lc_letter_filename'] = letter.filename

            # Handle Birth Certificate (optional)
            if post.get('birth_certificate'):
                cert = post.get('birth_certificate')
                vals['birth_certificate'] = base64.b64encode(cert.read())

            # Create the application record
            application = request.env['national.id'].sudo().create(vals)

            # Render thank you page with application ID
            return request.render("National_Id_application.thanks_template", {
                'application_id': application.id_number,
                'name': f"{application.given_name} {application.surname}"
            })

        # Return the empty form
        return request.render("National_Id_application.apply_form_template")
