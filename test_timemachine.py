import tempfile, unittest
from pathlib import Path
from timemachine import History
class HistoryTests(unittest.TestCase):
    def test_round_trip_and_dedup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'source'; root.mkdir(); (root/'hello.txt').write_text('first\n')
            h=History(root); a=h.snapshot('first'); h.snapshot('identical')
            self.assertEqual(len(list((h.store/'objects').iterdir())),1)
            (root/'hello.txt').write_text('second\n'); b=h.snapshot('second')
            self.assertIn('-first',h.diff(a,b)); self.assertIn('+second',h.diff(a,b))
            h.restore(a,Path(tmp)/'restored')
            self.assertEqual((Path(tmp)/'restored/hello.txt').read_text(),'first\n')
            with self.assertRaises(FileExistsError): h.restore(a,root)
    def test_rejects_revision_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): History(tmp).load('../../x')
if __name__=='__main__': unittest.main()
