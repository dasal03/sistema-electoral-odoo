from odoo import http
from odoo.http import request


class VotingPortal(http.Controller):

    @http.route("/voting_portal", type="http", auth="public", website=True)
    def voting_portal(self, **kw):
        student_id = kw.get("student_id")
        voting_message = kw.get("voting_message", "")

        if student_id:
            student = request.env["res.partner"].search(
                [("identification_number", "=", student_id)], limit=1
            )

            if not student:
                return request.render(
                    "uniacme_voting.voting_portal_template",
                    {
                        "votings": [],
                        "candidates": [],
                        "error_message": "Cédula no válida.",
                        "student_id": student_id,
                    },
                )

            campus_id = student.campus_id.id if student.campus_id else None
            votings = request.env["voting.process"].search(
                [("state", "=", "open"), ("campus_id", "=", campus_id)]
            )
            candidates = votings.mapped("candidates_ids") if votings else []
            return request.render(
                "uniacme_voting.voting_portal_template",
                {
                    "votings": votings,
                    "candidates": candidates,
                    "error_message": "",
                    "student_id": student_id,
                    "voting_message": voting_message,
                },
            )

        return request.render(
            "uniacme_voting.voting_portal_template",
            {
                "votings": [],
                "candidates": [],
                "error_message": "",
                "student_id": "",
                "voting_message": "",
            },
        )

    @http.route(
        "/vote", type="http", auth="public",
        methods=["POST"], csrf=False, website=True
    )
    def submit_vote(self, **post):
        """Process the submitted voting form."""
        student = request.env["res.partner"].search(
            [("identification_number", "=", post.get("student_id"))], limit=1
        )
        voting_process_id = post.get("voting_process_id")
        candidate_id = post.get("candidate_id")

        if student and voting_process_id and candidate_id:
            existing_vote = request.env["voter.record"].search(
                [
                    ("student_id", "=", student.id),
                    ("voting_process_id", "=", int(voting_process_id)),
                ],
                limit=1,
            )
            if existing_vote:
                voting_message = "Ya has votado."
                return request.redirect(
                    "/voting_portal?student_id={}&voting_message={}".format(
                        post.get("student_id"), voting_message
                    )
                )

            request.env["voter.record"].create(
                {
                    "student_id": student.id,
                    "voting_process_id": int(voting_process_id),
                    "candidate_id": int(candidate_id),
                }
            )

            request.env["voting.statistics"].create(
                {
                    "voting_process_id": int(voting_process_id),
                    "candidate_id": int(candidate_id),
                    "vote_count": 1,
                }
            )

            voting_message = "Tu voto ha sido registrado con éxito."
            return request.redirect(
                "/voting_portal?student_id={}&voting_message={}".format(
                    post.get("student_id"), voting_message
                )
            )

        return request.redirect(
            "/voting_portal?student_id={}&voting_message=Datos inválidos.".format(
                post.get("student_id")
            )
        )
