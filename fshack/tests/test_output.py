import unittest
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
        sink = PrefixedSink(sink=output, prefix='narrator: ')
        sink.write('')
        self.assertEqual('', output.getvalue())

    def test_single_newline(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ')
        sink.write('\n')
        self.assertEqual('narrator: \n', output.getvalue())

    def test_one_line(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ')
        sink.write('hello how do you do')
        self.assertEqual('narrator: hello how do you do', output.getvalue())

    def test_two_lines(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ')
        sink.write('hello how do you do\n')
        sink.write('my name is unknown')
        expected = 'narrator: hello how do you do\nnarrator: my name is unknown'
        self.assertEqual(expected, output.getvalue())

    def test_two_lines_with_latency(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ')
        sink.write('hello how do you ')
        sink.write('do\nmy ')
        sink.write('name is unknown')
        expected = 'narrator: hello how do you do\nnarrator: my name is unknown'
        self.assertEqual(expected, output.getvalue())

    def test_trailing_newline(self):
        output = StringIO()
        sink = PrefixedSink(sink=output, prefix='narrator: ')
        sink.write('hello how do you do\n')
        sink.write('my name is unknown\n')
        sink.write('\n')
        expected = 'narrator: hello how do you do\nnarrator: my name is unknown\nnarrator: \n'
        self.assertEqual(expected, output.getvalue())


if __name__ == '__main__':
    unittest.main()
