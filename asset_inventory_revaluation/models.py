from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Asset(models.Model):
    _name = 'asset_inventory_revaluation.asset'
    _description = 'Asset'

    name = fields.Char(string='Asset Name', required=True)
    asset_code = fields.Char(string='Asset Code', required=True, unique=True)
    purchase_date = fields.Date(string='Purchase Date')
    purchase_value = fields.Float(string='Purchase Value')
    current_value = fields.Float(string='Current Value', compute='_compute_current_value', store=True)
    location = fields.Char(string='Location')
    state = fields.Selection([
        ('active', 'Active'),
        ('disposed', 'Disposed'),
    ], string='Status', default='active')

    inventory_ids = fields.One2many('asset_inventory_revaluation.inventory', 'asset_id', string='Inventory Records')
    revaluation_ids = fields.One2many('asset_inventory_revaluation.revaluation', 'asset_id', string='Revaluation Records')

    @api.depends('purchase_value', 'revaluation_ids')
    def _compute_current_value(self):
        for asset in self:
            value = asset.purchase_value
            for reval in asset.revaluation_ids:
                value = reval.new_value
            asset.current_value = value

class Inventory(models.Model):
    _name = 'asset_inventory_revaluation.inventory'
    _description = 'Asset Inventory'

    asset_id = fields.Many2one('asset_inventory_revaluation.asset', string='Asset', required=True)
    inventory_date = fields.Date(string='Inventory Date', required=True, default=fields.Date.context_today)
    quantity = fields.Integer(string='Quantity', required=True, default=1)
    location = fields.Char(string='Location')

class Revaluation(models.Model):
    _name = 'asset_inventory_revaluation.revaluation'
    _description = 'Asset Revaluation'

    asset_id = fields.Many2one('asset_inventory_revaluation.asset', string='Asset', required=True)
    revaluation_date = fields.Date(string='Revaluation Date', required=True, default=fields.Date.context_today)
    old_value = fields.Float(string='Old Value', required=True)
    new_value = fields.Float(string='New Value', required=True)

    @api.constrains('new_value')
    def _check_new_value(self):
        for record in self:
            if record.new_value <= 0:
                raise ValidationError("New value must be greater than zero.")
