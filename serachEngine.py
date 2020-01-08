import numpy as np
import pandas as pd
import re
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


class searchEngine:

    def __init__(self):
        self.df = pd.DataFrame()

    def get_json(self, json_doc):

        self.df = pd.read_json(json_doc)
        self.df.drop_duplicates(['name', 'address'], inplace=True)

        def unpack_cuisine(source, target=3, defaultValue=None):
            n = len(source)
            if n < target:
                return [*source, *([defaultValue] * (target - len(source)))]
            elif n > target:
                return source[0:target]
            else:
                return source

        self.df['cuisine_main_type'], self.df['cuisine_sub_type'], self.df['cuisine_minor_type'] = zip(
            *self.df['cuisine'].apply(lambda x: unpack_cuisine(x)))
        self.df.drop('cuisine', axis=1, inplace=True)

        columns = ['name',
                   'address',
                   'district',
                   'cuisine_main_type',
                   'cuisine_sub_type',
                   'cuisine_minor_type',
                   'available_condition',
                   'price-range',
                   'rating',
                   'bookmark',
                   'review_count',
                   'review_happy',
                   'review_okay',
                   'review_sad']

        self.df = self.df[columns]

    def search(self, filter_select):
        restaurant_list = self.df.copy()
        restaurant_to_remove = []

        if 'name' in filter_select:

            for i in range(len(self.df)):
                if filter_select['name'] != self.df['name'][i]:
                    restaurant_to_remove.append(i)

        if 'name_contain' in filter_select:

            for i in range(len(self.df)):
                flag = 0
                for pattern in range(len(filter_select['name_contain'])):
                    if re.search(filter_select['name_contain'][pattern], self.df['name'][i]):
                        break
                if flag == 0:
                    restaurant_to_remove.append(i)

        if 'country' in filter_select:

            for i in range(len(self.df)):
                if filter_select['country'] != self.df['cuisine_main_type'][i]:
                    restaurant_to_remove.append(i)

        if 'dish' in filter_select:

            for i in range(len(self.df)):
                if filter_select['dish'] != self.df['cuisine_sub_type'][i] and \
                        filter_select['dish'] != self.df['cuisine_minor_type'][i]:
                    restaurant_to_remove.append(i)

        if 'avail_cond' in filter_select:

            for i in range(len(self.df)):
                cond_count = len(self.df['available_condition'][i])
                for option in filter_select['avail_cond']:
                    if option not in self.df['available_condition'][i]:
                        cond_count = cond_count - 1

                if cond_count <= 0:
                    restaurant_to_remove.append(i)

        if 'price range' in filter_select:

            min_range = int(filter_select['price range'][0:filter_select['price range'].find('-')])

            max_range = int(filter_select['price range'][filter_select['price range'].find('-') + 1:])

            for i in range(len(self.df)):
                if self.df['price-range'][i] == 'Below $50':
                    price_min = 0
                    price_max = 50
                elif self.df['price-range'][i] == '$51-100':
                    price_min = 51
                    price_max = 100
                elif self.df['price-range'][i] == '$101-200':
                    price_min = 101
                    price_max = 200
                elif self.df['price-range'][i] == '$201-400':
                    price_min = 201
                    price_max = 400
                elif self.df['price-range'][i] == '$401-800':
                    price_min = 401
                    price_max = 800
                elif self.df['price-range'][i] == 'Above $801':
                    price_min = 801
                    price_max = 10000

                if price_min < min_range or price_max > max_range:
                    restaurant_to_remove.append(i)

        for index_remove in set(restaurant_to_remove):
            restaurant_list.drop(index=index_remove, axis=0, inplace=True)

        return restaurant_list

    def top_N_similar(self, restaurant, district, n):
        scale = StandardScaler()
        list_similar = []

        if (restaurant != None) & (district == None):
            target_idx = self.df[self.df['name'] == restaurant].index[0]

        elif (restaurant == None) & (district != None):
            target_idx = self.df[self.df['district'] == district].index[0]

        else:
            target_idx = self.df[(self.df['name'] == restaurant) & (self.df['district'] == district)].index[0]

        n = (n + 1) * -1

        df_avail_cond = self.df['available_condition'].str.join('|').str.get_dummies()
        df_sim = pd.concat([self.df, df_avail_cond], axis=1)
        df_sim.drop(['available_condition'], axis=1, inplace=True)

        df_sim_matrix = df_sim.drop(['name', 'address'], axis=1)
        df_sim_matrix = pd.get_dummies(df_sim_matrix, drop_first=True)

        df_sim_matrix.iloc[:, :6] = scale.fit_transform(df_sim_matrix.iloc[:, :6])

        df_sim['similarity'] = list(cosine_similarity(df_sim_matrix, dense_output=True))

        top_n_indices = np.argsort(df_sim['similarity'][target_idx])[n:]
        top_n_indices = top_n_indices[:-1]

        for index in top_n_indices:
            list_similar.append(self.df.iloc[index, :])

        df_sim_results = pd.DataFrame(list_similar)

        return df_sim_results
