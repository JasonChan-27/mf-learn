{{- define "mf-metrics-ingestion.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "mf-metrics-ingestion.fullname" -}}
{{- printf "%s" (include "mf-metrics-ingestion.name" .) -}}
{{- end -}}
