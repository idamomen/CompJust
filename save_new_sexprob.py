def save_new_sexprob(prefix, n_meetings):
    ratios=[.1,.2,.3,.4,.5]
    for gender_ratio in ratios:
        print(gender_ratio)
        sexfaft, sexmaft = [],[]
        nsim = 1000
    # 1
    #with open(f'ratio{gender_ratio}_{n_meetings}meets_{nsim}nsim.pkl', 'rb') as input:
    # 2  [            anti_f_sexism, anti_m_sexism, 
    #                 sexf_bef, sexm_bef, 
    #                 sexf_aft,sexm_aft,
    #                 costsf,costsm, nsim, 
    #                 costfmeet, costmmeet]
        with open(f'{prefix}_ratio{gender_ratio}_0_{n_meetings}meets_{nsim}nsim.pkl', 'rb') as input:
            pickled_args = pickle.load(input)
            sexfaft, sexmaft = pickled_args[4],pickled_args[5]
            # turn into percentiles
            sexfaft.sort()
            sexmaft.sort()
            num=10
            chunkf=int(len(sexfaft)/10) 
            chunkm=int(len(sexmaft)/10)

            new_sexpf=[np.mean(sexfaft[i*(chunkf+1):i*(chunkf+1)+chunkf]) for i in range(num)]
            new_sexpm=[np.mean(sexmaft[i*(chunkm+1):i*(chunkm+1)+chunkm]) for i in range(num)]


            print(new_sexpm, new_sexpf)
            # save and use them in the next round
            env_sex_prob_args=(new_sexpm, new_sexpf)
            ###      pickle      ###
            with open('{prefix}_prob_{gender_ratio}_sex_prob_args.pkl', 'wb') as output:
                pickle.dump(env_sex_prob_args, output, pickle.HIGHEST_PROTOCOL)

