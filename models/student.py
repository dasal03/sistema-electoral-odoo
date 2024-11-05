from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Student(models.Model):
    _inherit = "res.partner"
    _description = "Student"

    is_student = fields.Boolean(default=False)
    is_candidate = fields.Boolean(default=False)
    identification_number = fields.Char(
        string="Identification Number", required=True)
    career_id = fields.Many2one("university.career", string="Career")
    campus_id = fields.Many2one(
        "university.campus", string="Campus", required=True)
    vote_count = fields.Integer(string="Vote Count", default=0, readonly=True)

    @api.model
    def create(self, vals):
        "Set is_student to True for newly created students"
        vals["is_student"] = True
        return super(Student, self).create(vals)

    def write(self, vals):
        if self.is_student:
            vals["is_student"] = True
        return super(Student, self).write(vals)

    @api.constrains("campus_id")
    def _check_student_campus(self):
        "Check if the student is associated to a campus"
        for record in self:
            if not record.campus_id:
                raise ValidationError(
                    "El estudiante debe estar asociado a un campus.")

    @api.constrains("identification_number")
    def _check_identification_number(self):
        "Check if the identification number is unique"
        for record in self:
            if not record.identification_number:
                raise ValidationError(
                    "El número de identificación no puede ser vacio.")

            if (
                self.search_count(
                    [
                        (
                            "identification_number", "=",
                            record.identification_number
                        ),
                        ("id", "!=", record.id),
                        ("is_student", "=", True)
                    ]
                ) > 0
            ):
                raise ValidationError(
                    "Ya existe un estudiante con este numero de identificación."
                )
