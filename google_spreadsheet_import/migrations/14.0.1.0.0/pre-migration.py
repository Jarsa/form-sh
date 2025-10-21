# Copyright 2021 Jarsa <http://www.forgeflow.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openupgradelib import openupgrade

_model_renames = [
    ("google.drive.sheet", "google.spreadsheet"),
    ("google.drive.sheet.error", "google.spreadsheet.error"),
    ("google.drive.file", "google.spreadsheet.file"),
    ("google.drive.file.sheet", "google.spreadsheet.file.sheet"),
    ("google.drive.file.model", "google.spreadsheet.file.model"),
]

_table_renames = [
    ("google_drive_sheet", "google_spreadsheet"),
    ("google_drive_sheet_error", "google_spreadsheet_error"),
    ("google_drive_file", "google_spreadsheet_file"),
    ("google_drive_file_sheet", "google_spreadsheet_file_sheet"),
    ("google_drive_file_model", "google_spreadsheet_file_model"),
]

_xmlid_renames = [
    (
        "google_spreadsheet_import.google_drive_file_form",
        "google_spreadsheet_import.google_spreadsheet_file_form",
    ),
    (
        "google_spreadsheet_import.google_drive_file_tree",
        "google_spreadsheet_import.google_spreadsheet_file_tree",
    ),
    (
        "google_spreadsheet_import.action_google_drive_file",
        "google_spreadsheet_import.action_google_spreadsheet_file",
    ),
    (
        "google_spreadsheet_import.google_drive_file_menu",
        "google_spreadsheet_import.google_spreadsheet_file_menu",
    ),
    (
        "google_spreadsheet_import.google_drive_sheet_form",
        "google_spreadsheet_import.google_spreadsheet_form",
    ),
    (
        "google_spreadsheet_import.google_drive_sheet_tree",
        "google_spreadsheet_import.google_spreadsheet_tree",
    ),
    (
        "google_spreadsheet_import.google_drive_sheet_search",
        "google_spreadsheet_import.google_spreadsheet_search",
    ),
    (
        "google_spreadsheet_import.action_google_drive_sheet",
        "google_spreadsheet_import.action_google_spreadsheet",
    ),
    (
        "google_spreadsheet_import.google_drive_sheet_menu",
        "google_spreadsheet_import.google_spreadsheet_menu",
    ),
]

records_to_remove = [
    "google_spreadsheet_import.auto_upload_drive_sheet_example",
    "google_spreadsheet_import.bitodoo_drive_sheet_assets_backend",
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.rename_xmlids(cr, _xmlid_renames)
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
    openupgrade.delete_records_safely_by_xml_id(env, records_to_remove)
