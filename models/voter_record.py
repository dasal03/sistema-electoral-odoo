from odoo import api, models, fields
from odoo.exceptions import ValidationError


class VoterRecord(models.Model):
    _name = "voter.record"
    _description = "Voter Record"

    student_id = fields.Many2one(
        "res.partner", string="Student", required=True)
    candidate_id = fields.Many2one(
        "res.partner", string="Candidate", required=True)
    voting_process_id = fields.Many2one(
        "voting.process", string="Voting Process", required=True
    )

    @api.constrains("student_id", "voting_process_id")
    def _check_unique_vote(self):
        for record in self:
            if self.search_count(
                [
                    ("student_id", "=", record.student_id.id),
                    ("voting_process_id", "=", record.voting_process_id.id),
                    ("id", "!=", record.id)
                ]
            ) > 0:
                raise ValidationError(
                    "El estudiante ya ha votado en esta votación."
                )
