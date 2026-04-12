DROP TABLE IF EXISTS airline.flights;

CREATE TABLE airline.flights (
    id BIGSERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    quarter INTEGER,
    month INTEGER NOT NULL,
    day_of_month INTEGER,
    day_of_week INTEGER,
    flight_date DATE NOT NULL,

    marketing_airline_network TEXT,
    operated_or_branded_code_share_partners TEXT,
    dot_id_marketing_airline INTEGER,
    iata_code_marketing_airline TEXT,
    flight_number_marketing_airline TEXT,

    operating_airline TEXT,
    dot_id_operating_airline INTEGER,
    iata_code_operating_airline TEXT,
    tail_number TEXT,
    flight_number_operating_airline TEXT,

    origin_airport_id INTEGER,
    origin_airport_seq_id INTEGER,
    origin_city_market_id INTEGER,
    origin TEXT,
    origin_city_name TEXT,
    origin_state TEXT,
    origin_state_fips TEXT,
    origin_state_name TEXT,
    origin_wac INTEGER,

    dest_airport_id INTEGER,
    dest_airport_seq_id INTEGER,
    dest_city_market_id INTEGER,
    dest TEXT,
    dest_city_name TEXT,
    dest_state TEXT,
    dest_state_fips TEXT,
    dest_state_name TEXT,
    dest_wac INTEGER,

    crs_dep_time TEXT,
    dep_time TEXT,
    dep_delay DOUBLE PRECISION,
    dep_delay_minutes DOUBLE PRECISION,
    dep_del15 DOUBLE PRECISION,
    departure_delay_groups INTEGER,
    dep_time_blk TEXT,

    taxi_out DOUBLE PRECISION,
    wheels_off TEXT,
    wheels_on TEXT,
    taxi_in DOUBLE PRECISION,

    crs_arr_time TEXT,
    arr_time TEXT,
    arr_delay DOUBLE PRECISION,
    arr_delay_minutes DOUBLE PRECISION,
    arr_del15 DOUBLE PRECISION,
    arrival_delay_groups INTEGER,
    arr_time_blk TEXT,

    cancelled DOUBLE PRECISION,
    cancellation_code TEXT,
    diverted DOUBLE PRECISION,

    crs_elapsed_time DOUBLE PRECISION,
    actual_elapsed_time DOUBLE PRECISION,
    air_time DOUBLE PRECISION,
    flights DOUBLE PRECISION,
    distance DOUBLE PRECISION,
    distance_group INTEGER,

    carrier_delay DOUBLE PRECISION,
    weather_delay DOUBLE PRECISION,
    nas_delay DOUBLE PRECISION,
    security_delay DOUBLE PRECISION,
    late_aircraft_delay DOUBLE PRECISION,

    duplicate_flag TEXT
);

CREATE INDEX IF NOT EXISTS idx_flights_flight_date
    ON airline.flights (flight_date);

CREATE INDEX IF NOT EXISTS idx_flights_airline_date
    ON airline.flights (iata_code_marketing_airline, flight_date);

CREATE INDEX IF NOT EXISTS idx_flights_origin_date
    ON airline.flights (origin, flight_date);

CREATE INDEX IF NOT EXISTS idx_flights_dest_date
    ON airline.flights (dest, flight_date);

CREATE INDEX IF NOT EXISTS idx_flights_route_date
    ON airline.flights (origin, dest, flight_date);