from odoo import models, fields, api


class VotingStatistics(models.TransientModel):
    _name = "voting.statistics"
    _description = "Voting Statistics"

    voting_process_id = fields.Many2one(
        "voting.process", string="Voting Process")
    candidate_id = fields.Many2one("res.partner", string="Candidate")
    vote_count = fields.Integer(string="Vote Count")

    @api.model
    def calculate_votes(self):
        self.search([]).unlink()

        records = []
        voting_processes = self.env["voting.process"].search([])

        for voting in voting_processes:
            for candidate in voting.candidates_ids:
                count = self.env["voter.record"].search_count(
                    [
                        ("voting_process_id", "=", voting.id),
                        ("candidate_id", "=", candidate.id),
                    ]
                )
                records.append(
                    {
                        "voting_process_id": voting.id,
                        "candidate_id": candidate.id,
                        "vote_count": count,
                    }
                )

        self.create(records)
