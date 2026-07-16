"""
用户管理模块白盒测试脚本
测试对象：User模型核心方法 + UserRegister密码复杂度校验
运行方式：cd D:/FitnessGraduationProject/02_Backend; python -m unittest tests/test_user_methods.py -v
"""

import unittest
from datetime import datetime, date
from unittest.mock import patch

from pydantic import ValidationError

from app.models.user import User, FitnessGoalEnum, ExperienceLevelEnum, GenderEnum
from app.schemas.user import UserRegister


class MockDateTime(datetime):
    _fixed_now = None

    @classmethod
    def now(cls, tz=None):
        if cls._fixed_now is not None:
            return cls._fixed_now
        return super().now(tz)

    @classmethod
    def set_fixed_now(cls, fixed):
        cls._fixed_now = fixed

    @classmethod
    def reset(cls):
        cls._fixed_now = None


class TestCalculateBMI(unittest.TestCase):

    def setUp(self):
        self.user = User(
            user_id="test_bmi_001",
            name="BMI测试用户",
            phone="13800000001",
            password_hash="hashed_pwd"
        )

    def test_calculate_bmi_normal(self):
        self.user.height = 175.0
        self.user.weight = 70.0
        result = self.user.calculate_bmi()
        expected = round(70.0 / ((175.0 / 100) ** 2), 2)
        self.assertEqual(result, expected)
        self.assertEqual(result, 22.86)

    def test_calculate_bmi_zero_height(self):
        self.user.height = 0.0
        self.user.weight = 70.0
        result = self.user.calculate_bmi()
        self.assertIsNone(result)

    def test_calculate_bmi_negative_height(self):
        self.user.height = -10.0
        self.user.weight = 70.0
        result = self.user.calculate_bmi()
        self.assertIsNone(result)

    def test_calculate_bmi_none_height(self):
        self.user.height = None
        self.user.weight = 70.0
        result = self.user.calculate_bmi()
        self.assertIsNone(result)

    def test_calculate_bmi_none_weight(self):
        self.user.height = 175.0
        self.user.weight = None
        result = self.user.calculate_bmi()
        self.assertIsNone(result)

    def test_calculate_bmi_both_none(self):
        self.user.height = None
        self.user.weight = None
        result = self.user.calculate_bmi()
        self.assertIsNone(result)


class TestCalculateAge(unittest.TestCase):

    def setUp(self):
        self.user = User(
            user_id="test_age_001",
            name="年龄测试用户",
            phone="13800000002",
            password_hash="hashed_pwd"
        )

    def test_calculate_age_birthday_passed(self):
        self.user.birthday = datetime(2000, 3, 15)
        MockDateTime.set_fixed_now(datetime(2026, 5, 9))
        with patch('app.models.user.datetime', MockDateTime):
            result = self.user.calculate_age()
        MockDateTime.reset()
        self.assertEqual(result, 26)

    def test_calculate_age_birthday_not_passed(self):
        self.user.birthday = datetime(2000, 12, 25)
        MockDateTime.set_fixed_now(datetime(2026, 5, 9))
        with patch('app.models.user.datetime', MockDateTime):
            result = self.user.calculate_age()
        MockDateTime.reset()
        self.assertEqual(result, 25)

    def test_calculate_age_birthday_today(self):
        self.user.birthday = datetime(2000, 5, 9)
        MockDateTime.set_fixed_now(datetime(2026, 5, 9))
        with patch('app.models.user.datetime', MockDateTime):
            result = self.user.calculate_age()
        MockDateTime.reset()
        self.assertEqual(result, 26)

    def test_calculate_age_no_birthday(self):
        self.user.birthday = None
        self.user.age = 30
        result = self.user.calculate_age()
        self.assertEqual(result, 30)

    def test_calculate_age_no_birthday_age_none(self):
        self.user.birthday = None
        self.user.age = None
        result = self.user.calculate_age()
        self.assertIsNone(result)

    def test_calculate_age_birthday_date_object(self):
        self.user.birthday = date(2000, 6, 15)
        MockDateTime.set_fixed_now(datetime(2026, 5, 9))
        with patch('app.models.user.datetime', MockDateTime):
            result = self.user.calculate_age()
        MockDateTime.reset()
        self.assertEqual(result, 25)


class TestIsProfileComplete(unittest.TestCase):

    def setUp(self):
        self.user = User(
            user_id="test_complete_001",
            name="完整性测试用户",
            phone="13800000003",
            password_hash="hashed_pwd"
        )

    def test_is_profile_complete_all_fields(self):
        self.user.birthday = datetime(2000, 1, 1)
        self.user.gender = GenderEnum.MALE
        self.user.height = 175.0
        self.user.weight = 70.0
        self.user.fitness_goal = FitnessGoalEnum.MUSCLE_GAIN
        self.user.experience_level = ExperienceLevelEnum.ADVANCED
        result = self.user.is_profile_complete()
        self.assertTrue(result)

    def test_is_profile_complete_missing_birthday(self):
        self.user.birthday = None
        self.user.gender = GenderEnum.MALE
        self.user.height = 175.0
        self.user.weight = 70.0
        self.user.fitness_goal = FitnessGoalEnum.MUSCLE_GAIN
        self.user.experience_level = ExperienceLevelEnum.ADVANCED
        result = self.user.is_profile_complete()
        self.assertFalse(result)

    def test_is_profile_complete_missing_gender(self):
        self.user.birthday = datetime(2000, 1, 1)
        self.user.gender = None
        self.user.height = 175.0
        self.user.weight = 70.0
        self.user.fitness_goal = FitnessGoalEnum.MUSCLE_GAIN
        self.user.experience_level = ExperienceLevelEnum.ADVANCED
        result = self.user.is_profile_complete()
        self.assertFalse(result)

    def test_is_profile_complete_missing_height(self):
        self.user.birthday = datetime(2000, 1, 1)
        self.user.gender = GenderEnum.MALE
        self.user.height = None
        self.user.weight = 70.0
        self.user.fitness_goal = FitnessGoalEnum.MUSCLE_GAIN
        self.user.experience_level = ExperienceLevelEnum.ADVANCED
        result = self.user.is_profile_complete()
        self.assertFalse(result)

    def test_is_profile_complete_missing_weight(self):
        self.user.birthday = datetime(2000, 1, 1)
        self.user.gender = GenderEnum.MALE
        self.user.height = 175.0
        self.user.weight = None
        self.user.fitness_goal = FitnessGoalEnum.MUSCLE_GAIN
        self.user.experience_level = ExperienceLevelEnum.ADVANCED
        result = self.user.is_profile_complete()
        self.assertFalse(result)

    def test_is_profile_complete_missing_fitness_goal(self):
        self.user.birthday = datetime(2000, 1, 1)
        self.user.gender = GenderEnum.MALE
        self.user.height = 175.0
        self.user.weight = 70.0
        self.user.fitness_goal = None
        self.user.experience_level = ExperienceLevelEnum.ADVANCED
        result = self.user.is_profile_complete()
        self.assertFalse(result)

    def test_is_profile_complete_missing_experience_level(self):
        self.user.birthday = datetime(2000, 1, 1)
        self.user.gender = GenderEnum.MALE
        self.user.height = 175.0
        self.user.weight = 70.0
        self.user.fitness_goal = FitnessGoalEnum.MUSCLE_GAIN
        self.user.experience_level = None
        result = self.user.is_profile_complete()
        self.assertFalse(result)

    def test_is_profile_complete_all_missing(self):
        self.user.birthday = None
        self.user.gender = None
        self.user.height = None
        self.user.weight = None
        self.user.fitness_goal = None
        self.user.experience_level = None
        result = self.user.is_profile_complete()
        self.assertFalse(result)


class TestValidatePassword(unittest.TestCase):

    def test_validate_password_pass(self):
        user = UserRegister(
            phone="13800000001",
            password="Test123!@",
            confirm_password="Test123!@"
        )
        self.assertEqual(user.password, "Test123!@")

    def test_validate_password_no_special_char(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegister(
                phone="13800000001",
                password="Abc12345",
                confirm_password="Abc12345"
            )
        error_messages = str(ctx.exception)
        self.assertIn("特殊符号", error_messages)

    def test_validate_password_no_uppercase(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegister(
                phone="13800000001",
                password="abc123!@",
                confirm_password="abc123!@"
            )
        error_messages = str(ctx.exception)
        self.assertIn("大写字母", error_messages)

    def test_validate_password_no_lowercase(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegister(
                phone="13800000001",
                password="ABC123!@",
                confirm_password="ABC123!@"
            )
        error_messages = str(ctx.exception)
        self.assertIn("小写字母", error_messages)

    def test_validate_password_no_digit(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegister(
                phone="13800000001",
                password="Abcdef!@",
                confirm_password="Abcdef!@"
            )
        error_messages = str(ctx.exception)
        self.assertIn("数字", error_messages)

    def test_validate_password_too_short(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegister(
                phone="13800000001",
                password="Abc1!@",
                confirm_password="Abc1!@"
            )
        error_messages = str(ctx.exception)
        self.assertIn("8", error_messages)

    def test_validate_password_confirm_mismatch(self):
        with self.assertRaises(ValidationError) as ctx:
            UserRegister(
                phone="13800000001",
                password="Test123!@",
                confirm_password="Test123!#"
            )
        error_messages = str(ctx.exception)
        self.assertIn("不一致", error_messages)

    def test_validate_password_all_conditions_met_various(self):
        valid_passwords = [
            "Abc123!@",
            "Xyz789#$",
            "Passw0rd+=",
            "MyP@ss1d",
            "Aa1!Aa1!"
        ]
        for pwd in valid_passwords:
            user = UserRegister(
                phone="13800000001",
                password=pwd,
                confirm_password=pwd
            )
            self.assertEqual(user.password, pwd)


class TestUpdateAgeFromBirthday(unittest.TestCase):

    def setUp(self):
        self.user = User(
            user_id="test_update_age_001",
            name="年龄更新测试用户",
            phone="13800000004",
            password_hash="hashed_pwd"
        )

    def test_update_age_from_birthday(self):
        self.user.birthday = datetime(2000, 3, 15)
        self.user.age = None
        MockDateTime.set_fixed_now(datetime(2026, 5, 9))
        with patch('app.models.user.datetime', MockDateTime):
            self.user.update_age_from_birthday()
        MockDateTime.reset()
        self.assertEqual(self.user.age, 26)

    def test_update_age_from_birthday_none(self):
        self.user.birthday = None
        self.user.age = 30
        self.user.update_age_from_birthday()
        self.assertEqual(self.user.age, 30)


if __name__ == '__main__':
    unittest.main()
