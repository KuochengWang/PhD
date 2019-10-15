import glob
import os
import pdb
import random
 
if __name__ == "__main__":
    inp_file = glob.glob('Jobs/*inp')
    num_job = len(inp_file)
    random.shuffle(inp_file)
    file = open("Jobs/error.txt","a+")
    pdb.set_trace()
    for inp in inp_file: 
        job_name = os.path.basename(inp)
        job_name = job_name.split('.')[0]
        er = os.system('abaqus j=' + job_name + ' interactive cpus=8 input=' + inp + '  double')
        if er != 0:
            file.write(str(inp) + '\n')
    file.close()
        