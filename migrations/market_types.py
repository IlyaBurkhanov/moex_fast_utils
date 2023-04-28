"""
GLOBAL DICTIONARIES ABOUT MARKET AND INSTRUMENTS TYPE
"""

engines = """
CREATE TABLE IF NOT EXISTS engines (
    id integer NOT NULL,
    name varchar(45) NOT NULL,
    title varchar(765),
    PRIMARY KEY (id)
)
"""

markets = """
CREATE TABLE IF NOT EXISTS markets (
    id integer NOT NULL,
    trade_engine_id integer NOT NULL,
    trade_engine_name varchar(45) NULL,
    trade_engine_title varchar(765) NULL,
    market_name varchar(45) NULL,
    market_title varchar(765) NULL,
    market_id integer NULL,
    marketplace varchar(48) NULL,
    is_otc integer NOT NULL,
    has_history_files integer NOT NULL,
    has_history_trades_files integer NOT NULL,
    has_trades integer NOT NULL,
    has_history integer NOT NULL,
    has_candles integer NOT NULL,
    has_orderbook integer NOT NULL,
    has_tradingsession integer NOT NULL,
    has_extra_yields integer NOT NULL,
    has_delay integer NOT NULL,
    PRIMARY KEY (id)
)
"""

boards = """
CREATE TABLE IF NOT EXISTS boards (
    id integer NOT NULL,
    board_group_id integer NOT NULL,
    engine_id integer NOT NULL,
    market_id integer NOT NULL,
    boardid varchar(12) NOT NULL,
    board_title varchar(381) NULL,
    is_traded integer NOT NULL,
    has_candles integer NOT NULL,
    is_primary integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_board_group FOREIGN KEY (board_group_id) references boardgroups(id) ON DELETE CASCADE,
    CONSTRAINT fk_engine FOREIGN KEY (engine_id) references engines(id) ON DELETE CASCADE,
    CONSTRAINT fk_market FOREIGN KEY (market_id) references markets(id) ON DELETE CASCADE
);
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS boardid_idx ON boards USING gin (boardid gin_trgm_ops);
"""

boardgroups = """
CREATE TABLE IF NOT EXISTS boardgroups (
    id integer NOT NULL,
    trade_engine_id integer NOT NULL,
    trade_engine_name varchar(45) NOT NULL,
    trade_engine_title varchar(765) NOT NULL,
    market_id integer NOT NULL,
    market_name varchar(45) NULL,
    name varchar(192) NOT NULL,
    title varchar(765) NULL,
    is_default integer NOT NULL,
    board_group_id integer NULL,
    is_traded integer NULL,
    is_order_driven integer NULL,
    category varchar(55) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_engine FOREIGN KEY (trade_engine_id) references engines(id) ON DELETE CASCADE,
    CONSTRAINT fk_market FOREIGN KEY (market_id) references markets(id) ON DELETE SET NULL
)
"""

durations = """
CREATE TABLE IF NOT EXISTS durations (
    interval integer NOT NULL,
    duration integer NOT NULL,
    days integer NULL,
    title varchar(765) NULL,
    hint  varchar(765) NULL
)
"""

securitytypes = """
CREATE TABLE IF NOT EXISTS securitytypes (
    id integer NOT NULL,
    trade_engine_id integer NOT NULL,
    trade_engine_name varchar(45) NULL,
    trade_engine_title varchar(765) NULL,
    security_type_name varchar(93) NOT NULL,
    security_type_title varchar(765) NULL,
    security_group_name varchar(93) NULL,
    stock_type varchar(10) NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_engine FOREIGN KEY (trade_engine_id) references engines(id) ON DELETE CASCADE
)
"""

securitygroups = """
CREATE TABLE IF NOT EXISTS securitygroups (
    id integer NOT NULL,
    name varchar(93) NOT NULL,
    title varchar(765) NULL,
    is_hidden integer NOT NULL,
    PRIMARY KEY (id)
)
"""

securitycollections = """
CREATE TABLE IF NOT EXISTS securitycollections (
    id integer NOT NULL,
    name varchar(96) NOT NULL,
    title varchar(765) NULL,
    security_group_id integer NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_security_group FOREIGN KEY (security_group_id) references securitygroups(id) ON DELETE CASCADE
)
"""
