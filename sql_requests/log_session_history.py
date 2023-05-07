

raw_sql_get_requests_to_api_history = """
    WITH TMP AS (SELECT id,
                        row_number() over (order by start_date)        as position,
                        start_date,
                        end_date,
                        lead(start_date) over (order by start_date)    as next_date,
                        case when status = 'success' then 0 else 1 end as wait_status
                 FROM logs_session_security_history
                 WHERE secid = $1
                   AND engine = $2
                   AND market = $3
                   AND session = $4
                   AND (
                         start_date between $5 AND $6
                         OR end_date between $5 AND $6
                         OR (start_date <= $5  AND end_date >= $6)
                     ))
    
    SELECT id,
           wait_status,
           request_date
    FROM (SELECT null                                           id,
                 0                                              wait_status,
                 ARRAY [$5, start_date - 1]                     request_date
          FROM TMP
          WHERE position = 1
            and start_date > $5
          UNION ALL
          SELECT id,
                 wait_status,
                 CASE
                     WHEN end_date < $6 THEN
                         CASE
                             WHEN next_date is NULL THEN ARRAY[end_date + 1, $6]
                             ELSE CASE
                                      WHEN next_date - end_date > 1 THEN ARRAY[end_date + 1, next_date - 1]
                                 END
                             END
                     END as request_date
          FROM TMP
          UNION ALL
          SELECT null          as id,
                 0             as wait_status,
                 ARRAY[$5, $6] as request_date
          WHERE NOT exists(SELECT * FROM TMP)
    ) as t1
    WHERE request_date is not null
       or wait_status = 1
"""