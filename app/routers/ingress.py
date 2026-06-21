from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.core.groups import list_groups, get_groups_with_entities, create_group, add_entity_to_group
from app.core.ha_client import get_states
from app.db.database import get_session

router = APIRouter()

class CreateGroupRequest(BaseModel):
    name: str

class AddEntityRequest(BaseModel):
    entity_id: str

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

                const heading = document.createElement('h3');
                heading.textContent = group.name;
                groupDiv.appendChild(heading);

                const entityList = document.createElement('ul');
                entityIds.forEach((entityId) => {
                    const li = document.createElement('li');
                    li.textContent = entityId;
                    entityList.appendChild(li);
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
