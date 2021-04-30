ALTER TABLE url ADD COLUMN retrieved boolean default True;
ALTER TABLE url ALTER COLUMN searchtermid_searchterm DROP NOT NULL;
ALTER TABLE url ADD COLUMN startyear int default 0;
ALTER TABLE url ADD COLUMN city varchar(255) NULL;