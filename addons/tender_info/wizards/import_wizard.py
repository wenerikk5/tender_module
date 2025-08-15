import re
import logging

from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError

from ..providers import ETPApiClient

_logger = logging.getLogger(__name__)
etp_api = ETPApiClient()

IMPORT_FAIL_MESSAGE = "Не удалось загрузить данные, обратитесь к администратору."

class ImportWizard(models.TransientModel):
    _name = 'tender.import.wizard'
    _description = 'Import Procedures Wizard'

    inn = fields.Char('ИНН организации', required=True)
    published_from = fields.Date(
        string='Дата публикации от',
        default=fields.Date.today(),
        required=True,
    )

    @api.constrains("published_from")
    def _check_published_from_date(self):
        for record in self:
            if record.published_from > date.today():
                raise UserError("Дата публикации не должна быть в будущем.")

    @api.constrains("inn")
    def _check_inn(self):
        for record in self:
            # Simple validation based on type and length
            if not re.match(r"^(\d{10}|\d{12})$", record.inn):
                raise UserError("Некорректный формат ИНН")

    def action_import(self):
        self.ensure_one()
        self.clear_tables()

        published_from = self.published_from.strftime('%Y-%m-%d')
        procedure_external_id_record_id = self.import_procedures(published_from)
        self.import_procedure_details(procedure_external_id_record_id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Procedures',
            'view_mode': 'tree,form',
            'res_model': 'tender.procedure',
            'target': 'current',
        }

    def import_procedures(self, published_from: date) -> dict:
        _logger.info("Importing a list of procedures")

        # Collect external_id and record.id dict
        procedure_external_id_record_id = {}
        try:
            data = etp_api.get_procedures(published_from=published_from, inn=self.inn)
            for procedure_data in data["data"]:
                data = self.parse_procedure(procedure_data)
                procedure_db = self.env['tender.procedure'].create(data)
                procedure_external_id_record_id[procedure_db.external_id] = procedure_db.id
        except ValueError as _err:
            raise UserError(IMPORT_FAIL_MESSAGE)
        except Exception as err:
            _logger.error(f"Failed to import procedures, error: {err}")
            raise UserError(IMPORT_FAIL_MESSAGE)

        return procedure_external_id_record_id

    def import_procedure_details(self, procedure_external_id_record_id: dict):
        _logger.info("Importing detailed data for procedures %s",
                     procedure_external_id_record_id.keys())

        try:
            procedures = etp_api.get_procedure_details(list(procedure_external_id_record_id.keys()))
            all_lots = []
            success_participants = []
            lot_external_id_record_id = {}

            for procedure in procedures:
                lots = procedure["data"]["lots"]
                all_lots.extend(lots)

            for lot in all_lots:
                procedure_id = procedure_external_id_record_id.get(lot["procedure_external_id"])
                if not procedure_id:
                    _logger.error(f'Not found related procedure_id: {lot["procedure_external_id"]}')
                    raise ValueError

                data = self.parse_lot(lot)
                lot_db = self.env["tender.lot"].create({
                    **data,
                    "procedure_id": procedure_id,
                })

                if lot_db.status == "completed":
                    # Add logic to select additional data required to load
                    participants = lot["participants"]
                    for participant in participants:
                        # Select only a winner and second place
                        if participant["place"] in [1, 2]:
                            success_participants.append(participant)

                lot_external_id_record_id[lot_db.external_id] = lot_db.id

            for participant in success_participants:
                lot_id = lot_external_id_record_id.get(str(participant["lot_external_id"]))
                if not lot_id:
                    _logger.error(f'Not found related lot_external_id: {participant["lot_external_id"]}')
                    raise ValueError

                data = self.parse_participant(participant)
                participant_db = self.env["tender.participant"].create({
                    **data,
                    "lot_id": lot_id,
                })
        except ValueError as _err:
            raise UserError(IMPORT_FAIL_MESSAGE)

        except Exception as err:
            _logger.error(f"Failed to import procedure details, error: {err}")
            raise UserError(IMPORT_FAIL_MESSAGE)

    @staticmethod
    def parse_procedure(data: dict) -> dict:
        try:
            publish_date = datetime.fromisoformat(data['attributes']['date_published'])
            procedure = {
                'external_id': data['external_id'],
                'registry_number': data['attributes']['registry_number'],
                'title': data['attributes']['title'],
                'stage': data['attributes']['stage'],
                'publish_date': publish_date.replace(tzinfo=None),
            }
            return procedure
        except Exception as err:
            _logger.error(f"Failed to parse procedure data: {data} with error: {err}")
            raise ValueError

    @staticmethod
    def parse_lot(data: dict) -> dict:
        try:
            lot = {
                "external_id": data["external_id"],
                "name": data["name"],
                "status": data["status"],
                "reason": data["reason"],
            }
            return lot
        except Exception as err:
            _logger.error(f"Failed to parse lot data: {data} with error: {err}")
            raise ValueError

    @staticmethod
    def parse_participant(data: dict) -> dict:
        try:
            participant = {
                "name": data["name"],
                "inn": data["inn"],
                "address": data["address"],
                "price": data["price"],
                "place": data.get("place", 0)
            }
            return participant
        except Exception as err:
            _logger.error(f"Failed to parse participant data: {data} with error: {err}")
            raise ValueError

    def clear_tables(self) -> None:
        tables = ["tender.participant", "tender.lot", "tender.procedure"]

        for table in tables:
            model = self.env[table]
            records = model.search([])
            records.unlink()
