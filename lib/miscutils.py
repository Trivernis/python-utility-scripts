class SearchEngine:
    """ A Search engine that searches a list of strings for
     specific string occurences. """

    def __init__(self, data: list):
        self.data = data

    def search(self, q: str) -> tuple:
        q = q.lower()
        _score_dic = {}

        # checking for query syntax
        if '"' in q:
            _static_q = q.split('"')[1::2]
            print("STATIC: {}".format(_static_q))
            _flex_q = q.split('"')[0::2]
            print("FLEX: {}".format(_flex_q))

            for _static_single in _static_q:  # search for whole term
                _score_dic.update(self._static_search(_static_single))

            for _flex_single in _flex_q:  # search for single words
                _score_dic.update(self._flex_search(_flex_single.split(' ')))
        else:
            _flex_q = q.split(' ')
            print("FLEX: {}".format(_flex_q))
            _score_dic.update(self._flex_search(_flex_q))

        returnable = sorted(_score_dic, key=_score_dic.get)
        returnable.reverse()
        return tuple(returnable)  # change into a tuple because the order matters

    def _flex_search(self, q: list, data: list=None) -> dict:  # single word search
        _rescore_dic = {}  # returnable score dictionary

        if not data:
            data = self.data

        if len(q) > 0:
            for entry in data:
                for sin_query in q:
                    if sin_query in entry.lower() and len(sin_query) > 0:
                        if entry not in _rescore_dic.keys():
                            _rescore_dic[entry] = 0
                        # for each appereance the rank score increases
                        _rescore_dic[entry] += (entry.lower().count(sin_query) / 10) + 0.9

        return _rescore_dic

    def _static_search(self, q: str, data: list=None) -> dict:  # whole term search
        _rescore_dic = {}

        if not data:
            data = self.data

        if len(q) > 0:
            for entry in data:
                if q in entry.lower():
                    if entry not in _rescore_dic.keys():
                        _rescore_dic[entry] = 0

                    _rescore_dic[entry] += (entry.lower().count(q) * 100)

        return _rescore_dic
