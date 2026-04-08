{% macro generate_schema_name(custom_schema_name, node) -%}
    {#
        Override dbt's default schema naming so models land in the exact schema
        defined in dbt_project.yml (+schema: STAGING / INTERMEDIATE / MARTS)
        instead of <target_schema>_<custom_schema>.
    #}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | upper | trim }}
    {%- endif -%}
{%- endmacro %}
