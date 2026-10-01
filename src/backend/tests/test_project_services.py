"""Tests for project service helpers."""

from unittest.mock import AsyncMock

from app.projects import project_services


async def test_save_data_extract_explicitly_clears_existing_task_areas(monkeypatch):
    """Replacing an extract must return the project to an unsplit state."""
    db = AsyncMock()
    update_mock = AsyncMock()
    check_crs_mock = AsyncMock()

    monkeypatch.setattr(project_services.DbProject, "update", update_mock)
    monkeypatch.setattr(project_services, "check_crs", check_crs_mock)

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {"type": "Point", "coordinates": [0, 0]},
            }
        ],
    }

    count = await project_services.save_data_extract(
        db=db,
        project_id=42,
        geojson_data=geojson,
    )

    assert count == 1
    check_crs_mock.assert_awaited_once_with(geojson)
    update_mock.assert_awaited_once()
    args, kwargs = update_mock.await_args
    assert args[0] is db
    assert args[1] == 42
    assert args[2].data_extract_geojson == geojson
    assert kwargs["fields_to_null"] == {"task_areas_geojson"}
    db.commit.assert_awaited_once()
