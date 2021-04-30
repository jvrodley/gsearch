ALTER TABLE url ADD COLUMN coversdetectives boolean default false;
ALTER TABLE url ADD COLUMN coverslieutenants boolean default false;
ALTER TABLE url ADD COLUMN agency_type varchar(255) default 'Police Department';

