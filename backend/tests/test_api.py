from tests.conftest import login


def test_login_lists_organizations(client):
    _, data = login(client, "ravi@consult.test")
    names = {o["org_name"] for o in data["organizations"]}
    assert names == {"Northwind Logistics", "Bluepeak Retail"}


def test_cannot_select_org_without_membership(client):
    headers, _ = login(client, "asha@northwind.test", "Northwind Logistics")
    r = client.post("/auth/select-org", json={"org_id": 2}, headers=headers)
    assert r.status_code == 403


def test_can_select_own_org(client):
    headers, data = login(client, "ravi@consult.test")
    org_id = data["organizations"][0]["org_id"]
    r = client.post("/auth/select-org", json={"org_id": org_id}, headers=headers)
    assert r.status_code == 200
    assert r.json()["org_id"] == org_id


def test_employee_sees_questions(client):
    headers, _ = login(client, "priya@northwind.test", "Northwind Logistics")
    r = client.get("/diagnostic/questions", headers=headers)
    assert r.status_code == 200
    assert any(q["id"] == "sup-drafts" for q in r.json())


def test_admin_dashboard(client):
    headers, data = login(client, "asha@northwind.test", "Northwind Logistics")
    org_id = data["organizations"][0]["org_id"]
    r = client.get(f"/dashboard?org_id={org_id}", headers=headers)
    assert r.status_code == 200
    assert len(r.json()["departments"]) == 4


def test_admin_cannot_see_other_org(client):
    headers, _ = login(client, "asha@northwind.test", "Northwind Logistics")
    # Asha is admin of Northwind (org 1); org 2 is Bluepeak
    r = client.get("/dashboard?org_id=2", headers=headers)
    assert r.status_code == 403


def test_resubmitting_replaces_previous_answers(client):
    headers, _ = login(client, "priya@northwind.test", "Northwind Logistics")
    option = client.get("/diagnostic/questions", headers=headers).json()[0]["options"][0]
    body = {"answers": [{"question_id": "common-freq", "answer": option}]}
    admin, data = login(client, "asha@northwind.test", "Northwind Logistics")
    dash = f"/dashboard?org_id={data['organizations'][0]['org_id']}"

    client.post("/diagnostic/submit", json=body, headers=headers)
    once = client.get(dash, headers=admin).json()
    client.post("/diagnostic/submit", json=body, headers=headers)
    twice = client.get(dash, headers=admin).json()
    assert once == twice
