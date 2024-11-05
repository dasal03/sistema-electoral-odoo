from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class VotingProcess(models.Model):
    _name = "voting.process"
    _description = "Voting Process"

    description = fields.Char(string="Description", required=True)
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)
    campus_id = fields.Many2one(
        "university.campus", string="Campus", required=True)
    candidates_ids = fields.Many2many("res.partner", string="Candidates")
    voter_ids = fields.One2many(
        "voter.record", "voting_process_id", string="Voter Records"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("open", "Open"), ("closed", "Closed")],
        default="draft",
        string="State",
        readonly=True,
    )
    total_votes = fields.Integer(
        compute="_compute_total_votes", string="Total Votes", store=False
    )

    @api.depends("voter_ids")
    def _compute_total_votes(self):
        for record in self:
            record.total_votes = len(record.voter_ids)

    @api.constrains("start_date", "end_date")
    def _check_voting_dates(self):
        for record in self:
            if record.start_date >= record.end_date:
                raise ValidationError(
                    "La fecha de inicio no puede ser posterior a "
                    "la fecha de finalización."
                )
            if datetime.now() > record.end_date:
                raise ValidationError("El proceso ya finalizó.")

    def action_open_voting(self):
        if self.state != "draft":
            raise UserError("Solo procesos en borrador pueden ser abiertos.")
        if datetime.now() < self.start_date or datetime.now() > self.end_date:
            raise UserError(
                "No se puede abrir un proceso fuera del rango de fechas.")
        self.state = "open"

    def action_close_voting(self):
        if self.state != "open":
            raise UserError("Solo los procesos abiertos pueden ser cerrados.")
        self.state = "closed"

    @api.onchange("campus_id")
    def _onchange_campus_id(self):
        if self.campus_id:
            candidates = self.env["res.partner"].search(
                [("is_candidate", "=", True),
                 ("campus_id", "=", self.campus_id.id)]
            )
            return {"domain": {"candidates_ids": [
                ("id", "in", candidates.ids)]}}
