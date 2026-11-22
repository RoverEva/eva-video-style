"""protagonist look per zodiac sign / MBTI type (fed into aries_char.STYLE)"""
ZODIAC = {
    'aries':       dict(horns='ram', hair='flame', back='sword', flower=False, extras=()),
    'taurus':      dict(horns='bull', hair='curly', back=None, flower=True, extras=()),
    'gemini':      dict(horns='none', hair='wave', back=None, flower=False, extras=('twinstar', 'twin')),
    'cancer':      dict(horns='none', hair='curly', back=None, flower=False, extras=('shell',)),
    'leo':         dict(horns='none', hair='mane', back=None, flower=False, extras=('crown',)),
    'virgo':       dict(horns='none', hair='long', back=None, flower=False, extras=('wheat',)),
    'libra':       dict(horns='none', hair='wave', back=None, flower=False, extras=('scales',)),
    'scorpio':     dict(horns='none', hair='short', back=None, flower=False, extras=('tail',)),
    'sagittarius': dict(horns='none', hair='flame', back='bow', flower=False, extras=()),
    'capricorn':   dict(horns='goat', hair='short', back=None, flower=False, extras=()),
    'aquarius':    dict(horns='none', hair='wave', back=None, flower=False, extras=('jar',)),
    'pisces':      dict(horns='none', hair='long', back=None, flower=False, extras=('fish',)),
}
MBTI_HAIR = {'INFJ': 'long', 'INFP': 'wave', 'ENFJ': 'short', 'ENFP': 'curly', 'INTJ': 'short', 'INTP': 'curly', 'ENTJ': 'short', 'ENTP': 'flame',
             'ISTJ': 'short', 'ISFJ': 'long', 'ESTJ': 'short', 'ESFJ': 'wave', 'ISTP': 'short', 'ISFP': 'wave', 'ESTP': 'flame', 'ESFP': 'curly'}


def mbti(t):
    ex = ('glasses',) if t[1:3] == 'NT' or t in ('ISTJ', 'INFJ') else ()
    return dict(horns='none', hair=MBTI_HAIR[t], back=None, flower=t in ('ISFP', 'INFP', 'ESFP'), extras=ex)
