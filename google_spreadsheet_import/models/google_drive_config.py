# Copyright 2022, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import requests

from odoo import api, models


class GoogleDriveConfig(models.Model):
    _name = "google.drive.config"
    _description = "Google Drive Config"

    @api.model
    def get_access_token(self):
        client_id = self.env["ir.config_parameter"].sudo().get_param(
            "google_spreadsheet_import_client_id")
        client_secret = self.env["ir.config_parameter"].sudo().get_param(
            "google_spreadsheet_import_client_secret")
        refresh_token = self.env["ir.config_parameter"].sudo().get_param(
            "google_spreadsheet_import_refresh_token")
        url = "https://accounts.google.com/o/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded"
        }
        response = requests.request("POST", url, data=data, headers=headers)
        return response.json().get("access_token")
