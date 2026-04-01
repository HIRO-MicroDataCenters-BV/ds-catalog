{{/*
Expand the name of the chart.
*/}}
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "app.labels" -}}
helm.sh/chart: {{ include "app.chart" . }}
{{ include "app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "app.commonEnv" }}
- name: DS__CATALOG__TITLE
  value: "{{ .Values.catalog.title }}"
- name: DS__CATALOG__DESCRIPTION
  value: "{{ .Values.catalog.description }}"
- name: DS__DATABASE__PROTOCOL
  value: "{{ .Values.database.protocol }}"
- name: DS__DATABASE__HOST
  value: "{{ .Values.database.host }}"
- name: DS__TEST_DATABASE__PORT
  value: "{{ .Values.database.port }}"
- name: DS__TEST_DATABASE__NAME
  value: "{{ .Values.database.name }}"
- name: DS__DATABASE__USERNAME
  value: "{{ .Values.database.username }}"
- name: DS__DATABASE__PASSWORD
  value: "{{ .Values.database.password }}"
- name: DS__OCA_REPOSITORY_BUNDLES_URL
  value: "{{ .Values.baseUrls.ocaRepositoryBundlesUrl }}"
- name: DS__CONNECTOR_BASE_URL
  value: "{{ .Values.baseUrls.connectorBaseUrl }}"
- name: DS__ALLOWED_VALUES_CONFIG_PATH
  value: "{{ .Values.allowedValuesConfigPath }}"
{{- end }}


{{/*
Create the image name
*/}}
{{- define "app.image" -}}
{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}
{{- end }}
