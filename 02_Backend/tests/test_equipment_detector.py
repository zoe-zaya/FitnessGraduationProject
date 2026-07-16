"""
健身房管理模块白盒测试脚本
测试对象：EquipmentDetector核心方法 + GymEquipment.get_target_muscles_list()
运行方式：cd D:/FitnessGraduationProject/02_Backend; python -m unittest tests/test_equipment_detector.py -v
"""

import unittest
import json
import numpy as np
import cv2
from unittest.mock import patch, MagicMock

from app.models.equipment import GymEquipment
from app.services.detection import EquipmentDetector


def _create_mock_detector():
    detector = object.__new__(EquipmentDetector)
    detector.session = MagicMock()
    detector.input_name = 'images'
    detector.input_shape = [1, 3, 640, 640]
    detector.confidence_threshold = 0.7
    return detector


class TestPreprocess(unittest.TestCase):

    def setUp(self):
        self.detector = _create_mock_detector()

    def test_preprocess_normal_image(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, encoded = cv2.imencode('.jpg', img)
        image_bytes = encoded.tobytes()
        batched, original_shape = self.detector.preprocess(image_bytes)
        self.assertEqual(batched.shape, (1, 3, 640, 640))
        self.assertEqual(original_shape, (480, 640))
        self.assertTrue(float(batched.max()) <= 1.0)
        self.assertTrue(float(batched.min()) >= 0.0)

    def test_preprocess_empty_image(self):
        image_bytes = b''
        with self.assertRaises((ValueError, cv2.error)):
            self.detector.preprocess(image_bytes)

    def test_preprocess_invalid_bytes(self):
        image_bytes = b'this_is_not_an_image'
        with self.assertRaises(ValueError) as ctx:
            self.detector.preprocess(image_bytes)
        self.assertIn("图片解码失败", str(ctx.exception))

    def test_preprocess_output_dtype(self):
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        _, encoded = cv2.imencode('.jpg', img)
        image_bytes = encoded.tobytes()
        batched, original_shape = self.detector.preprocess(image_bytes)
        self.assertEqual(batched.dtype, np.float32)
        self.assertEqual(original_shape, (300, 400))


class TestPostprocess(unittest.TestCase):

    def setUp(self):
        self.detector = _create_mock_detector()

    def test_postprocess_high_confidence(self):
        detection = np.zeros(85, dtype=np.float32)
        detection[0] = 0.5
        detection[1] = 0.5
        detection[2] = 0.3
        detection[3] = 0.3
        detection[4] = 0.89
        detection[5 + 6] = 1.0
        outputs = [np.array([[detection]])]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['equipment_id'], 'eq_6')
        self.assertAlmostEqual(results[0]['confidence'], 0.89, places=2)
        self.assertIn('box', results[0])
        self.assertEqual(len(results[0]['box']), 4)

    def test_postprocess_low_confidence(self):
        detection = np.zeros(85, dtype=np.float32)
        detection[4] = 0.42
        detection[5 + 6] = 1.0
        outputs = [np.array([[detection]])]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 0)

    def test_postprocess_confidence_at_threshold(self):
        detection = np.zeros(85, dtype=np.float32)
        detection[0] = 0.5
        detection[1] = 0.5
        detection[2] = 0.3
        detection[3] = 0.3
        detection[4] = 0.71
        detection[5 + 6] = 1.0
        outputs = [np.array([[detection]])]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 1)

    def test_postprocess_confidence_just_below_threshold(self):
        detection = np.zeros(85, dtype=np.float32)
        detection[4] = 0.699
        detection[5 + 6] = 1.0
        outputs = [np.array([[detection]])]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 0)

    def test_postprocess_multiple_detections(self):
        det1 = np.zeros(85, dtype=np.float32)
        det1[0] = 0.3
        det1[1] = 0.3
        det1[2] = 0.2
        det1[3] = 0.2
        det1[4] = 0.89
        det1[5 + 6] = 1.0

        det2 = np.zeros(85, dtype=np.float32)
        det2[0] = 0.7
        det2[1] = 0.7
        det2[2] = 0.2
        det2[3] = 0.2
        det2[4] = 0.42
        det2[5 + 3] = 1.0

        det3 = np.zeros(85, dtype=np.float32)
        det3[0] = 0.5
        det3[1] = 0.5
        det3[2] = 0.3
        det3[3] = 0.3
        det3[4] = 0.91
        det3[5 + 12] = 1.0

        outputs = [np.array([[det1, det2, det3]])]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['equipment_id'], 'eq_6')
        self.assertEqual(results[1]['equipment_id'], 'eq_12')

    def test_postprocess_empty_output(self):
        outputs = [np.zeros((1, 0, 85), dtype=np.float32)]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 0)

    def test_postprocess_box_coordinate_scaling(self):
        detection = np.zeros(85, dtype=np.float32)
        detection[0] = 320.0
        detection[1] = 240.0
        detection[2] = 100.0
        detection[3] = 100.0
        detection[4] = 0.85
        detection[5 + 0] = 1.0
        outputs = [np.array([[detection]])]
        original_shape = (480, 640)
        results = self.detector.postprocess(outputs, original_shape)
        self.assertEqual(len(results), 1)
        box = results[0]['box']
        expected_x1 = (320 - 50) / 640 * 640
        expected_y1 = (240 - 50) / 640 * 480
        self.assertAlmostEqual(box[0], expected_x1, places=1)
        self.assertAlmostEqual(box[1], expected_y1, places=1)


class TestDetect(unittest.TestCase):

    def setUp(self):
        self.detector = _create_mock_detector()

    def test_detect_empty_image_returns_empty_list(self):
        result = self.detector.detect(b'')
        self.assertEqual(result, [])

    def test_detect_invalid_bytes_returns_empty_list(self):
        result = self.detector.detect(b'not_an_image')
        self.assertEqual(result, [])

    def test_detect_valid_image_with_mock_inference(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, encoded = cv2.imencode('.jpg', img)
        image_bytes = encoded.tobytes()

        detection = np.zeros(85, dtype=np.float32)
        detection[0] = 0.5
        detection[1] = 0.5
        detection[2] = 0.3
        detection[3] = 0.3
        detection[4] = 0.89
        detection[5 + 6] = 1.0
        mock_output = np.array([[detection]])

        self.detector.session.run = MagicMock(return_value=[mock_output])
        results = self.detector.detect(image_bytes)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['equipment_id'], 'eq_6')
        self.assertAlmostEqual(results[0]['confidence'], 0.89, places=2)

    def test_detect_valid_image_all_low_confidence(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, encoded = cv2.imencode('.jpg', img)
        image_bytes = encoded.tobytes()

        detection = np.zeros(85, dtype=np.float32)
        detection[4] = 0.3
        detection[5 + 0] = 1.0
        mock_output = np.array([[detection]])

        self.detector.session.run = MagicMock(return_value=[mock_output])
        results = self.detector.detect(image_bytes)
        self.assertEqual(len(results), 0)

    def test_detect_valid_image_multiple_results(self):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        _, encoded = cv2.imencode('.jpg', img)
        image_bytes = encoded.tobytes()

        det1 = np.zeros(85, dtype=np.float32)
        det1[0] = 0.3
        det1[1] = 0.3
        det1[2] = 0.2
        det1[3] = 0.2
        det1[4] = 0.88
        det1[5 + 2] = 1.0

        det2 = np.zeros(85, dtype=np.float32)
        det2[0] = 0.7
        det2[1] = 0.7
        det2[2] = 0.2
        det2[3] = 0.2
        det2[4] = 0.91
        det2[5 + 8] = 1.0

        mock_output = np.array([[det1, det2]])
        self.detector.session.run = MagicMock(return_value=[mock_output])
        results = self.detector.detect(image_bytes)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['equipment_id'], 'eq_2')
        self.assertEqual(results[1]['equipment_id'], 'eq_8')


class TestGetTargetMusclesList(unittest.TestCase):

    def setUp(self):
        self.equipment = GymEquipment(
            equipment_id="eq_test_001",
            name="测试器材",
            category="力量"
        )

    def test_get_target_muscles_list_normal_json(self):
        self.equipment.target_muscles = json.dumps(["胸大肌", "三角肌"], ensure_ascii=False)
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, ["胸大肌", "三角肌"])

    def test_get_target_muscles_list_single_muscle(self):
        self.equipment.target_muscles = json.dumps(["股四头肌"], ensure_ascii=False)
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, ["股四头肌"])

    def test_get_target_muscles_list_invalid_json(self):
        self.equipment.target_muscles = "{invalid json"
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, [])

    def test_get_target_muscles_list_none(self):
        self.equipment.target_muscles = None
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, [])

    def test_get_target_muscles_list_empty_string(self):
        self.equipment.target_muscles = ""
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, [])

    def test_get_target_muscles_list_empty_array(self):
        self.equipment.target_muscles = "[]"
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, [])

    def test_get_target_muscles_list_nested_json(self):
        self.equipment.target_muscles = json.dumps({"muscles": ["胸大肌"]}, ensure_ascii=False)
        result = self.equipment.get_target_muscles_list()
        self.assertEqual(result, {"muscles": ["胸大肌"]})


if __name__ == '__main__':
    unittest.main()
