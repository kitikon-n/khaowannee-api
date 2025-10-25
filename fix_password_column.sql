-- แก้ไข column password ให้รองรับ bcrypt hash (60 characters)
-- bcrypt hash มีความยาว 60 ตัวอักษร แต่แนะนำให้ใช้ 200 สำหรับอนาคต

ALTER TABLE su_user
ALTER COLUMN password TYPE VARCHAR(200);

-- ตรวจสอบผลลัพธ์
SELECT
    column_name,
    data_type,
    character_maximum_length
FROM information_schema.columns
WHERE table_name = 'su_user'
AND column_name = 'password';
