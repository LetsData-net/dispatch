"""
.. module: dispatch.tag.scheduled
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging

from typing import NoReturn

from dispatch.database.core import SessionLocal
from dispatch.decorators import scheduled_project_task
from dispatch.incident import service as incident_service
from dispatch.plugin import service as plugin_service
from dispatch.project.models import Project
from dispatch.scheduler import scheduler
from dispatch.tag import service as tag_service
from dispatch.tag.models import TagCreate
from dispatch.tag.recommender import build_model
from schedule import every

log = logging.getLogger(__name__)


@scheduler.add(every(1).hour, name="tag-sync")
@scheduled_project_task
def sync_tags(db_session: SessionLocal, project: Project) -> NoReturn:
    """Syncs tags from external sources."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session,
        project_id=project.id,
        plugin_type="tag",
    )

    if not plugin:
        log.warning(
            f"Tags not synced using external sources. No tag plugin enabled. Project: {project.name}. Organization: {project.organization.name}"
        )
        return

    log.debug(f"Fetching tags using {plugin.plugin.slug} plugin...")
    for t in plugin.instance.get():
        log.debug(f"Adding tag {t}...")

        # we always use the plugin project when syncing
        t["tag_type"].update({"project": project})
        tag_in = TagCreate(**t, project=project)
        tag_service.get_or_create(db_session=db_session, tag_in=tag_in)


@scheduler.add(every(1).hour, name="tag-model-builder")
@scheduled_project_task
def build_tag_models(db_session: SessionLocal, project: Project) -> NoReturn:
    """Builds the intensive tag recommendation models."""
    # incident model
    incidents = incident_service.get_all(db_session=db_session, project_id=project.id).all()
    log.debug("Starting to build the incident/tag model for ...")
    build_model(incidents, project.organization.slug, project.slug, "incident")
    log.debug("Successfully built the incident/tag model.")
