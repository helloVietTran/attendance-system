-- init tables


-- init config data
INSERT INTO absence_types (name, code, is_paid) VALUES ('Nghỉ phép năm', 'VAC', 1);
INSERT INTO absence_types (name, code, is_paid) VALUES ('Nghỉ ốm', 'SICK', 1);

INSERT INTO system_settings (`key`, `value`, `description`) VALUES 
('lunch_break_start', '12:00', 'Giờ bắt đầu nghỉ trưa'),
('lunch_break_end', '13:30', 'Giờ kết thúc nghỉ trưa'),
('annual_paid_leave_days', '14', 'Số ngày nghỉ phép hưởng lương định mức hàng năm'),
('maternity_leave_months', '6', 'Thời gian nghỉ thai sản tính theo tháng'),
('max_attendance_correction_per_month', '3', 'Số lần tối đa nhân viên được phép gửi yêu cầu chỉnh sửa chấm công trong một tháng');

INSERT INTO shifts (name, start_time, end_time, work_value, is_active) VALUES 
('Ca Hành Chính 1', '08:30:00', '17:30:00', 1, 1),
('Ca Hành Chính 2', '09:00:00', '18:00:00', 1, 1);