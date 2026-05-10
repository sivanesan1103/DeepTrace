from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import uuid

from app.models import (
    ReportGenerateRequest,
    ReportStatusResponse,
    ReportStatus,
    ExportFormat,
)
from app.tasks.report_tasks import generate_report_task
from app.core.storage import storage_client
from app.core.minio_client import upload_report, get_report

router = APIRouter()


@router.post("/generate", response_model=ReportStatusResponse)
async def generate_report(request: ReportGenerateRequest):
    task_id = str(uuid.uuid4())
    
    task = generate_report_task.delay(
        task_id=task_id,
        investigation_id=request.investigation_id,
        template=request.template,
        options=request.options.model_dump(),
    )
    
    return ReportStatusResponse(
        task_id=task_id,
        status=ReportStatus.PENDING,
        progress=0,
    )


@router.get("/status/{task_id}", response_model=ReportStatusResponse)
async def get_report_status(task_id: str):
    from app.core.celery_app import celery_app
    
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.state == "PENDING":
        return ReportStatusResponse(
            task_id=task_id,
            status=ReportStatus.PENDING,
            progress=0,
        )
    elif task_result.state == "PROCESSING":
        return ReportStatusResponse(
            task_id=task_id,
            status=ReportStatus.PROCESSING,
            progress=task_result.info.get("progress", 0) if task_result.info else 0,
        )
    elif task_result.state == "SUCCESS":
        result = task_result.result or {}
        return ReportStatusResponse(
            task_id=task_id,
            status=ReportStatus.COMPLETED,
            progress=100,
            result_url=result.get("url"),
        )
    elif task_result.state == "FAILURE":
        return ReportStatusResponse(
            task_id=task_id,
            status=ReportStatus.FAILED,
            error=str(task_result.info),
        )
    else:
        return ReportStatusResponse(
            task_id=task_id,
            status=ReportStatus.PENDING,
            progress=0,
        )


@router.get("/download/{task_id}")
async def download_report(task_id: str, format: Optional[ExportFormat] = None):
    report_path = await get_report(task_id)
    
    if not report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if format and format != ExportFormat.PDF:
        ext = format.value
    else:
        ext = "pdf"
    
    return FileResponse(
        path=report_path,
        media_type="application/pdf" if ext == "pdf" else "application/json",
        filename=f"report-{task_id}.{ext}",
    )