from odoo import models, fields
from odoo.exceptions import ValidationError
import pytz


class UniversityCampus(models.Model):
    _name = "university.campus"
    _description = "University Campus"

    name = fields.Char(string="Campus Name", required=True)
    country_id = fields.Many2one(
        "res.country", string="Country", required=True)
    city_id = fields.Many2one(
        "res.country.state", string="State", required=True)
    active = fields.Boolean(string="Active", default=True)

    def _get_timezone(self):
        """Get the first timezone available for the selected country."""
        if self.country_id:
            country_code = self.country_id.code
            country_timezones = pytz.country_timezones.get(country_code)

            if country_timezones:
                return country_timezones[0]

        return "UTC"

    def _convert_to_campus_timezone(self, date_time):
        """Convert datetime to campus timezone."""
        campus_timezone = pytz.timezone(self._get_timezone())
        utc_time = pytz.utc.localize(date_time)
        return utc_time.astimezone(campus_timezone)

    def validate_voting_period(self, voting_start, voting_end):
        """
        Ensure voting period falls within campus creation
        and last update dates in the campus time zone.
        """
        for record in self:
            create_local = record._convert_to_campus_timezone(
                record.create_date)
            write_local = record._convert_to_campus_timezone(record.write_date)

            start_local = record._convert_to_campus_timezone(voting_start)
            end_local = record._convert_to_campus_timezone(voting_end)

            if start_local < create_local or end_local > write_local:
                raise ValidationError(
                    "Las fechas de votación deben estar en el rango de "
                    "fechas de creación y actualización del campus."
                )
