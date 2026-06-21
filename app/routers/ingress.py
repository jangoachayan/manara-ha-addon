from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.core.groups import (
    list_groups,
    get_groups_with_entities,
    create_group,
    add_entity_to_group,
    remove_entity_from_group,
    delete_group,
    update_group_name,
    reorder_group_entities,
)
from app.core.ha_client import get_states
from app.db.database import get_session

router = APIRouter()

class CreateGroupRequest(BaseModel):
    name: str

class AddEntityRequest(BaseModel):
    entity_id: str

class UpdateGroupRequest(BaseModel):
    name: str

class ReorderRequest(BaseModel):
    entity_id_order: list[str]

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manara Backend</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 480px;
            box-sizing: border-box;
        }
        header {
            background-color: #5a2f82;
            color: white;
            text-align: center;
            padding: 16px 0;
        }
        section {
            padding: 0 20px 20px;
        }
        .status a {
            display: block;
            margin-bottom: 5px;
            color: #5a2f82;
            text-decoration: none;
        }
        .create-group {
            margin-bottom: 16px;
        }
        .group-card {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
        }
        .group-card h3 {
            margin: 0 0 8px;
            color: #5a2f82;
        }
        .group-card ul {
            margin: 0 0 8px;
            padding-left: 20px;
        }
        .group-card li {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
        }
        .group-card li span {
            flex: 1;
        }
        .group-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
        }
        .group-header h3 {
            margin: 0;
            flex: 1;
        }
        .entity-search {
            display: block;
            margin-bottom: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>Manara Backend</header>
        <section class="pair-device">
            <h2>Pair a Device</h2>
            <p>Scan this QR code with the Manara app to pair your device. The code expires in 10 minutes.</p>
            <a href="auth/qr" target="_blank" rel="noopener"><button type="button">Show QR Code</button></a>
            <button onclick="window.location.reload()">Refresh</button>
        </section>
        <section class="status">
            <h2>Status</h2>
            <a href="health" target="_blank">Health</a>
            <a href="docs" target="_blank">API Docs</a>
        </section>
        <section class="manage-groups">
            <h2>Manage Groups</h2>
            <div class="create-group">
                <input type="text" id="new-group-name" placeholder="Group name">
                <button onclick="createGroup()">Create Group</button>
            </div>
            <div id="groups-list">Loading groups...</div>
        </section>
    </div>
    <script>
        let allEntities = [];

        async function loadGroupsData() {
            const response = await fetch('admin/groups/data');
            const data = await response.json();
            allEntities = data.all_entities;
            renderGroups(data.groups, data.memberships);
        }

        function renderGroups(groups, memberships) {
            const container = document.getElementById('groups-list');
            container.innerHTML = '';

            if (groups.length === 0) {
                container.textContent = 'No groups yet.';
                return;
            }

            groups.forEach((group) => {
                const entityIds = memberships[group.name] || [];

                const groupDiv = document.createElement('div');
                groupDiv.className = 'group-card';

                const headerDiv = document.createElement('div');
                headerDiv.className = 'group-header';

                const heading = document.createElement('h3');
                heading.textContent = group.name;
                headerDiv.appendChild(heading);

                const renameButton = document.createElement('button');
                renameButton.type = 'button';
                renameButton.textContent = 'Rename';
                renameButton.onclick = () => startRenameGroup(group.id, headerDiv, heading, renameButton);
                headerDiv.appendChild(renameButton);

                const deleteButton = document.createElement('button');
                deleteButton.type = 'button';
                deleteButton.textContent = 'Delete';
                deleteButton.onclick = () => handleDeleteGroupClick(group.id, deleteButton);
                headerDiv.appendChild(deleteButton);

                groupDiv.appendChild(headerDiv);

                const entityList = document.createElement('ul');
                entityIds.forEach((entityId, index) => {
                    entityList.appendChild(buildEntityListItem(group.id, entityId, entityIds, index));
                });
                groupDiv.appendChild(entityList);

                const select = document.createElement('select');
                allEntities.forEach((entityId) => {
                    const option = document.createElement('option');
                    option.value = entityId;
                    option.textContent = entityId;
                    select.appendChild(option);
                });

                const searchInput = document.createElement('input');
                searchInput.type = 'text';
                searchInput.id = `entity-search-${group.id}`;
                searchInput.className = 'entity-search';
                searchInput.placeholder = 'Search entities...';
                searchInput.oninput = () => filterEntityOptions(searchInput.value, select);
                groupDiv.appendChild(searchInput);
                groupDiv.appendChild(select);

                const addButton = document.createElement('button');
                addButton.type = 'button';
                addButton.textContent = 'Add Entity';
                addButton.onclick = () => addEntityToGroup(group.id, select.value);
                groupDiv.appendChild(addButton);

                container.appendChild(groupDiv);
            });
        }

        function buildEntityListItem(groupId, entityId, entityIds, index) {
            const li = document.createElement('li');

            const label = document.createElement('span');
            label.textContent = entityId;
            li.appendChild(label);

            const upButton = document.createElement('button');
            upButton.type = 'button';
            upButton.textContent = '↑';
            if (index === 0) {
                upButton.style.display = 'none';
            } else {
                upButton.onclick = () => moveEntity(groupId, entityIds, index, index - 1);
            }
            li.appendChild(upButton);

            const downButton = document.createElement('button');
            downButton.type = 'button';
            downButton.textContent = '↓';
            if (index === entityIds.length - 1) {
                downButton.style.display = 'none';
            } else {
                downButton.onclick = () => moveEntity(groupId, entityIds, index, index + 1);
            }
            li.appendChild(downButton);

            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.textContent = 'Remove';
            removeButton.onclick = () => removeEntityFromGroup(groupId, entityId);
            li.appendChild(removeButton);

            return li;
        }

        function handleDeleteGroupClick(groupId, button) {
            if (button.dataset.confirming === 'true') {
                clearTimeout(Number(button.dataset.timeoutId));
                deleteGroup(groupId);
                return;
            }

            const originalText = button.textContent;
            button.dataset.confirming = 'true';
            button.textContent = 'Confirm Delete?';
            const timeoutId = setTimeout(() => {
                button.textContent = originalText;
                button.dataset.confirming = 'false';
            }, 3000);
            button.dataset.timeoutId = String(timeoutId);
        }

        async function deleteGroup(groupId) {
            await fetch(`admin/groups/${groupId}`, { method: 'DELETE' });
            loadGroupsData();
        }

        function startRenameGroup(groupId, headerDiv, heading, renameButton) {
            const input = document.createElement('input');
            input.type = 'text';
            input.value = heading.textContent;

            const saveButton = document.createElement('button');
            saveButton.type = 'button';
            saveButton.textContent = 'Save';
            saveButton.onclick = () => saveGroupName(groupId, input.value.trim());

            headerDiv.replaceChild(input, heading);
            renameButton.style.display = 'none';
            headerDiv.appendChild(saveButton);
            input.focus();
        }

        async function saveGroupName(groupId, newName) {
            if (!newName) return;

            await fetch(`admin/groups/${groupId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: newName }),
            });

            loadGroupsData();
        }

        async function removeEntityFromGroup(groupId, entityId) {
            await fetch(`admin/groups/${groupId}/entities/${entityId}`, { method: 'DELETE' });
            loadGroupsData();
        }

        async function moveEntity(groupId, entityIds, fromIndex, toIndex) {
            const newOrder = entityIds.slice();
            const [moved] = newOrder.splice(fromIndex, 1);
            newOrder.splice(toIndex, 0, moved);

            await fetch(`admin/groups/${groupId}/reorder`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ entity_id_order: newOrder }),
            });

            loadGroupsData();
        }

        function filterEntityOptions(searchTerm, selectElement) {
            const term = searchTerm.toLowerCase();
            Array.from(selectElement.options).forEach((option) => {
                const matches = option.value.toLowerCase().includes(term)
                    || option.textContent.toLowerCase().includes(term);
                option.style.display = matches ? '' : 'none';
            });
        }

        async function createGroup() {
            const input = document.getElementById('new-group-name');
            const name = input.value.trim();
            if (!name) return;

            await fetch('admin/groups', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name }),
            });

            input.value = '';
            loadGroupsData();
        }

        async function addEntityToGroup(groupId, entityId) {
            if (!entityId) return;

            await fetch(`admin/groups/${groupId}/entities`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ entity_id: entityId }),
            });

            loadGroupsData();
        }

        loadGroupsData();
    </script>
</body>
</html>
"""


@router.get("/")
async def ingress_ui() -> HTMLResponse:
    return HTMLResponse(content=HTML_CONTENT, status_code=200)


@router.get('/admin/groups/data')
async def get_groups_data(session: Session = Depends(get_session)) -> dict:
    groups = list_groups(session)
    memberships = get_groups_with_entities(session)
    states = await get_states()
    return {
        'groups': [{'id': group.id, 'name': group.name} for group in groups],
        'memberships': memberships,
        'all_entities': [state['entity_id'] for state in states],
    }


@router.post('/admin/groups')
async def create_group_endpoint(
    request: CreateGroupRequest,
    session: Session = Depends(get_session),
) -> dict:
    group = create_group(session, name=request.name)
    return {'id': group.id, 'name': group.name}


@router.post('/admin/groups/{group_id}/entities')
async def add_entity_to_group_endpoint(
    group_id: int,
    request: AddEntityRequest,
    session: Session = Depends(get_session),
) -> dict:
    membership = add_entity_to_group(session, group_id, request.entity_id)
    return {'id': membership.id, 'group_id': membership.group_id, 'entity_id': membership.entity_id}


@router.delete('/admin/groups/{group_id}')
async def delete_group_endpoint(
    group_id: int,
    session: Session = Depends(get_session),
) -> dict:
    delete_group(session, group_id)
    return {'status': 'deleted'}


@router.patch('/admin/groups/{group_id}')
async def update_group_name_endpoint(
    group_id: int,
    request: UpdateGroupRequest,
    session: Session = Depends(get_session),
) -> dict:
    try:
        group = update_group_name(session, group_id, request.name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail='Group not found') from e
    return {'id': group.id, 'name': group.name}


@router.delete('/admin/groups/{group_id}/entities/{entity_id}')
async def remove_entity_from_group_endpoint(
    group_id: int,
    entity_id: str,
    session: Session = Depends(get_session),
) -> dict:
    remove_entity_from_group(session, group_id, entity_id)
    return {'status': 'removed'}


@router.post('/admin/groups/{group_id}/reorder')
async def reorder_group_entities_endpoint(
    group_id: int,
    request: ReorderRequest,
    session: Session = Depends(get_session),
) -> dict:
    reorder_group_entities(session, group_id, request.entity_id_order)
    return {'status': 'reordered'}
