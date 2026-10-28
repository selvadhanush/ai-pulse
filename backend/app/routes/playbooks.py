from fastapi import APIRouter, Depends, HTTPException

from .. import models
from ..auth import current_membership
from ..services.playbooks import executive_card

router = APIRouter(prefix="/playbooks", tags=["playbooks"])


@router.get("/{risk}")
def get_playbook(risk: str, m: models.Membership = Depends(current_membership)):
    if m.role != "admin":
        raise HTTPException(403, "Admins only")
    card = executive_card(risk)
    if card is None:
        raise HTTPException(404, "No playbook for this risk")
    return card
