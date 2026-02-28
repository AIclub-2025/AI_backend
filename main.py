from fastapi import FastAPI, Request, Response
from api import praise_report, campus_news
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# 处理跨域请求和 Private Network Access
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    # 获取请求的 Origin，如果没有则默认为 *
    origin = request.headers.get("Origin", "*")
    
    # 处理预检请求 (OPTIONS)
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "3600"
        
        # 处理 Private Network Access (PNA)
        if request.headers.get("Access-Control-Request-Private-Network") == "true":
            response.headers["Access-Control-Allow-Private-Network"] = "true"
            
        return response

    # 处理正常请求
    response = await call_next(request)
    
    # 添加 CORS 头
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    # 处理 Private Network Access (PNA)
    if request.headers.get("Access-Control-Request-Private-Network") == "true":
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        
    return response

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(praise_report.router)
app.include_router(campus_news.router, prefix="/campus_news", tags=["campus_news"])