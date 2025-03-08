import torch
import numpy as np

def generate(pos_num,neg_num, TRN_PORTION):
    TRN_PORTION = 0.7
    pos_idxs =np.arange(pos_num)
    np.random.shuffle(pos_idxs)
    neg_idxs = np.arange(neg_num)
    np.random.shuffle(neg_idxs)
    pos_trn_idxs = pos_idxs[:int(pos_num*TRN_PORTION)]
    pos_tst_idxs = pos_idxs[int(pos_num*TRN_PORTION):]
    neg_trn_idxs = neg_idxs[:int(neg_num*TRN_PORTION)]
    neg_tst_idxs = neg_idxs[int(neg_num*TRN_PORTION):]
    return pos_trn_idxs, pos_tst_idxs, neg_trn_idxs, neg_tst_idxs


    


