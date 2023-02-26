from typing import List, Dict, Any
from pandas import DataFrame
from tqdm import tqdm

class OpenFoodFactParser():
    
    def __init__(self, data:List[Dict[str, Any]]):
        self.data = data
        
    def to_df(self)->DataFrame:
        data_ = {}
        for product in tqdm(self.data):
            id_ = product['_id']
            data_[id_] = {}
            for k, v in product.items():
                if isinstance(v, list):
                    data_[id_][k] = ';'.join(v)
                elif isinstance(v, dict):
                    data_[id_][k] = ';'.join([f'{k_}:{v_}' for k_, v_ in v.items()])
                if isinstance(v, (str, int, float)):
                    data_[id_][k] = v
        df = DataFrame.from_dict(data_, orient='index').set_index('_id')
        df.index.name = 'code'
        return df