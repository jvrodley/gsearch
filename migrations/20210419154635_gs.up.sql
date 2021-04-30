CREATE TABLE "ori" (
                        oriid serial primary key,
                        externalid varchar(255) not null,
                        agency_name varchar(255) NOT NULL,
                        location_name varchar(255) NOT NULL,
                        agency_type varchar(255) NOT NULL,
                        state varchar(2),
                        state_full varchar(100),
                        total_population varchar(100),
                        police_union_contract_link varchar(1024),
                        sort_order int
);

ALTER TABLE url ADD COLUMN oriid_ori int;
