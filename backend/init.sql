-- =========================
-- INSERT SHIFTS
-- =========================
INSERT INTO shifts (id, name, start_time, end_time, work_value, is_active)
VALUES
(1, 'Morning Shift', '08:00:00', '17:00:00', 480, 1),
(2, 'Evening Shift', '13:00:00', '22:00:00', 480, 1),
(3, 'Night Shift', '22:00:00', '06:00:00', 480, 1);

-- =========================
-- INSERT EMPLOYEES
-- =========================
INSERT INTO employees
(id, full_name, age, email, department_id, password_hash, dob, salary, shift_id, role, is_active)
VALUES
(1, 'Nguyen Van Admin', 35, 'admin@company.com', 1, 'hashed_admin_pw', '1991-03-10', 30000000, 1, 'ADMIN', 1),

(2, 'Tran Thi HR', 30, 'hr@company.com', 2, '123', '1995-07-15', 20000000, 1, 'HR', 1),

(3, 'Le Van A', 25, 'leva@company.com', 3, 'hashed_emp1_pw', '2000-01-12', 15000000, 1, 'EMPLOYEE', 1),

(4, 'Pham Thi B', 28, 'phamb@company.com', 3, 'hashed_emp2_pw', '1997-05-22', 16000000, 2, 'EMPLOYEE', 1);

-- =========================
-- INSERT ABSENCE TRACKERS
-- =========================
INSERT INTO absence_trackers
(employee_id, current_year_total, current_year_used,
 carried_over_from_last_year, carried_over_used, last_reset_year)
VALUES
(3, 12, 2, 3, 1, 2026),
(4, 12, 1, 2, 0, 2026);

-- =========================
-- INSERT ABSENCE PLANS
-- =========================
INSERT INTO absence_plans
(employee_id, start_date, end_date, absence_type,
 status, approved_by, approved_at, reason)
VALUES
(3, '2026-06-10', '2026-06-12', 'ANNUAL',
 'APPROVED', 2, NOW(), 'Du lich gia dinh'),

(4, '2026-07-01', '2026-07-03', 'WEDDING',
 'PENDING', NULL, NULL, 'Dam cuoi chi gai');

-- =========================
-- INSERT ABSENCES
-- =========================
INSERT INTO absences
(work_date, is_paid, created_at, updated_at,
 employee_id, absence_type)
VALUES
('2026-05-10', 1, NOW(), NOW(), 3, 'ANNUAL'),
('2026-05-11', 1, NOW(), NOW(), 3, 'ANNUAL');

-- =========================
-- INSERT ATTENDANCE LOGS
-- =========================
INSERT INTO attendance_logs
(employee_id, log_date, shift_start, shift_end, checked_time)
VALUES
(3, '2026-05-20', '08:00:00', '17:00:00', '07:55:00'),
(3, '2026-05-20', '08:00:00', '17:00:00', '17:10:00'),
(4, '2026-05-20', '13:00:00', '22:00:00', '13:05:00');

-- =========================
-- INSERT DAILY WORK REPORTS
-- =========================
INSERT INTO daily_work_reports
(employee_id, work_date, check_in, check_out,
 late_arrive_minutes, leave_early_minutes,
 lack_minutes, overtime_minutes,
 in_office_minutes, work_time_minutes, note)
VALUES
(3, '2026-05-20',
 '07:55:00', '17:10:00',
 0, 0,
 0, 10,
 555, 490,
 'Lam viec binh thuong'),

(4, '2026-05-20',
 '13:05:00', '22:00:00',
 5, 0,
 5, 0,
 535, 475,
 'Den muon 5 phut');

-- =========================
-- INSERT EMPLOYEE BENEFIT LOGS
-- =========================
INSERT INTO employee_benefit_logs
(employee_id, benefit_type, work_value,
 apply_date, description)
VALUES
(3, 'BONUS', 1000000, '2026-05-01', 'Thuong nhan vien xuat sac'),
(4, 'ALLOWANCE', 500000, '2026-05-01', 'Tro cap di lai');

-- =========================
-- INSERT FACE TEMPLATES: INSERT ON DEPLOYMENT
-- =========================


-- =========================
-- INSERT FIX ATTENDANCE REQUESTS
-- =========================
INSERT INTO fix_attendance_requests
(employee_id, work_date,
 requested_check_in, requested_check_out,
 reason, status, approved_by)
VALUES
(4, '2026-05-20',
 '13:00:00', '22:00:00',
 'Quen check-in do loi camera',
 'APPROVED', 2);

-- =========================
-- INSERT MONTHLY WORK REPORTS
-- =========================
INSERT INTO monthly_work_reports
(employee_id, period_start, period_end,
 standard_work_minutes,
 lack_minutes,
 estimated_minutes,
 actual_work_days,
 paid_leave_days,
 unpaid_leave_days)
VALUES
(3, '2026-05-01', '2026-05-31',
 10560, 0, 10600,
 22, 2, 0),

(4, '2026-05-01', '2026-05-31',
 10560, 30, 10530,
 21, 1, 1);

-- =========================
-- INSERT NOTIFICATIONS
-- =========================
INSERT INTO notifications
(employee_id, title, content,
 is_read, notification_type)
VALUES
(3, 'Thong bao OT',
 'Yeu cau OT cua ban da duoc phe duyet',
 0, 'OVERTIME'),

(4, 'Cham cong',
 'Yeu cau sua cham cong da duoc phe duyet',
 1, 'ATTENDANCE');

-- =========================
-- INSERT OVERTIME REQUESTS
-- =========================
INSERT INTO overtime_requests
(employee_id, work_date,
 actual_work_time,
 start_time, end_time,
 ot_type, multiplier,
 status, reason,
 approved_by, approved_at)
VALUES
(3, '2026-05-21',
 120,
 '18:00:00', '20:00:00',
 'NORMAL_DAY', 1.5,
 'APPROVED',
 'Hoan thanh deadline du an',
 2, NOW());

-- =========================
-- INSERT SHIFT CHANGE REQUESTS
-- =========================
INSERT INTO shift_change_requests
(employee_id,
 target_month, target_year,
 old_shift_id, new_shift_id,
 status, reason,
 processed_by, processed_at)
VALUES
(4,
 6, 2026,
 2, 1,
 'APPROVED',
 'Muon chuyen sang ca sang',
 2, NOW());

-- =========================
-- INSERT SYSTEM SETTINGS
-- =========================
INSERT INTO system_settings
(`key`, `value`, description)
VALUES
('standard_work_minutes_per_day', '480', 'So phut lam viec tieu chuan'),
('max_late_minutes', '15', 'So phut di muon toi da');

-- =========================
-- INSERT TIMESHEET PERIOD CONTROLS
-- =========================
INSERT INTO timesheet_period_controls
(month, year,
 closing_date,
 is_locked,
 locked_by,
 locked_at,
 note)
VALUES
(5, 2026,
 '2026-05-31',
 1,
 1,
 NOW(),
 'Da khoa bang cong thang 5');

-- =========================
-- INSERT VACATIONS
-- =========================
INSERT INTO vacations
(title, description,
 start_date, end_date,
 vacation_type,
 is_paid,
 is_recurring)
VALUES
('Tet Nguyen Dan',
 'Ky nghi Tet Am lich',
 '2026-02-15',
 '2026-02-21',
 'HOLIDAY',
 1,
 1),

('Team Building',
 'Su kien cong ty',
 '2026-08-10',
 '2026-08-12',
 'COMPANY_EVENT',
 1,
 0);

-- =========================
-- INSERT WORK COMPENSATIONS
-- =========================
INSERT INTO work_compensations
(title, compensate_date, description)
VALUES
('Bu ngay nghi Le 30/4',
 '2026-05-02',
 'Lam bu cho ngay nghi le');