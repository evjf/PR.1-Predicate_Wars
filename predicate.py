from dataclasses import dataclass
import re
from typing import Sequence, Tuple

def _checkSubSeq(subseq: Sequence, seq: Sequence) -> bool: #From https://stackoverflow.com/questions/425604/best-way-to-determine-if-a-sequence-is-in-another-sequence
    """
    Return if the subsequence is in the sequence.
    """
    i, n, m = -1, len(seq), len(subseq)
    if len(subseq) == 0: return True
    try:
        while True:
            i = seq.index(subseq[0], i + 1, n - m + 1)
            if subseq == seq[i:i + m]:
               return True
    except ValueError:
        return False

def _subSeqIndexes(subseq: Sequence, seq: Sequence) -> Tuple[int]: #From https://stackoverflow.com/questions/425604/best-way-to-determine-if-a-sequence-is-in-another-sequence
    """
    Return starting indexes of the subsequence in the sequence.
    """
    i, n, m = -1, len(seq), len(subseq)
    matches = []
    try:
        while True:
            i = seq.index(subseq[0], i + 1, n - m + 1)
            if subseq == seq[i:i + m]:
               matches.append(i)
    except ValueError:
        return tuple(matches)

def _checkSeqForm(seq: Sequence, start: Sequence, end: Sequence, mid: Sequence=()) -> bool:
    """
    Check the sequence if it is the form of [start..., ?, mid..., ?, end...].
    """
    if not (seq[:len(start)] == start): return False
    if not (seq[-len(end):] == end): return False
    if not _checkSubSeq(mid, seq[len(start):-len(end)]): return False
    return True

def _seqFormOptionalsIndexes(seq: Sequence, start: Sequence, end: Sequence, mid=()) -> Tuple[Tuple] | None:
    """
    Return indexes of optional sequences in the sequence of the seq form.
    """
    if _checkSeqForm(seq, start, end, mid):
        if len(mid) == 0:
            return ((len(start), len(seq) - len(end)),)
        else:
            return ((len(start), len(seq) - len(end)),
                tuple((index + len(start), index + len(start) + len(mid)) for index in _subSeqIndexes(mid, seq[len(start):-len(end)]))
            )
    return None


#Export constants and functions
gameFuncNames = [x.replace("[", "\[").replace("]", "\]") for x in ['[randPlayer]', '[randCard]', '[chosenPlayer]', '[chosenCard]', '[playerOfChosenCard]']]
predGFuncNames = [x.replace("[", "\[").replace("]", "\]") for x in ['[PLAYER]', '[CARD]', '[HEALTHLOWER]', '[HEALTHHIGHER]', '[POWERLOWER]', '[POWERHIGHER]', '[PROVPOWERLOWER]', '[PROVPOWERHIGHER]', '[SYMBOLPOINTLOWER]', '[SYMBOLPOINTHIGHER]']]
predAFuncNames = [x.replace("[", "\[").replace("]", "\]") for x in ['[CLAIM]', '[ATK]', '[HEAL]', '[ADDPOWER]', '[SUBPOWER]', '[ADDRULE]', '[DELETERULE]', '[ADDSUBPROOF]']]

varDetector = r'([a-z](_[0-9]+)?)|([0-9]+)'

symbolsType = (
    ('gameFuncName', '|'.join(gameFuncNames)),
    ('predGFuncName', '|'.join(predGFuncNames)),
    ('predAFuncName', '|'.join(predAFuncNames)),
    ('distVar', r'[a-z]_[0-9]+'),
    ('distPred', r'[A_Z]_[0-9]+'),
    ('truth', r't[TF]'),
    ('quanti', r'forall|exists'),
    ('connect', r'not | and | or | imply '),
    ('var', r'[a-z]'),
    ('pred', r'[A-Z]'),
    ('equal', r'='),
    ('comma', r','),
    ('bracket', r'[\(\)]'),
    ('number', r'[0-9]+'),
    ('space', r'\s'),
)

def symbolTypeCalc(symbol: str) -> str | None: return next((name for name, cond in symbolsType if re.match('^{}$'.format(cond), symbol)), None)

def symbolTrans(symbol: str) -> Tuple[str, ...] | None:
    symType = symbolTypeCalc(symbol)
    if symType == None:
        return None
    if symType == 'var':
        return (symType, str(ord(symbol.lower()) - ord('a') + 1))
    if symType == 'pred':
        return (symType, str(ord(symbol.lower()) - ord('a') + 1))
    if symType == 'distVar':
        return (symType, str(ord(symbol[0].lower()) - ord('a') + 1), symbol[2:])
    if symType == 'distPred':
        return (symType, str(ord(symbol[0].lower()) - ord('a') + 1), symbol[2:])
    if symType in ['gameFuncName', 'predGFuncName', 'predAFuncName', 'truth', 'quanti', 'connect', 'bracket', 'number']:
        return (symType, symbol)
    return (symType,)
@dataclass
class Statement:
    statement: Tuple[Tuple]

    @staticmethod
    def lex(string: str) -> 'Statement':
        """
        Tokenize statement from string.
        """
        tokens = []
        unLexed = string
        while unLexed != '':
            typeDetect = tuple(re.match(regex, unLexed) for _, regex in symbolsType)
            if any(x != None for x in typeDetect):
                typeDetectIndex = tuple(re.match(regex, unLexed).start() if re.match(regex, unLexed) else float('inf') for _, regex in symbolsType)
                nextTokenMatch = typeDetect[typeDetectIndex.index(min(typeDetectIndex))]
                nextToken = symbolTrans(nextTokenMatch.group())
                if nextToken != ('space',):
                    tokens.append(nextToken)
                unLexed = unLexed[nextTokenMatch.end():]
            else:
                raise ValueError("Invalid string")
        return Statement(tuple(tokens))

    def wellformed(self) -> bool:
        """
        Check whether the given token sequence is well formed.
        """
        #TODO: Implement this method
