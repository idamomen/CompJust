import numpy as np
import pickle
def get_new_sexism_probs(sexm_aft, sexf_aft):
    # Compute the new probabilities after conversations in 
    # a given environment
    # inputs
    # sexm_aft: sexism probability for men after conversations/meetings
    # sexf_aft: sexism probability for fen after conversations/meetings
    # output: pickled new probabilities for men and fem, in 10% percentiles

    a=np.asarray(sexm_aft)
    b=np.asarray(sexf_aft)
    a.sort()
    b.sort()
    # turning probabilities into 10 percentiles
    num=10
    chunk=int(len(a)/10) 
    chunkf=int(len(b)/10)

    new_sexpm=[np.mean(a[i*(chunk+1):i*(chunk+1)+chunk]) for i in range(num)]
    new_sexpf=[np.mean(b[i*(chunkf+1):i*(chunkf+1)+chunkf]) for i in range(num)]

    print(new_sexpm, new_sexpf)

    # save them and use them in the next round
    env_sex_prob_args=(new_sexpm, new_sexpf)
    import pickle
    with open('env_sex_prob_args.pkl', 'wb') as output:
        pickle.dump(env_sex_prob_args, output, pickle.HIGHEST_PROTOCOL)

