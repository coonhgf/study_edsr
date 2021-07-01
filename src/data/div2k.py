import os
from data import srdata

class DIV2K(srdata.SRData):
    def __init__(self, args, name='DIV2K', train=True, benchmark=False):
        ### [y]
        print("run DIV2K's __init__()")
        
        data_range = [r.split('-') for r in args.data_range.split('/')]
        ### [y]
        print("ori data_range = {0}".format(data_range))
        
        if train:
            data_range = data_range[0]
        else:
            if args.test_only and len(data_range) == 1:
                data_range = data_range[0]
            else:
                data_range = data_range[1]
        ### [y]
        print("now data_range = {0}".format(data_range))

        self.begin, self.end = list(map(lambda x: int(x), data_range))
        
        ###[y]
        print("DIV2K, self.begin={0}".format(self.begin))
        print("DIV2K, self.end={0}".format(self.end))
        
        super(DIV2K, self).__init__(
            args, name=name, train=train, benchmark=benchmark
        )

    def _scan(self):
        names_hr, names_lr = super(DIV2K, self)._scan()
        names_hr = names_hr[self.begin - 1:self.end]
        names_lr = [n[self.begin - 1:self.end] for n in names_lr]
        
        ### [y]
        print("names_hr={0}".format(names_hr))
        print("names_lr={0}".format(names_lr))

        return names_hr, names_lr

    def _set_filesystem(self, dir_data):
        ### [y]
        print("now in DIV2K's _set_filesystem()")
        
        super(DIV2K, self)._set_filesystem(dir_data)
        self.dir_hr = os.path.join(self.apath, 'DIV2K_train_HR')
        self.dir_lr = os.path.join(self.apath, 'DIV2K_train_LR_bicubic')
        if self.input_large: self.dir_lr += 'L'
        
        ### [y]
        print("self.apath={0}".format(self.apath))
        print("self.dir_hr={0}".format(self.dir_hr))
        print("self.dir_lr={0}".format(self.dir_lr))

