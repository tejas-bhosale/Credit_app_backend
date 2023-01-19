from __future__ import unicode_literals
from frappe import _

def get_data():

    return [
        {
            "label": "Credit App",
            "icon": "octicon octicon-briefcase",
            "items": [
                {
                    "type": "doctype",
                    "name": "credit_app",
                    "label": _("Credit App"),
                },
                {
					"type": "doctype",
					"name": "test",
					"description": _("test")
				},
                 {
					"type": "doctype",
					"name": "Users",
					"description": _("Users")
				},
                {
					"type": "doctype",
					"name": "Transactions",
					"description": _("Transactions")
				}
            ]
        }
    ]