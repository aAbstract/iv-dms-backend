# autopep8: off
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from models.httpio import JsonResponse
import lib.log as log_man
import database.mongo_driver as mdb
from dotenv import load_dotenv
load_dotenv()

# routes
from routes import auth_api
from routes import manuals_api
from routes import activity_api
from routes import regulations_api
from routes import llm_api
from routes import ai_tasks_api
from routes import attachments_api
from routes import flow_report_api
# autopep8: on


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mdb.mongodb_connect()
    yield
    # clean up resources here


server = FastAPI(
    title=os.environ['SERVER_NAME'],
    description='Added Main Branch Database',
    version="0.37.1",
    lifespan=lifespan,
)
server.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)
server.include_router(auth_api.router)
server.include_router(manuals_api.router)
server.include_router(activity_api.router)
server.include_router(regulations_api.router)
server.include_router(llm_api.router)
server.include_router(ai_tasks_api.router)
server.include_router(attachments_api.router)
server.include_router(flow_report_api.router)


@server.get('/api/test')
async def get_test():
    """Test route to check if server is online."""
    await log_man.add_log('main.get_test', 'DEBUG', 'received get test request')
    return JsonResponse(msg='server online')


# mount static files server
server.mount('/', StaticFiles(directory='public', html=True), name='public')
# TODO-LATER: add fs security (when adding airlines user)


if __name__ == '__main__':
    uvicorn.run(server, host='0.0.0.0', port=int(os.environ['SERVER_PORT']))
