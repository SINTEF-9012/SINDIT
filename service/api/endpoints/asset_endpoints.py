from service.api.api import app
from service.knowledge_graph.dao.AssetNodesDao import AssetsDao

ASSETS_DAO: AssetsDao = AssetsDao.instance()


@app.get("/assets")
def get_assets_deep(deep: bool = True):
    return ASSETS_DAO.get_assets_deep_json()
