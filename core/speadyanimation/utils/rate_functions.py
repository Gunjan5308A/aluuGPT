import math

def linear(t):
    return t

def smooth(t):
    s = 1 - t
    return (t ** 3) * (10 * s * s + 5 * s * t + t * t)

def smoothstep(t):
    return 3 * t * t - 2 * t * t * t

def smootherstep(t):
    return t * t * t * (t * (6 * t - 15) + 10)

def ease_in_quad(t):
    return t * t

def ease_out_quad(t):
    return 1 - (1 - t) ** 2

def ease_in_out_quad(t):
    if t < 0.5:
        return 2 * t * t
    return 1 - (-2 * t + 2) ** 2 / 2

def ease_in_cubic(t):
    return t * t * t

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2

def ease_in_quart(t):
    return t ** 4

def ease_out_quart(t):
    return 1 - (1 - t) ** 4

def ease_in_out_quart(t):
    if t < 0.5:
        return 8 * t ** 4
    return 1 - (-2 * t + 2) ** 4 / 2

def ease_in_expo(t):
    if t == 0:
        return 0
    return 2 ** (10 * t - 10)

def ease_out_expo(t):
    if t == 1:
        return 1
    return 1 - 2 ** (-10 * t)

def ease_in_out_expo(t):
    if t == 0:
        return 0
    if t == 1:
        return 1
    if t < 0.5:
        return 2 ** (20 * t - 10) / 2
    return (2 - 2 ** (-20 * t + 10)) / 2

def ease_in_sine(t):
    return 1 - math.cos(t * math.pi / 2)

def ease_out_sine(t):
    return math.sin(t * math.pi / 2)

def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2

def ease_in_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t * t * t - c1 * t * t

def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_in_out_back(t):
    c1 = 1.70158
    c2 = c1 * 1.525
    if t < 0.5:
        return ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    return ((2 * t - 2) ** 2 * ((c2 + 1) * (2 * t - 2) + c2) + 2) / 2

def ease_in_elastic(t):
    if t == 0:
        return 0
    if t == 1:
        return 1
    c4 = (2 * math.pi) / 3
    return -(2 ** (10 * t - 10)) * math.sin((t * 10 - 10.75) * c4)

def ease_out_elastic(t):
    if t == 0:
        return 0
    if t == 1:
        return 1
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

def ease_in_out_elastic(t):
    if t == 0:
        return 0
    if t == 1:
        return 1
    c5 = (2 * math.pi) / 4.5
    if t < 0.5:
        return -(2 ** (20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2
    return (2 ** (-20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1

def ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375

def ease_in_bounce(t):
    return 1 - ease_out_bounce(1 - t)

def ease_in_out_bounce(t):
    if t < 0.5:
        return (1 - ease_out_bounce(1 - 2 * t)) / 2
    return (1 + ease_out_bounce(2 * t - 1)) / 2

def there_and_back(t):
    if t < 0.5:
        return smooth(2 * t)
    return smooth(2 * (1 - t))

def there_and_back_with_pause(t, pause_ratio=1.0 / 3):
    a = 1.0 / (1 - pause_ratio)
    if t < 0.5 - pause_ratio / 2:
        return smooth(a * t)
    elif t < 0.5 + pause_ratio / 2:
        return 1
    return smooth(a - a * t)

def rush_into(t, inflection=10.0):
    return 2 * smooth(t / 2.0)

def rush_from(t, inflection=10.0):
    return 2 * smooth(t / 2.0 + 0.5) - 1

def double_smooth(t):
    if t < 0.5:
        return 2 * smooth(t)
    return 2 * smooth(1 - t)

def lingering(t):
    return smooth(smooth(t))

def not_quite_there(func=smooth, proportion=0.95):
    def result(t):
        return proportion * func(t)
    return result
