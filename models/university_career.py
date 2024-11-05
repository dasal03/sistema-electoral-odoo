from odoo import api, models, fields
from odoo.exceptions import ValidationError


class UniversityCareer(models.Model):
    _name = "university.career"
    _description = "University Career"

    code = fields.Char(string="Career Code", required=True)
    name = fields.Char(string="Career Name", required=True)
    campus_id = fields.Many2one(
        "university.campus", string="Campus", required=True)

    @api.constrains("campus_id")
    def _check_campus_relationship(self):
        "Check if the career is associated with a campus"
        for record in self:
            if not record.campus_id:
                raise ValidationError(
                    "La carrera debe estar asociada a un campus.")
