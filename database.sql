drop table if exists predictions;

CREATE TABLE predictions (
    Hours_studied REAL,
    sleep REAL,
    attendance REAL
);

select * from predictions;

insert into predictions (Hours_studied, sleep, attendance) values
(5.5, 7.0, 90.0),
(3.0, 6.5, 80.0),
(8.0, 8.0, 95.0),
(2.5, 5.0, 70.0);

IF OBJECT_ID('predictions', 'U') IS NOT NULL
    DROP TABLE predictions;
