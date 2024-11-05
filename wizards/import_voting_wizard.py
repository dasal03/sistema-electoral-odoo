import csv
import base64
from io import StringIO
from datetime import datetime
from odoo import models, fields
from odoo.exceptions import UserError


class ImportVotingWizard(models.TransientModel):
    _name = "import.voting.wizard"
    _description = "Wizard to import voting processes"

    file = fields.Binary("File", required=True)
    file_name = fields.Char("File Name")

    def import_voting_processes(self):
        if not self.file:
            raise UserError("No file uploaded.")

        file_data = base64.b64decode(self.file)
        file_content = StringIO(file_data.decode("utf-8"))
        reader = csv.DictReader(file_content)

        for row in reader:
            try:
                campus = self.env["university.campus"].search(
                    [("name", "=", row["campus"])], limit=1
                )
                if not campus:
                    raise UserError(
                        f"El campus '{row['campus']}' "
                        "no existe en la base de datos."
                    )

                self.env["voting.process"].create(
                    {
                        "description": row["description"],
                        "start_date": fields.Datetime.to_string(
                            datetime.strptime(
                                row["start_date"], "%Y-%m-%d %H:%M:%S")
                        ),
                        "end_date": fields.Datetime.to_string(
                            datetime.strptime(
                                row["end_date"], "%Y-%m-%d %H:%M:%S")
                        ),
                        "campus_id": campus.id,
                    }
                )
            except UserError as e:
                raise UserError(f"Error importing row: {row}. Error: {str(e)}")
            except Exception as e:
                raise UserError(f"Error importing row: {row}. Error: {str(e)}")

        return {"type": "ir.actions.act_window_close"}
