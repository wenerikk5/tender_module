# -*- coding: utf-8 -*-
from pkg_resources import require

from odoo import models, fields, api


class Lot(models.TransientModel):
    """
    Лот торговой процедуры.
    """
    _name = 'tender.lot'
    _description = 'Lot'
    _transient_max_hours = 1.0

    external_id = fields.Char('Внешний id', required=True)
    name = fields.Char('Наименование')
    status = fields.Selection(
        [
            ('active', 'Подача заявок'),
            ('cancelled', 'Не состоялся'),
            ('completed', 'Состоялся'),
        ],
        string='Статус',
        required=True,
    )  # Неизвестен весь перечень возможных статусов
    reason = fields.Text('Причина')
    participant_ids = fields.One2many(
        'tender.participant',
        'lot_id',
        string='Участники'
    )
    procedure_id = fields.Many2one(
        'tender.procedure',
        string='Процедура',
        ondelete='cascade',
        required=True,
    )
