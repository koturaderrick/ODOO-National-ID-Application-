import requests

BASE_URL = "http://192.168.40.129:8069"
API_KEY = "d3cd32d074a4878b953643f1c48a402917f42984"
headers = {
    "Authorization": f"bearer {API_KEY}",
    "X-Odoo-Database": "odoobd",
    "User-Agent": "mysoftware " + requests.utils.default_user_agent(),
}

res_search = requests.post(
    f"{BASE_URL}/res.partner/search",
    headers=headers,
    json={
        "context": {"lang": "en_US"},
        "domain": [
            ("name", "ilike", "%deco%"),
            ("is_company", "=", True),
        ],
    },
)
res_search.raise_for_status()
ids = res_search.json()

res_read = requests.post(
    f"{BASE_URL}/res.partner/read",
    headers=headers,
    json={
        "ids": ids,
        "context": {"lang": "en_US"},
        "fields": ["name"],
    }
)
res_read.raise_for_status()
names = res_read.json()
print(names)