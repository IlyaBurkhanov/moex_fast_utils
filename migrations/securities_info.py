"""
TABLES WITH SECURITIES INFO
"""

security_description = """
CREATE TABLE IF NOT EXISTS security_description (
    SECID varchar(150) NOT NULL,
    "NAME" varchar(800) NULL,
    SHORTNAME varchar(400) NULL,
    ISIN varchar(100) NULL,
    REGNUMBER varchar(400) NULL,
    ISSUESIZE bigint NULL,
    FACEVALUE NUMERIC(19, 8) NULL,
    FACEUNIT varchar(50) NULL,
    ISSUEDATE date NULL,
    LATNAME varchar(500) NULL,
    LISTLEVEL smallint NULL,
    ISQUALIFIEDINVESTORS smallint NULL default 0,
    TYPENAME varchar(500) NULL,
    "GROUP" varchar(100) NULL,
    "TYPE" varchar(100) NULL,
    GROUPNAME varchar(100) NULL,
    EMITTER_ID varchar(200) NULL,
    PRIMARY KEY (SECID)
);
CREATE INDEX IF NOT EXISTS security_description_idx ON security_description 
    USING gin ("NAME" gin_trgm_ops, SHORTNAME gin_trgm_ops, ISIN gin_trgm_ops);
"""

security_boards = """
CREATE TABLE IF NOT EXISTS security_boards (
    secid varchar(150) NOT NULL,
    boardid varchar(12) NOT NULL,
    title varchar(400) NOT NULL,
    board_group_id integer NULL,
    market_id integer NULL,
    market varchar(45) NULL,
    engine_id integer NULL,
    engine varchar(45) NOT NULL,
    is_traded smallint NULL,
    decimals integer NULL,
    history_from date NULL,
    history_till date NULL,
    listed_from date NULL,
    listed_till date NULL, 
    is_primary smallint NULL,
    currencyid varchar(10) NULL,
    UNIQUE (secid, boardid)
);
CREATE INDEX IF NOT EXISTS security_boards_idx ON security_boards (
    secid, boardid, market, engine, is_traded, is_primary
);
"""