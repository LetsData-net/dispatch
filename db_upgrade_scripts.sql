CREATE INDEX IF NOT EXISTS incident_name_index
  ON dispatch_organization_default.incident (name);

CREATE INDEX IF NOT EXISTS incident_reporter_id_reported_at_index
  ON dispatch_organization_default.incident (reporter_id, reported_at DESC);

CREATE INDEX IF NOT EXISTS incident_project_id_reported_at_index
  ON dispatch_organization_default.incident (project_id, reported_at DESC);

CREATE INDEX IF NOT EXISTS incident_commander_id_reported_at_index
  ON dispatch_organization_default.incident (commander_id, reported_at DESC);

CREATE INDEX IF NOT EXISTS incident_visibility_reported_at_index
  ON dispatch_organization_default.incident (visibility, reported_at DESC);

CREATE INDEX IF NOT EXISTS incident_duplicate_id_index
  ON dispatch_organization_default.incident (duplicate_id);

CREATE INDEX IF NOT EXISTS participant_incident_id_index
  ON dispatch_organization_default.participant (incident_id DESC);

CREATE INDEX IF NOT EXISTS participant_individual_contact_id_index
  ON dispatch_organization_default.participant (individual_contact_id);

CREATE INDEX IF NOT EXISTS individual_contact_email_index
  ON dispatch_organization_default.individual_contact (email);

CREATE INDEX IF NOT EXISTS participant_role_participant_id_index
  ON dispatch_organization_default.participant_role (participant_id ASC);

CREATE INDEX IF NOT EXISTS incident_cost_incident_id_created_at_index
  ON dispatch_organization_default.incident_cost (incident_id, created_at);

CREATE INDEX IF NOT EXISTS incident_type_exclude_from_metrics_idx
  ON dispatch_organization_default.incident_type (exclude_from_metrics);


