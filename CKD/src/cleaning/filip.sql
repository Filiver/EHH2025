SELECT count() FROM (SELECT Dg, count(Dg) FROM diagnoses GROUP BY Dg);

SELECT Dg, count(Dg) count FROM diagnoses GROUP BY Dg ORDER BY count DESC;

SELECT Dg, count(Dg) count FROM diagnoses WHERE Dg REGEXP '[A-Z]+[0-9.]*:.*' GROUP BY Dg ORDER BY count ASC;

SELECT count() FROM diagnoses;

SELECT * FROM diagnoses;

SELECT * from reports NATURAL JOIN main.diagnoses ORDER BY ReportId;


SELECT * from reports NATURAL JOIN main.diagnoses ORDER BY ReportId;

SELECT * from labs;

SELECT * from transplantations WHERE Patient = 1517610;

ALTER TABLE transplantations ADD COLUMN small_intestine INTEGER DEFAULT 0 NOT NULL ;

UPDATE transplantations
SET small_intestine = 1
WHERE Organs LIKE '%tenké střevo%';

ALTER TABLE diagnoses ADD COLUMN dg_code VARCHAR(10) DEFAULT NULL;

UPDATE diagnoses
SET dg_code = null WHERE dg_code REGEXP '[A-Z]*';

UPDATE diagnoses
SET dg_code = 'CHOAP' WHERE Dg LIKE 'CHOAP%';

SELECT * FROM diagnoses WHERE dg like '%%';
SELECT * FROM medications where name like '%tbl%' and name not like '% tbl%';

SELECT Patient, count(Patient) FROM patients natural join diagnoses GROUP BY Patient