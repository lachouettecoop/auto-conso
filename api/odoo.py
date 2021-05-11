import logging
import os
import xmlrpc.client
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

ODOO_URL = os.getenv("ODOO_URL", "https://sas.lachouettecoop.fr")
ODOO_DB = os.getenv("ODOO_DB", "dbsas")
ODOO_LOGIN = os.getenv("ODOO_LOGIN")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

AUTO_CONSUMPTION_ID = 8  # Autoconsommation
AUTO_CONSUMPTION_LOC_ID = 18
HYGIENE_ID = 9  # Autoconsommation Hygiène
HYGIENE_LOC_ID = 18
LOSS_ID = 10  # Pertes
LOSS_LOC_ID = 19
COMPANY_ID = 1
STOCK_LOC_ID = 12

blueprint = Blueprint("odoo", __name__)


class OdooAPI:
    def __init__(self):
        try:
            common_proxy_url = "{}/xmlrpc/2/common".format(ODOO_URL)
            object_proxy_url = "{}/xmlrpc/2/object".format(ODOO_URL)
            self.common = xmlrpc.client.ServerProxy(common_proxy_url)
            self.uid = self.common.authenticate(ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD, {})
            self.models = xmlrpc.client.ServerProxy(object_proxy_url)
        except Exception as e:
            logging.error(f"Odoo API connection impossible: {e}")

    def search_read(self, entity, cond=None, fields=None, limit=0, offset=0, order="id ASC"):
        fields_and_context = {
            "fields": fields if fields else {},
            "context": {"lang": "fr_FR", "tz": "Europe/Paris"},
            "limit": limit,
            "offset": offset,
            "order": order,
        }

        return self.models.execute_kw(
            ODOO_DB,
            self.uid,
            ODOO_PASSWORD,
            entity,
            "search_read",
            [cond if cond else []],
            fields_and_context,
        )

    def authenticate(self, login, password):
        return self.common.authenticate(ODOO_DB, login, password, {})

    def create(self, entity, fields):
        return self.models.execute_kw(
            ODOO_DB,
            self.uid,
            ODOO_PASSWORD,
            entity,
            "create",
            [fields],
        )

    def execute(self, entity, method, ids, params=None):
        if params is None:
            params = {}
        return self.models.execute_kw(
            ODOO_DB,
            self.uid,
            ODOO_PASSWORD,
            entity,
            method,
            [ids],
            params,
        )


@blueprint.route("/api/products", methods=["GET"])
@jwt_required()
def products():
    _products = OdooAPI().search_read(
        "product.product",
        cond=[
            ["active", "=", True],
        ],
        fields=[
            "barcode",
            "id",
            "uom_id",
            "name",
            "qty_available",
        ],
    )
    return jsonify(_products)


@blueprint.route("/api/losses", methods=["POST"])
@jwt_required()
def register_losses():
    losses = request.json
    losses_by_type = {}
    for loss in losses:
        loss_type = loss["lossType"]
        if loss_type not in losses_by_type:
            losses_by_type[loss_type] = []
        losses_by_type[loss_type].append(loss)

    records = []
    api = OdooAPI()
    user = get_jwt_identity()
    record_by = f"{user.get('name')} {user.get('lastname')}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for loss_type, losses in losses_by_type.items():
        fields = {
            "company_id": COMPANY_ID,
            "location_id": STOCK_LOC_ID,
            "move_lines": [],
            "pack_operation_ids": [],
        }
        if loss_type == "loss":
            fields["name"] = f"[{now}] Pertes ({record_by})"
            fields["picking_type_id"] = LOSS_ID
            fields["location_dest_id"] = LOSS_LOC_ID
        elif loss_type == "autoconso":
            fields["name"] = f"[{now}] Autoconsommation ({record_by})"
            fields["picking_type_id"] = AUTO_CONSUMPTION_ID
            fields["location_dest_id"] = AUTO_CONSUMPTION_LOC_ID
        elif loss_type == "hygiene":
            fields["name"] = f"[{now}] Autoconsommation pour hygiène ({record_by})"
            fields["picking_type_id"] = HYGIENE_ID
            fields["location_dest_id"] = HYGIENE_LOC_ID
        else:
            logging.error(f"Type de mouvement incorrect {loss_type}")
            continue
        for loss in losses:
            product = loss["product"]
            quantity = f"{float(loss['quantity']):.2f}"
            fields["move_lines"].append(
                [
                    0,
                    False,
                    {
                        "date_expected": now,
                        "product_id": product["id"],
                        "name": product["name"],
                        "product_uom": product["uom_id"][0],
                        "product_uom_qty": quantity,
                        "picking_type_id": fields["picking_type_id"],
                        "location_id": STOCK_LOC_ID,
                        "location_dest_id": fields["location_dest_id"],
                        "state": "draft",
                        "scrapped": False,
                    },
                ]
            )
            fields["pack_operation_ids"].append(
                [
                    0,
                    False,
                    {
                        "product_id": product["id"],
                        "name": product["name"],
                        "product_uom_id": product["uom_id"][0],
                        "product_qty": quantity,
                        "qty_done": quantity,
                        "location_id": STOCK_LOC_ID,
                        "location_dest_id": fields["location_dest_id"],
                        "state": "done",
                        "fresh_record": False,
                    },
                ]
            )
        try:
            picking = api.create("stock.picking", fields)
            if picking:
                records.append(picking)
                # Set stock.picking done
                api.execute("stock.picking", "action_done", [picking])

                # Generate accounting writings for this picking
                api.execute("stock.picking", "generate_expense_entry", picking)
        except Exception as e:
            logging.error(str(e))

    return jsonify(records)
