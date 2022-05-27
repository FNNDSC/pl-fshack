import unittest
from unittest.mock import Mock
from io import StringIO
from fshack._output import MultiSink, PrefixedSink


class MultiSinkTests(unittest.TestCase):
    def test_multi_sink(self):
        sinks = (StringIO(), StringIO(), StringIO())
        MultiSink(sinks).write('hello')
        for sink in sinks:
            self.assertEqual('hello', sink.getvalue())


class PrefixedSinkTests(unittest.TestCase):
    def test_no_output(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ', suffix='!')
        sink.write('')
        sink.flush()
        self.assertEqual('', output.getvalue())

    def test_single_newline(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ', suffix='!')
        sink.write('\n')
        self.assertEqual('narrator: !\n', output.getvalue())

        sink.flush()
        self.assertEqual('narrator: !\n', output.getvalue())

    def test_one_line(self):
        output = StringIO()
        output.close = Mock()  # prevent buffer from being discarded when closed

        with PrefixedSink(sink=output, prefix='narrator: ', suffix='!') as sink:
            sink.write('hello how do you do')
            sink.flush()
            self.assertEqual('narrator: hello how do you do', output.getvalue())

        self.assertEqual('narrator: hello how do you do!', output.getvalue())

    def test_two_lines(self):
        output = StringIO()
        output.close = Mock()  # prevent buffer from being discarded when closed

        with PrefixedSink(sink=output, prefix='narrator: ', suffix='!') as sink:
            sink.write('hello how do you do\n')
            sink.write('my name is unknown')
            expected = 'narrator: hello how do you do!\n'
            self.assertEqual(expected, output.getvalue())

        expected = 'narrator: hello how do you do!\nnarrator: my name is unknown!'
        self.assertEqual(expected, output.getvalue())

    def test_two_lines_with_latency(self):
        output = StringIO()
        output.close = Mock()  # prevent buffer from being discarded when closed

        with PrefixedSink(sink=output, prefix='narrator: ', suffix='!') as sink:
            sink.write('hello how do you ')
            self.assertEqual('', output.getvalue())
            sink.write('do\nmy ')
            self.assertEqual('narrator: hello how do you do!\n', output.getvalue())
            sink.write('name is unknown')
            self.assertEqual('narrator: hello how do you do!\n', output.getvalue())

        expected = 'narrator: hello how do you do!\nnarrator: my name is unknown!'
        self.assertEqual(expected, output.getvalue())

    def test_trailing_newline(self):
        output = StringIO()
        output.close = Mock()  # prevent buffer from being discarded when closed

        sink = PrefixedSink(sink=output, prefix='narrator: ', suffix='!')
        sink.write('hello how do you do\n')
        sink.write('my name is unknown\n')
        sink.write('\n')
        expected = 'narrator: hello how do you do!\nnarrator: my name is unknown!\nnarrator: !\n'
        self.assertEqual(expected, output.getvalue())


if __name__ == '__main__':
    unittest.main()
