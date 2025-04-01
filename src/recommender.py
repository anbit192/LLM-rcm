import numpy as np


class Recommender:
    _instance = None

    def __init__(self, index, movie_list, k_per_item=5, output_k=10, negative_thres=3, negative_alpha=-1):
        self.index = index
        self.movie_list = movie_list
        self.k_per_item = k_per_item + 1
        self.output_k = output_k
        self.negative_thres = negative_thres
        self.negative_alpha = negative_alpha

    @classmethod
    def get_instance(cls, index, movie_list, k_per_item=5, output_k=10, negative_thres=3, negative_alpha=-1):
        if (cls._instance is None):
            cls._instance = cls(index, movie_list, k_per_item,
                                output_k, negative_thres, negative_alpha)
        return cls._instance

    def _similar_search(self, movie):
        embed_input = self.index.reconstruct(movie["vectorID"])
        D, I = self.index.search(np.array([embed_input]), self.k_per_item)

        return D, I

    def _get_rcm_ranking(self):
        user_dislike = []
        user_like = []
        recommend_dict = {}

        for movieId, row in self.movie_list.iterrows():

            m_rating = row["rating"]
            m_weight_rating = row["weight_rating"]

            combine_rating = 0.9 * m_rating + 0.1 * m_weight_rating

            D, I = self._similar_search(row)

            rcm_ids = I.flatten().tolist()[1:]

            rcm_dists = D.flatten().tolist()[1:]

            for id_, dist_ in zip(rcm_ids, rcm_dists):

                if (m_rating < self.negative_thres):
                    if (id_ in user_like):
                        continue

                    user_dislike.append(row["vectorID"])
                    wgt = (combine_rating + self.negative_alpha *
                           (5 - m_rating)) * dist_

                    recommend_dict[id_] = recommend_dict.get(id_, 0) + wgt
                else:
                    user_like.append(row["vectorID"])

                    wgt = combine_rating * dist_

                    recommend_dict[id_] = recommend_dict.get(id_, 0) + wgt

        print(user_dislike)
        for id_ in set(user_dislike):
            recommend_dict.pop(id_, -1)

        sorted_candidates = sorted(recommend_dict.items(),
                                   key=lambda x: x[1], reverse=True)

        return sorted_candidates

    def set_movie_list(self, movie_list):
        self.movie_list = movie_list

    def get_top_k(self):
        res = self._get_rcm_ranking()
        return [id_ for id_, _ in res[:self.output_k]]
