SELECT *
FROM {{ source('raw_dwh', 'purchases') }}
