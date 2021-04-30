CREATE TABLE "searchterm" (
                        searchtermid serial primary key,
                        searchdate timestamp,
                        searchterm varchar(100) NOT NULL,
                        savecount int not null default 0,
                        dupecount int not null default 0,
                        resultcount int not null default 0,
                        done boolean default false,
                        lastresult int NOT NULL
);

CREATE TABLE "url" (
                        urlid serial primary key,
                        url varchar(255) not null,
                        searchtermid_searchterm int NOT NULL,
                        filename varchar(100),
                        knowntobeacontract bool default false,
                        state varchar(2),
                        municipalityoragency varchar(100),
                        error varchar(100),
                        searchdate timestamp
);

