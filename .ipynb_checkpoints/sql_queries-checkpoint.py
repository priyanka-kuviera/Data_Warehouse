import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# GLOBAL VARIABLES
LOG_DATA = config.get("S3","LOG_DATA")
LOG_PATH = config.get("S3", "LOG_JSONPATH")
SONG_DATA = config.get("S3", "SONG_DATA")
IAM_ROLE = config.get("IAM_ROLE","ARN")

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay_facttable"
user_table_drop = "DROP TABLE IF EXISTS user_dimtable"
song_table_drop = "DROP TABLE IF EXISTS song_dimtable"
artist_table_drop = "DROP TABLE IF EXISTS artist_dimtable"
time_table_drop = "DROP TABLE IF EXISTS time_dimtable"

# CREATE TABLES

staging_events_table_create= ("""
CREATE TABLE IF NOT EXISTS staging_events
(
artist          VARCHAR,
auth            VARCHAR, 
firstName       VARCHAR,
gender          VARCHAR,   
itemInSession   INTEGER,
lastName        VARCHAR,
length          FLOAT,
level           VARCHAR, 
location        VARCHAR,
method          VARCHAR,
page            VARCHAR,
registration    BIGINT,
sessionId       INTEGER,
song            VARCHAR,
status          INTEGER,
ts              TIMESTAMP,
userAgent       VARCHAR,
userId          INTEGER
);
""")

staging_songs_table_create = ("""
CREATE TABLE IF NOT EXISTS staging_songs
(
song_id            VARCHAR,
num_songs          INTEGER,
title              VARCHAR,
artist_name        VARCHAR,
artist_latitude    FLOAT,
year               INTEGER,
duration           FLOAT,
artist_id          VARCHAR,
artist_longitude   FLOAT,
artist_location    VARCHAR
);
""")

songplay_table_create = ("""
CREATE TABLE IF NOT EXISTS songplay_facttable
(
songplay_id          INTEGER IDENTITY(0,1) PRIMARY KEY sortkey,
start_time           varchar NOT NULL,
user_id              INTEGER NOT NULL,
level                VARCHAR,
song_id              VARCHAR NOT NULL,
artist_id            VARCHAR NOT NULL,
session_id           INTEGER,
location             VARCHAR,
user_agent           VARCHAR
);
""")

user_table_create = ("""
CREATE TABLE IF NOT EXISTS user_dimtable
(
user_id INTEGER PRIMARY KEY distkey NOT NULL,
first_name      VARCHAR,
last_name       VARCHAR,
gender          VARCHAR,
level           VARCHAR
);
""")

song_table_create = ("""
CREATE TABLE IF NOT EXISTS song_dimtable
(
song_id     VARCHAR PRIMARY KEY NOT NULL,
title       VARCHAR,
artist_id   VARCHAR distkey NOT NULL,
year        INTEGER,
duration    FLOAT
);
""")

artist_table_create = ("""
CREATE TABLE IF NOT EXISTS artist_dimtable
(
artist_id          VARCHAR PRIMARY KEY distkey NOT NULL,
name               VARCHAR,
location           VARCHAR,
latitude           FLOAT,
longitude          FLOAT
);
""")

time_table_create = ("""
CREATE TABLE IF NOT EXISTS time_dimtable
(
start_time    varchar PRIMARY KEY sortkey distkey NOT NULL,
hour          INTEGER,
day           INTEGER,
week          INTEGER,
month         INTEGER,
year          INTEGER,
weekday       INTEGER
);
""")
# STAGING TABLES

staging_events_copy = ("""
    COPY staging_events FROM {}
    CREDENTIALS 'aws_iam_role={}'
    COMPUPDATE OFF region 'us-west-2'
    TIMEFORMAT as 'epochmillisecs'
    TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL
    FORMAT AS JSON {};
""").format(LOG_DATA, IAM_ROLE, LOG_PATH)

staging_songs_copy = ("""
    COPY staging_songs FROM {}
    CREDENTIALS 'aws_iam_role={}'
    COMPUPDATE OFF region 'us-west-2'
    FORMAT AS JSON 'auto' 
    TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL;
""").format(SONG_DATA, IAM_ROLE)


'''staging_events_copy = ("""
    COPY staging_events FROM {}
    iam_role {}
    COMPUPDATE OFF region 'us-west-2'
    TIMEFORMAT as 'epochmillisecs'
    TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL
    FORMAT AS JSON {};
""").format(LOG_DATA, IAM_ROLE, LOG_PATH)

staging_songs_copy = ("""
    COPY staging_songs FROM {}
    iam_role {}
    COMPUPDATE OFF region 'us-west-2'
    FORMAT AS JSON 'auto' 
    TRUNCATECOLUMNS BLANKSASNULL EMPTYASNULL;
""").format(SONG_DATA, IAM_ROLE)
'''
'''staging_events_copy = ("""
COPY staging_events FROM {}
iam_role {}
region 'us-west-2'
format as json {}
STATUPDATE ON ;
""").format(config.get('S3','LOG_DATA'), config.get('IAM_ROLE', 'ARN'),
config.get('S3','LOG_JSONPATH'))

staging_songs_copy = ("""
COPY staging_songs FROM {}
iam_role {}
region 'us-west-2'
JSON 'auto' ;
""").format(config.get('S3','SONG_DATA'), config.get('IAM_ROLE', 'ARN'))
'''
# FINAL TABLES

songplay_table_insert = ("""
INSERT INTO songplay_facttable(start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT DISTINCT to_timestamp(to_char(se.ts, '9999-99-99 99:99:99'),'YYYY-MM-DD HH24:MI:SS'),
                se.userId as user_id,
                se.level as level,
                ss.song_id as song_id,
                ss.artist_id as artist_id,
                se.sessionId as session_id,
                se.location as location,
                se.userAgent as user_agent
FROM staging_events se
JOIN staging_songs ss ON se.song = ss.title AND se.artist = ss.artist_name
WHERE se.userID IS NOT NULL AND se.page = 'NextSong';
""")

user_table_insert = ("""
INSERT INTO user_dimtable(user_id, first_name, last_name, gender, level)
SELECT DISTINCT userId as user_id,
                firstName as first_name,
                lastName as last_name,
                gender as gender,
                level as level
FROM staging_events
where page = 'NextSong';
""")

song_table_insert = ("""
INSERT INTO song_dimtable(song_id, title, artist_id, year, duration)
SELECT DISTINCT song_id as song_id,
                title as title,
                artist_id as artist_id,
                year as year,
                duration as duration
FROM staging_songs
WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artist_dimtable(artist_id, name, location, latitude, longitude)
SELECT DISTINCT artist_id as artist_id,
                artist_name as name,
                artist_location as location,
                artist_latitude as latitude,
                artist_longitude as longitude
FROM staging_songs
where artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO time_dimtable(start_time, hour, day, week, month, year, weekday)
SELECT distinct ts,
                EXTRACT(hour from ts),
                EXTRACT(day from ts),
                EXTRACT(week from ts),
                EXTRACT(month from ts),
                EXTRACT(year from ts),
                EXTRACT(weekday from ts)
FROM staging_events
WHERE ts IS NOT NULL;
""")


# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
