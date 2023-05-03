
session_security_history = """
CREATE TABLE IF NOT EXISTS session_security_history(
    id bigserial,
    BOARDID varchar(12) NOT NULL,
    TRADEDATE date NOT NULL,
    SHORTNAME varchar(400) NULL,
    SECID varchar(150) NOT NULL,
    NUMTRADES bigint NOT NULL,
    VALUE double precision NULL, 
    OPEN double precision NULL, 
    LOW double precision NULL, 
    HIGH double precision NULL, 
    LEGALCLOSEPRICE double precision NULL, 
    WAPRICE double precision NULL, 
    CLOSE double precision NULL, 
    VOLUME double precision NULL, 
    MARKETPRICE2 double precision NULL, 
    MARKETPRICE3 double precision NULL, 
    ADMITTEDQUOTE double precision NULL, 
    MP2VALTRD double precision NULL, 
    MARKETPRICE3TRADESVALUE double precision NULL, 
    ADMITTEDVALUE double precision NULL, 
    WAVAL double precision NULL, 
    TRADINGSESSION smallint NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (BOARDID, TRADEDATE, SECID)
);
CREATE INDEX IF NOT EXISTS session_security_history_idx ON session_security_history (
    BOARDID, TRADEDATE, SECID
);
"""