import json
from datetime import date

from src.services.cloud_report_service import CLOUD_REPORT_STOCK_CODE, CloudReportService


def test_cloud_report_service_reads_local_index_and_markdown(tmp_path):
    cloud_dir = tmp_path / "cloud_reports"
    cloud_dir.mkdir()
    report_path = cloud_dir / "report_20260507.md"
    report_path.write_text("# Daily report\n\nhello", encoding="utf-8")
    (cloud_dir / "index.json").write_text(
        json.dumps({
            "reports": [{
                "date": "2026-05-07",
                "date_compact": "20260507",
                "title": "2026-05-07 每日股票分析日报",
                "file": "cloud_reports/report_20260507.md",
                "created_at": "2026-05-07T20:20:00+08:00",
                "run_id": "25494683143",
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )

    service = CloudReportService(
        repo_root=tmp_path,
        repository="owner/repo",
        branch="main",
        remote_enabled=False,
    )

    items = service.list_history_items(
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 31),
    )

    assert len(items) == 1
    assert items[0]["id"] == -20260507
    assert items[0]["stock_code"] == CLOUD_REPORT_STOCK_CODE
    assert items[0]["query_id"] == "cloud-report-20260507"

    detail = service.get_detail("-20260507")
    assert detail is not None
    assert detail["stock_code"] == CLOUD_REPORT_STOCK_CODE
    assert detail["sentiment_score"] == 50
    assert service.get_markdown_report("cloud-report-20260507") == "# Daily report\n\nhello"


def test_cloud_report_service_filters_by_date_and_stock_code(tmp_path):
    cloud_dir = tmp_path / "cloud_reports"
    cloud_dir.mkdir()
    (cloud_dir / "index.json").write_text(
        json.dumps({
            "reports": [{
                "date_compact": "20260507",
                "file": "cloud_reports/report_20260507.md",
            }]
        }),
        encoding="utf-8",
    )
    service = CloudReportService(
        repo_root=tmp_path,
        repository="owner/repo",
        branch="main",
        remote_enabled=False,
    )

    assert service.list_history_items(stock_code="600519") == []
    assert service.list_history_items(start_date=date(2026, 5, 8)) == []
    assert service.is_cloud_record_id("-20260507")
    assert service.is_cloud_record_id("cloud-report-20260507")
    assert not service.is_cloud_record_id("1")
