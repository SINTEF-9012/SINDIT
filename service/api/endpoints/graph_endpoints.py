from service.api.api import app
from service.knowledge_graph.dao.BaseNodeDao import BaseNodeDao
from service.knowledge_graph.dao.MachinesDao import MachinesDao

MACHINES_DAO: MachinesDao = MachinesDao.instance()
BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()

@app.get("/graph/machines_deep")
def get_machines_deep():
    return MACHINES_DAO.get_machines_deep_json()

@app.patch("/graph/node_position")
def update_node_position(iri: str, pos_x: float, pos_y: float):
    return BASE_NODE_DAO.update_node_position(iri=iri, new_pos_x=pos_x, new_pos_y=pos_y)

# TODO: restructure api endpoints