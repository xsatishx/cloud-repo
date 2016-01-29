CREATE TABLE inode(
    id integer not null primary key autoincrement
);

CREATE TABLE file(
    id integer not null primary key autoincrement,
    parent integer not null references inode(id) ON DELETE CASCADE,
    real_location char(512) unique,
    name char(512) unique,
    owner references filesystem_user(id)
);

CREATE TABLE collection(
    id integer not null primary key autoincrement,
    parent integer not null references inode(id) ON DELETE CASCADE,
    name char(512) unique,
    owner references filesystem_user(id) 
);

CREATE TABLE collection2(
    id integer not null primary key autoincrement,
    parent integer not null references inode(id) ON DELETE CASCADE,
    name char(512) unique,
    owner references filesystem_user(id)
);

CREATE TABLE collection_file(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_ref INTEGER REFERENCES collection(id) ON DELETE CASCADE,
    file_ref INTEGER REFERENCES file(id) ON DELETE CASCADE,
    owner references filesystem_user(id)
);

CREATE TABLE collection2_collection(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection2_ref INTEGER REFERENCES collection2(id) ON DELETE CASCADE,
    collection_ref INTEGER REFERENCES collection(id) ON DELETE CASCADE,
    owner references filesystem_user(id)
);

CREATE TABLE abstract_user(
    id integer not null primary key AUTOINCREMENT
);

CREATE TABLE filesystem_user(
    id integer not null primary key autoincrement,
    parent integer not null references abstract_user(id) ON DELETE CASCADE,
    name char(512) unique
);

CREATE TABLE filesystem_group(
    id integer not null primary key autoincrement,
    parent integer not null references abstract_user(id) ON DELETE CASCADE,
    name char(512) unique,
    owner references filesystem_user(id)
);

CREATE TABLE filesystem_group_filesystem_user(
    id integer primary key autoincrement,
    filesystem_user_ref integer references filesystem_user(id) on delete cascade,
    filesystem_group_ref integer references filesystem_group(id) on delete cascade,
    owner references filesystem_user(id)
);

CREATE TABLE permission(
    id integer not null primary key AUTOINCREMENT,
    inode_ref INTEGER REFERENCES inode(id) ON DELETE CASCADE,
    user_ref INTEGER REFERENCES abstract_user(id) ON DELETE CASCADE,
    owner references filesystem_user(id)
); 
