from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import TenantAccessChecker, get_current_active_user
from app.database import get_db
from app.models.organization import Membership, Organization
from app.models.user import User, UserRole
from app.schemas.auth import (
    AddMemberRequest,
    MembershipResponse,
    OrganizationCreate,
    OrganizationResponse,
)

router = APIRouter()


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_in: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a new organization and assign current user as OWNER."""
    slug = org_in.name.lower().replace(" ", "-") + f"-{current_user.id[:6]}"
    existing_org = db.query(Organization).filter(Organization.slug == slug).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An organization with a similar name already exists.",
        )

    org = Organization(name=org_in.name, slug=slug)
    db.add(org)
    db.flush()

    membership = Membership(
        user_id=current_user.id,
        organization_id=org.id,
        role=UserRole.OWNER,
    )
    db.add(membership)
    db.commit()
    db.refresh(org)
    return org


@router.get("/", response_model=List[MembershipResponse])
def get_user_organizations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Get all organizations the current user belongs to with their roles."""
    memberships = (
        db.query(Membership)
        .filter(Membership.user_id == current_user.id)
        .all()
    )
    result = []
    for m in memberships:
        result.append(
            MembershipResponse(
                id=m.id,
                organization_id=m.organization_id,
                organization_name=m.organization.name,
                role=m.role,
                created_at=m.created_at,
            )
        )
    return result


@router.post("/{org_id}/members", response_model=MembershipResponse)
def add_organization_member(
    org_id: str,
    member_in: AddMemberRequest,
    db: Session = Depends(get_db),
    membership: Membership = Depends(TenantAccessChecker(allowed_roles=[UserRole.OWNER])),
) -> Any:
    """Add a new member to an organization (Requires OWNER role)."""
    target_user = db.query(User).filter(User.email == member_in.user_email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user with given email not found",
        )

    existing_membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == target_user.id,
            Membership.organization_id == org_id,
        )
        .first()
    )
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization",
        )

    new_membership = Membership(
        user_id=target_user.id,
        organization_id=org_id,
        role=member_in.role,
    )
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    return MembershipResponse(
        id=new_membership.id,
        organization_id=new_membership.organization_id,
        organization_name=new_membership.organization.name,
        role=new_membership.role,
        created_at=new_membership.created_at,
    )
