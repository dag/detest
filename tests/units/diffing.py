import detest


@detest.test
def diffs(diff):
    result = diff.env.differ.diff(diff.left, diff.right, 'left', 'right')
    if result is None:
        assert diff.expected is None
    else:
        assert result.strip() == diff.expected
