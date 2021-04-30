ALTER TABLE url ADD COLUMN contractingunittype varchar(255) NULL;
ALTER TABLE url ADD COLUMN bargainingunitlocalname varchar(255) NULL;
ALTER TABLE url ADD COLUMN bargainingunitnationalname varchar(255) NULL;
ALTER TABLE url ADD COLUMN endyear int default 0;
ALTER TABLE url ADD COLUMN coverspatrol boolean default false;
ALTER TABLE url ADD COLUMN coverssergeants boolean default false;
ALTER TABLE url ADD COLUMN coverssuperiorofficers boolean default false;

