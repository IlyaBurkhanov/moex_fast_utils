

logs_session_security_history = """
DO $$ BEGIN
    CREATE TYPE log_status as enum ('wait', 'success', 'error');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;
CREATE TABLE IF NOT EXISTS logs_session_security_history(
    id bigserial,
    create_date timestamp default current_timestamp,
    engine varchar(45) NOT NULL,
    market  varchar(45) NOT NULL,
    session smallint NOT NULL default 3,
    secid varchar(150) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    status log_status NOT NULL,
    PRIMARY KEY (id),
    CHECK (start_date <= end_date),
    CHECK (end_date - start_date <= 3000),
    UNIQUE (engine, market, session, secid, start_date, end_date)
);
"""