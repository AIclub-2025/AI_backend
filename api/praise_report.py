from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
import tinydb
from datetime import datetime
from typing import List, Optional

db = tinydb.TinyDB("./database/db.json")
praise_table = db.table("praise")
report_table = db.table("report")

router = APIRouter(
    prefix='/praise_report',
    tags=['praise_report']
)

class PraiseReportBase(BaseModel):
    class_name: str
    student_name: str
    content: str
    date: str = datetime.now().strftime("%Y-%m-%d")
    
class PraiseReport(PraiseReportBase):
    id: str

# 添加表扬
@router.post("/praise")
async def add_praise(praise: PraiseReportBase):
    record_id = str(datetime.now().timestamp())
    praise_table.insert({"id": record_id, "class_name": praise.class_name, 
                         "student_name": praise.student_name, 
                         "content": praise.content, 
                         "date": praise.date})
    return {"code": 0, "message": "添加表扬成功", "id": record_id}

# 添加通报
@router.post("/report")
async def add_report(report: PraiseReportBase):
    record_id = str(datetime.now().timestamp())
    report_table.insert({"id": record_id, "class_name": report.class_name, 
                         "student_name": report.student_name, 
                         "content": report.content, 
                         "date": report.date})
    return {"code": 0, "message": "添加通报成功", "id": record_id}

# 获取当日表扬列表
@router.get("/praise/today")
async def get_today_praise():
    today = datetime.now().strftime("%Y-%m-%d")
    praises = praise_table.search(tinydb.Query().date == today)
    return {"code": 0, "data": praises}

# 获取当日通报列表
@router.get("/report/today")
async def get_today_report():
    today = datetime.now().strftime("%Y-%m-%d")
    reports = report_table.search(tinydb.Query().date == today)
    return {"code": 0, "data": reports}

# 获取所有表扬列表
@router.get("/praise/all")
async def get_all_praise():
    praises = praise_table.all()
    return {"code": 0, "data": praises}

# 获取所有通报列表
@router.get("/report/all")
async def get_all_report():
    reports = report_table.all()
    return {"code": 0, "data": reports}

# 删除表扬
@router.delete("/praise/{praise_id}")
async def delete_praise(praise_id: str):
    removed = praise_table.remove(tinydb.Query().id == praise_id)
    if not removed:
        raise HTTPException(status_code=404, detail="表扬记录不存在")
    return {"code": 0, "message": "删除表扬成功"}

# 删除通报
@router.delete("/report/{report_id}")
async def delete_report(report_id: str):
    removed = report_table.remove(tinydb.Query().id == report_id)
    if not removed:
        raise HTTPException(status_code=404, detail="通报记录不存在")
    return {"code": 0, "message": "删除通报成功"}

# 更新表扬
@router.put("/praise/{praise_id}")
async def update_praise(praise_id: str, praise: PraiseReportBase):
    updated = praise_table.update({"class_name": praise.class_name, 
                                  "student_name": praise.student_name, 
                                  "content": praise.content, 
                                  "date": praise.date}, 
                                  tinydb.Query().id == praise_id)
    if not updated:
        raise HTTPException(status_code=404, detail="表扬记录不存在")
    return {"code": 0, "message": "更新表扬成功"}

# 更新通报
@router.put("/report/{report_id}")
async def update_report(report_id: str, report: PraiseReportBase):
    updated = report_table.update({"class_name": report.class_name, 
                                  "student_name": report.student_name, 
                                  "content": report.content, 
                                  "date": report.date}, 
                                  tinydb.Query().id == report_id)
    if not updated:
        raise HTTPException(status_code=404, detail="通报记录不存在")
    return {"code": 0, "message": "更新通报成功"}