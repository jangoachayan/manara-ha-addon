from sqlmodel import Session, select
from app.db.models import EntityGroup, GroupMembership

def create_group(session: Session, name: str, display_order: int = 0) -> EntityGroup:
    group = EntityGroup(name=name, display_order=display_order)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group

def list_groups(session: Session) -> list[EntityGroup]:
    statement = select(EntityGroup).order_by(EntityGroup.display_order)  # type: ignore[arg-type]  # no sqlmodel mypy plugin configured, so mypy sees display_order as plain int instead of a queryable column
    result = session.execute(statement)
    return list(result.scalars().all())

def delete_group(session: Session, group_id: int) -> None:
    membership_statement = select(GroupMembership).where(GroupMembership.group_id == group_id)
    memberships = session.execute(membership_statement).scalars().all()
    for membership in memberships:
        session.delete(membership)

    group_statement = select(EntityGroup).where(EntityGroup.id == group_id)
    group = session.execute(group_statement).scalar_one_or_none()
    if group is not None:
        session.delete(group)

    session.commit()

def update_group_name(session: Session, group_id: int, new_name: str) -> EntityGroup:
    statement = select(EntityGroup).where(EntityGroup.id == group_id)
    group = session.execute(statement).scalar_one_or_none()
    if group is None:
        raise ValueError(f'EntityGroup {group_id} does not exist')
    group.name = new_name
    session.add(group)
    session.commit()
    session.refresh(group)
    return group

def add_entity_to_group(session: Session, group_id: int, entity_id: str) -> GroupMembership:
    membership = GroupMembership(group_id=group_id, entity_id=entity_id)
    session.add(membership)
    session.commit()
    session.refresh(membership)
    return membership

def remove_entity_from_group(session: Session, group_id: int, entity_id: str) -> None:
    statement = select(GroupMembership).where(
        GroupMembership.group_id == group_id,
        GroupMembership.entity_id == entity_id,
    )
    result = session.execute(statement)
    membership = result.scalar_one_or_none()
    if membership is not None:
        session.delete(membership)
        session.commit()

def reorder_group_entities(session: Session, group_id: int, entity_id_order: list[str]) -> None:
    statement = select(GroupMembership).where(GroupMembership.group_id == group_id)
    memberships_by_entity_id = {
        membership.entity_id: membership
        for membership in session.execute(statement).scalars().all()
    }

    for index, entity_id in enumerate(entity_id_order):
        membership = memberships_by_entity_id.get(entity_id)
        if membership is not None:
            membership.display_order = index
            session.add(membership)

    session.commit()

def get_groups_with_entities(session: Session) -> dict[str, list[str]]:
    groups = session.execute(
        select(EntityGroup).order_by(EntityGroup.display_order)  # type: ignore[arg-type]  # no sqlmodel mypy plugin configured, so mypy sees display_order as plain int instead of a queryable column
    ).scalars().all()
    memberships = session.execute(
        select(GroupMembership).order_by(GroupMembership.display_order)  # type: ignore[arg-type]  # no sqlmodel mypy plugin configured, so mypy sees display_order as plain int instead of a queryable column
    ).scalars().all()

    entities_by_group_id: dict[int, list[str]] = {}
    for membership in memberships:
        entities_by_group_id.setdefault(membership.group_id, []).append(membership.entity_id)

    return {
        group.name: entities_by_group_id.get(group.id, [])
        for group in groups
        if group.id is not None
    }
