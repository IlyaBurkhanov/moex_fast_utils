
GET_SECID_INFO = """
SELECT secid,
    "NAME",
    shortname,
    isin,
    regnumber,
    issuesize,
    facevalue,
    faceunit,
    issuedate,
    latname,
    listlevel,
    isqualifiedinvestors,
    typename,
    "GROUP",
    "TYPE",
    groupname,
    emitter_id
FROM security_description
WHERE %s = $1
"""

INSERT_INTO_SECURITY = """
INSERT INTO security_description(
    secid,
    "NAME",
    shortname,
    isin,
    regnumber,
    issuesize,
    facevalue,
    faceunit,
    issuedate,
    latname,
    listlevel,
    isqualifiedinvestors,
    typename,
    "GROUP",
    "TYPE",
    groupname,
    emitter_id
)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
ON CONFLICT DO NOTHING
"""

SECURITY_COLUMNS = [
    "SECID",
    "NAME",
    "SHORTNAME",
    "ISIN",
    "REGNUMBER",
    "ISSUESIZE",
    "FACEVALUE",
    "FACEUNIT",
    "ISSUEDATE",
    "LATNAME",
    "LISTLEVEL",
    "ISQUALIFIEDINVESTORS",
    "TYPENAME",
    "GROUP",
    "TYPE",
    "GROUPNAME",
    "EMITTER_ID",
]
