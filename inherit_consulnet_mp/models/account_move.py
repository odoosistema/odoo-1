from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'
    

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.currency_id.name != 'CLP':
            raise UserError(_('El tipo de moneda debe ser igual a CLP.'))
        return res

