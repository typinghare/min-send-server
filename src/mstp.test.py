import unittest
from src.mstp import MSTPMessage


class MSTPTest(unittest.TestCase):
    def test_parse(self):
        """
        Test MSTPMessage parsing.
        """

        message = """
        REQ user-sign-in
        time=1703847211
        username=5511ca17-e592-4090-a170-35fc7426c470
        pin=4302
        
        Nothing
        """.strip()
        mstp_message = MSTPMessage.parse(message)
        self.assertEqual(mstp_message.type, MSTPMessage.TYPE_REQ)
        self.assertEqual(mstp_message.action, "user-sign-in")

        headers = mstp_message.headers
        self.assertEqual(headers.get('time'), '1703847211')
        self.assertEqual(headers.get('username'), '5511ca17-e592-4090-a170-35fc7426c470')
        self.assertEqual(headers.get('pin'), '4302')

        self.assertEqual(mstp_message.data, 'Nothing')


if __name__ == '__main__':
    unittest.main()
