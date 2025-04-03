<template>
  <v-form @submit.prevent="report()" v-slot="{ isValid }" class="form-wrapper">
    <v-row class="ma-4 h-100" dense>
      <div :style="previewCollapsed ? 'width: 64%' : 'width: 34%'" class="d-flex flex-column">
        <v-card variant="outlined" class="fill-height d-flex flex-column">
          <v-card-title>Body of the alert</v-card-title>
          <v-card-text class="flex-grow-1 overflow-hidden d-flex flex-column">
            <RichTextEditor v-model="description" class="flex-grow-1" />
          </v-card-text>
        </v-card>
      </div>

      <div :style="previewCollapsed ? 'width: 4%' : 'width: 34%'" class="d-flex flex-column">
        <v-card variant="outlined" class="fill-height d-flex flex-column">
          <v-card-title class="justify-center">
            {{ !previewCollapsed ? "Preview of the alert" : "" }}
            <v-btn icon variant="text" @click="togglePreview">
              <v-icon>{{ previewCollapsed ? "mdi-eye-off-outline" : "mdi-eye-outline" }}</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text v-show="!previewCollapsed" class="overflow-auto flex-grow-1">
            <div class="preview" v-html="description" />
          </v-card-text>
        </v-card>
      </div>

      <div style="width: 23%" class="d-flex flex-column">
        <v-card variant="outlined" class="fill-height d-flex flex-column">
          <v-card-title>Details</v-card-title>
          <v-card-text class="flex-grow-1 overflow-auto">
            <v-textarea
              v-model="title"
              label="Title"
              hint="Brief title"
              clearable
              auto-grow
              rows="2"
              :rules="[rules.required]"
            />
            <project-select v-model="project" excludeDisabled />
            <incident-type-select :project="project" v-model="incident_type" />
            <incident-priority-select :project="project" v-model="incident_priority" />
            <tag-filter-auto-complete
              :project="project"
              v-model="tags"
              label="Tags"
              model="incident"
            />
            <participant-select
              v-model="local_commander"
              label="Optional: Incident Commander"
              hint="If not entered, the current on-call will be assigned."
              clearable
              :project="project"
              :rules="[only_one]"
            />
          </v-card-text>

          <v-card-actions>
            <v-btn
              color="success"
              block
              :loading="loading"
              :disabled="!isValid.value"
              type="submit"
            >
              Submit
              <template #loader>
                <v-progress-linear indeterminate color="white" />
              </template>
            </v-btn>
          </v-card-actions>
        </v-card>
      </div>
    </v-row>
  </v-form>
</template>

<script>
import { required } from "@/util/form"

import { mapActions } from "vuex"
import { mapFields } from "vuex-map-fields"
import { isNavigationFailure, NavigationFailureType } from "vue-router"

import router from "@/router"

import DocumentApi from "@/document/api"
import ProjectApi from "@/project/api"
import AuthApi from "@/auth/api"
import IncidentPrioritySelect from "@/incident/priority/IncidentPrioritySelect.vue"
import IncidentTypeSelect from "@/incident/type/IncidentTypeSelect.vue"
import ProjectSelect from "@/project/ProjectSelect.vue"
import TagFilterAutoComplete from "@/tag/TagPicker.vue"
import ParticipantSelect from "@/components/ParticipantSelect.vue"
import RichTextEditor from "@/incident/RichTextEditor/RichTextEditor.vue"

export default {
  setup() {
    return {
      rules: { required },
    }
  },
  name: "ReportSubmissionCard",

  components: {
    RichTextEditor,
    IncidentTypeSelect,
    IncidentPrioritySelect,
    ProjectSelect,
    TagFilterAutoComplete,
    ParticipantSelect,
  },

  data() {
    return {
      previewCollapsed: false,
      isSubmitted: false,
      project_faq: null,
      local_commander: null,
      only_one: (value) => {
        if (value && value.length > 1) {
          return "Only one is allowed"
        }
        return true
      },
    }
  },

  computed: {
    ...mapFields("incident", [
      "selected.incident_priority",
      "selected.incident_type",
      "selected.commander_email",
      "selected.title",
      "selected.tags",
      "selected.description",
      "selected.conversation",
      "selected.conference",
      "selected.visibility",
      "selected.storage",
      "selected.documents",
      "selected.loading",
      "selected.ticket",
      "selected.project",
      "selected.id",
      "default_project",
    ]),
    ...mapFields("auth", ["currentUser.projects"]),
  },

  methods: {
    togglePreview() {
      this.previewCollapsed = !this.previewCollapsed
    },
    getFAQ() {
      if (this.project) {
        DocumentApi.getAll({
          filter: JSON.stringify({
            and: [
              {
                field: "resource_type",
                op: "==",
                value: "dispatch-faq-reference-document",
              },
              {
                model: "Project",
                field: "name",
                op: "==",
                value: this.project.name,
              },
            ],
          }),
        }).then((response) => {
          if (response.data.items.length) {
            this.project_faq = response.data.items[0]
          }
        })
      }
    },
    ...mapActions("incident", ["report", "get", "resetSelected"]),
  },

  created() {
    if (this.$route.query.project) {
      let params = {
        filter: { field: "name", op: "==", value: this.$route.query.project },
      }
      // get full project object from api
      ProjectApi.getAll(params).then((response) => {
        if (response.data.items.length && !this.project) {
          this.project = response.data.items[0]
        }
      })
    } else if (this.projects.length && !this.project) {
      this.project = this.projects[0].project
    } else {
      // if no user projects stored yet, get the default project for the user
      // if no default user project, then get the default project for the organization
      AuthApi.getUserInfo().then((response) => {
        if (this.project) {
          // if the user has already selected something, exit
          return
        }
        let default_user_project = response.data.projects.filter((v) => v.default === true)
        if (default_user_project.length) {
          this.project = default_user_project[0].project
        } else if (this.default_project) {
          this.project = this.default_project
        } else {
          let default_params = {
            filter: { field: "default", op: "==", value: true },
          }
          ProjectApi.getAll(default_params).then((response) => {
            if (response.data.items.length && !this.project) {
              this.project = response.data.items[0]
            }
          })
        }
      })
    }

    if (this.$route.query.incident_type) {
      this.incident_type = { name: this.$route.query.incident_type }
    }

    if (this.$route.query.incident_priority) {
      this.incident_priority = { name: this.$route.query.incident_priority }
    }

    if (this.$route.query.title) {
      this.title = this.$route.query.title
    }

    if (this.$route.query.description) {
      this.description = this.$route.query.description
    }

    if (this.$route.query.tag) {
      if (Array.isArray(this.$route.query.tag)) {
        this.tags = this.$route.query.tag.map(function (t) {
          return { name: t }
        })
      } else {
        this.tags = [{ name: this.$route.query.tag }]
      }
    }

    this.getFAQ()

    this.$watch(
      (vm) => [vm.project],
      () => {
        this.getFAQ()
      }
    )

    this.$watch(
      (vm) => [
        vm.project,
        vm.incident_priority,
        vm.incident_type,
        vm.title,
        vm.description,
        vm.local_commander,
        vm.tags,
      ],
      () => {
        if (Array.isArray(this.local_commander))
          this.commander_email = this.local_commander[0].individual.email
        var queryParams = {
          project: this.project ? this.project.name : null,
          incident_priority: this.incident_priority ? this.incident_priority.name : null,
          incident_type: this.incident_type ? this.incident_type.name : null,
          title: this.title,
          description: this.description,
          tag: this.tags ? this.tags.map((tag) => tag.name) : null,
          commander_email: this.commander_email,
        }
        Object.keys(queryParams).forEach((key) => (queryParams[key] ? {} : delete queryParams[key]))
        router
          .replace({
            query: queryParams,
          })
          .catch((err) => {
            // Updating the query fields also updates the URL.
            // Frequent updates to these fields throws navigation cancelled failures.
            if (isNavigationFailure(err, NavigationFailureType.cancelled)) {
              // resolve error
              return err
            }
            // rethrow error
            return Promise.reject(err)
          })
      }
    )
  },
}
</script>

<style scoped>
.preview-wrapper {
  overflow-y: auto;
  flex-grow: 1;
  max-height: 70vh;
}

.preview {
  border: 1px solid #ccc;
  border-radius: 16px;
  padding: 1rem;
  margin: 1rem;
  background: #f9f9f9;
  min-height: 100%;
  overflow: auto;
}

.form-wrapper {
  background-color: #f0f0f0;
  min-height: 100vh;
  padding: 2rem 0;
}

.v-card {
  background-color: white !important;
  border-radius: 16px;
}

.v-card-title {
  text-transform: uppercase;
  color: white;
  background: #bbbcc3;
  height: 43px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.v-icon {
  color: white;
}

.v-row {
  gap: 30px;
}

.v-btn {
  background-color: white;
  height: 28px;
  width: 28px;
  margin: 5px;
}

::v-deep(.tiptap a) {
  color: #1e88e5;
  text-decoration: underline;
}
</style>
