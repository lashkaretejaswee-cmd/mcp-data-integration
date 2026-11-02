-- Run with: psql postgres -f db/setup.sql
CREATE DATABASE mcp_integration;
\c mcp_integration

CREATE TABLE employees (
    employee_id  VARCHAR(10) PRIMARY KEY,
    name         VARCHAR(100),
    department   VARCHAR(50),
    salary       INTEGER,
    access_level VARCHAR(20),
    created_at   TIMESTAMP DEFAULT NOW()
);

INSERT INTO employees VALUES
  ('E001','Tejaswee Lashkare','Engineering',95000,'admin',NOW()),
  ('E002','Bob Smith','Analytics',75000,'analyst',NOW()),
  ('E003','Charlie Brown','Operations',45000,'intern',NOW()),
  ('E004','Diana Prince','Engineering',98000,'admin',NOW()),
  ('E005','Eve Johnson','Analytics',72000,'analyst',NOW()),
  ('E006','Frank Miller','Operations',43000,'intern',NOW());
