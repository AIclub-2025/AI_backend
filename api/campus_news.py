from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

router = APIRouter()

# 数据模型
class CampusNews(BaseModel):
    id: Optional[int] = None
    title: str
    summary: str
    create_time: Optional[str] = None

class CampusNewsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[List[CampusNews]] = None

# 数据文件路径
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "campus_news.json")

# 确保数据文件存在
def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)

# 读取数据
def read_news():
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# 写入数据
def write_news(news_list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(news_list, ensure_ascii=False, indent=4, fp=f)

# 获取所有新闻
@router.get("/list", response_model=CampusNewsResponse)
async def get_news_list():
    news_list = read_news()
    return {
        "success": True,
        "message": "获取新闻列表成功",
        "data": news_list
    }

# 添加新闻
@router.post("/add", response_model=CampusNewsResponse)
async def add_news(news: CampusNews):
    # 验证摘要长度
    if len(news.summary) > 100:
        raise HTTPException(status_code=400, detail="新闻摘要不能超过100字")
    
    news_list = read_news()
    
    # 生成ID
    new_id = 1
    if news_list:
        new_id = max(item["id"] for item in news_list) + 1
    
    # 添加时间戳
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 创建新闻对象
    news_dict = {
        "id": new_id,
        "title": news.title,
        "summary": news.summary,
        "create_time": current_time
    }
    
    # 添加到列表
    news_list.append(news_dict)
    write_news(news_list)
    
    return {
        "success": True,
        "message": "添加新闻成功",
        "data": [news_dict]
    }

# 删除新闻
@router.delete("/delete/{news_id}", response_model=CampusNewsResponse)
async def delete_news(news_id: int):
    news_list = read_news()
    
    # 查找并删除
    for i, news in enumerate(news_list):
        if news["id"] == news_id:
            del news_list[i]
            write_news(news_list)
            return {
                "success": True,
                "message": "删除新闻成功",
                "data": None
            }
    
    raise HTTPException(status_code=404, detail="未找到指定ID的新闻")

# 编辑新闻
@router.put("/edit/{news_id}", response_model=CampusNewsResponse)
async def edit_news(news_id: int, news: CampusNews):
    ensure_data_file()
    news_list = read_news()
    
    # 查找要编辑的新闻
    for i, existing_news in enumerate(news_list):
        if existing_news["id"] == news_id:
            # 更新新闻信息，保留原有的ID和创建时间
            news_list[i] = {
                "id": news_id,
                "title": news.title,
                "summary": news.summary,
                "create_time": existing_news["create_time"]  # 保留原创建时间
            }
            write_news(news_list)
            return {
                "success": True,
                "message": "编辑新闻成功",
                "data": [news_list[i]]
            }
    
    raise HTTPException(status_code=404, detail="未找到指定ID的新闻")

# 根据标题模糊搜索新闻
@router.get("/search", response_model=CampusNewsResponse)
async def search_news(title: str):
    ensure_data_file()
    news_list = read_news()
    
    # 模糊搜索：标题包含搜索关键词的新闻
    filtered_news = [
        news for news in news_list 
        if title.lower() in news["title"].lower()
    ]
    
    return {
        "success": True,
        "message": f"搜索到 {len(filtered_news)} 条新闻",
        "data": filtered_news
    }