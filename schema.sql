drop table if exists entries;
drop table if exists comments;
drop table if exists users;

create table users(
    id integer primary key autoincrement,
    username string not null,
    -- This should be hashed at some point --
    password string not null
);

create table entries (
    id integer primary key autoincrement,
    title string not null,
    text  string not null
);

create table comments (
    id integer primary key autoincrement,
    parentid integer,
    email string not null,
    title string not null,
    text  string not null
);
