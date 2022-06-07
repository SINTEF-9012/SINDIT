import fastapi

"""
Fast API
Separated from service.py to avoid circular dependencies with endpoint files importing the "app" instance. 
"""

app = fastapi.FastAPI()
