# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Participant(models.TransientModel):
    """
    Участники торгов (победитель и второе место).
    """
    _name = 'tender.participant'
    _description = 'Participant'
    _transient_max_hours = 1.0
    _order = 'place asc, name asc'

    name = fields.Char('ФИО/Наименование', required=True)
    inn = fields.Char('ИНН')
    address = fields.Char('Адрес')
    price = fields.Float('Цена, RUB')
    place = fields.Integer('Место')
    lot_id = fields.Many2one('tender.lot', string='Лот')
