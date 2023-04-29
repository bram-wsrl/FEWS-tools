import unittest

from lib.dtypes import GroupSet


class TestGroupSet(unittest.TestCase):

    def test_groupset_no_sort_keys(self):
        gs1_amsterdam = GroupSet('Amsterdam')
        gs2_amsterdam = GroupSet('amsterdam')
        gs3_brussels = GroupSet('Brussels')

        self.assertTrue(gs1_amsterdam == gs2_amsterdam)
        self.assertTrue(gs1_amsterdam != gs3_brussels)

        self.assertEqual({gs1_amsterdam, gs2_amsterdam}, {gs1_amsterdam})
        self.assertEqual({gs1_amsterdam, gs3_brussels}, {gs1_amsterdam, gs3_brussels})

        sort_groupset = sorted([gs3_brussels, gs1_amsterdam], key=GroupSet.grouper)
        self.assertListEqual(sort_groupset, [gs1_amsterdam, gs3_brussels])

        exception_text = 'group_key takes string arguments only'
        with self.assertRaises(TypeError) as e:
            GroupSet(0)
        self.assertEqual(str(e.exception), exception_text)

        with self.assertRaises(TypeError) as e:
            GroupSet(['Amsterdam'])
        self.assertEqual(str(e.exception), exception_text)

        with self.assertRaises(TypeError) as e:
            GroupSet({})
        self.assertEqual(str(e.exception), exception_text)

    def test_groupset_single_sort_key(self):
        pass


if __name__ == '__main__':
    unittest.main()
