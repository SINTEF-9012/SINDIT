from service.api.api import app
from service.knowledge_graph.dao.MachinesDao import MachinesDao

MACHINES_DAO: MachinesDao = MachinesDao.instance()

@app.get("/graph/machines_deep")
def get_machines_deep():
    return MACHINES_DAO.get_machines_deep_json()
