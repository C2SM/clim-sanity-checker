colors = {
    'black' : "\033[30m",
    'green' : "\033[32m",
    'orange' : "\033[93m",
    'red' : "\x1b[31;21m",
    'bold_red' : "\x1b[31;1m",
    'red_highl' : "\u001b[41m",
    'reset' : "\x1b[0m"
    }

class style():
    '''define colors for output on terminal'''

    BLACK = lambda x: colors['black'] + str(x) + colors['reset']
    GREEN = lambda x: colors['green'] + str(x) + colors['reset']
    ORANGE = lambda x: colors['orange'] + str(x) + colors['reset']
    RED = lambda x: colors['red'] + str(x) + colors['reset']
    BOLD_RED = lambda x: colors['bold_red'] + str(x) + colors['reset']
    RED_HIGHL = lambda x: colors['red_highl'] + str(x) + colors['reset']


if __name__ == '__main__':
    print(colors)
    print(style.ORANGE('shshsh'))
    print(style.GREEN('shshsh'))
    print(style.BOLD_RED('shshsh'))
    print('test')
