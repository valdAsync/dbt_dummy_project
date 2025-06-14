SELECT *
FROM {{ source('raw_dwh', 'customers') }}
