from service.api.api import app
from service.knowledge_graph.dao.BaseNodesDao import BaseNodeDao
from service.knowledge_graph.dao.AssetNodesDao import AssetsDao

BASE_NODE_DAO: BaseNodeDao = BaseNodeDao.instance()


@app.patch("/node_position")
def update_node_position(iri: str, pos_x: float, pos_y: float):
    return BASE_NODE_DAO.update_node_position(iri=iri, new_pos_x=pos_x, new_pos_y=pos_y)
