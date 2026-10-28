from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..auth import current_membership
from ..utils import maturity_level

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def org_dashboard(org_id: int, m: models.Membership = Depends(current_membership), db: Session = Depends(get_db)):
    if m.role != "admin":
        raise HTTPException(403, "Admins only")

    # Tenant check first so callers can't probe which org IDs exist
    if org_id != m.org_id:
        raise HTTPException(403, "You cannot access another organization")

    org = db.get(models.Organization, org_id)
    if not org:
        raise HTTPException(404, "Organization not found")

    members = db.query(models.Membership).filter_by(org_id=org_id).all()
    departments = []
    all_flags = {}
    for dept in org.departments:
        dept_members = [x for x in members if x.department_id == dept.id]
        employee_avgs = []  # one average per employee who completed the diagnostic
        responded = 0
        for dm in dept_members:
            rows = db.query(models.Response).filter_by(membership_id=dm.id).all()
            if rows:
                responded += 1
            scores = [r.score for r in rows if r.score is not None]
            if scores:
                employee_avgs.append(sum(scores) / len(scores))
            for r in rows:
                for f in r.flags or []:
                    all_flags[f] = all_flags.get(f, 0) + 1
        avg = sum(employee_avgs) / len(employee_avgs) if employee_avgs else None
        departments.append({
            "department": dept.name,
            "employees": len(dept_members),
            "responded": responded,
            "average_score": round(avg, 2) if avg is not None else None,
            "level": maturity_level(avg),
        })

    return {
        "organization": org.name,
        "departments": departments,
        "top_risks": sorted(all_flags.items(), key=lambda kv: -kv[1])[:5],
    }
