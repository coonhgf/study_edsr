import os
from data import srdata

class yh_sr_exp1(srdata.SRData):
    def __init__(self, args, name='yh_sr_exp1', train=True, benchmark=False):
        ### [y]
        print("[y] run yh_sr_exp1's __init__()")
        
        super(yh_sr_exp1, self).__init__(
            args, name=name, train=train, benchmark=benchmark
        )
        
        ### [y]
        print("[y] end yh_sr_exp1's __init__()")
        

    def _scan(self):
        ### [y]
        print("[y] start yh_sr_exp1's _scan()")
        
        names_hr, names_lr = super(yh_sr_exp1, self)._scasn()
        names_hr = glob.glob(os.path.join(self.dir_hr, '*' + self.ext[0]))
        names_hr.sort()
        print("len of names_hr={0}".format(len()))
        
        names_lr = []
        sub_name_lr = glob.glob(os.path.join(self.dir_lr, "{0}".format("X2"), '*' + self.ext[1]))
        sub_name_lr.sort()
        names_lr.append(sub_name_lr)
        print("len of names_lr={0}".format(len(names_lr)))
        print("len of names_lr[0]={0}".format(len(names_lr[0])))
        
        ### [y]
        print("[y] end yh_sr_exp1's _scan()")

        return names_hr, names_lr

    def _set_filesystem(self, dir_data):
        ### [y]
        print("[y] now in yh_sr_exp1's _set_filesystem()")
        
        super(yh_sr_exp1, self)._set_filesystem(dir_data)
        self.dir_hr = os.path.join(self.apath, 'yh_edsr_csh_axial_train_HR')
        self.dir_lr = os.path.join(self.apath, 'yh_edsr_csh_axial_train_LR_bicubic')
        if self.input_large: self.dir_lr += 'L'
        
        ### [y]
        print("[y] self.apath={0}".format(self.apath))
        print("[y] self.dir_hr={0}".format(self.dir_hr))
        print("[y] self.dir_lr={0}".format(self.dir_lr))
        ### [y]
        print("[y] end yh_sr_exp1's _set_filesystem()")

