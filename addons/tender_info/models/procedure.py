# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Procedure(models.TransientModel):
    """
    Информация о торговой процедуре со страницы: https://etpgpb.ru/procedures/
    """
    _name = 'tender.procedure'
    _description = 'Процедура'
    _rec_name = 'registry_number'
    _transient_max_hours = 1.0
    _order = 'publish_date desc'

    external_id = fields.Char('Внешний id', required=True)
    registry_number = fields.Char('Номер', required=True)
    title = fields.Char('Наименование', required=True)
    stage = fields.Selection(
        [
            ('completed', 'Завершен'),
            ('accepting', 'Подача заявок'),
            ('commission', 'Работа комиссии'),
        ],
        string='Этап процедуры',
        required=True,
    )
    publish_date = fields.Datetime('Дата публикации', required=True)
    lot_ids = fields.One2many(
        'tender.lot',
        'procedure_id',
        string='Лоты'
    )
