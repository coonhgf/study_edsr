import torch

import utility
import data
import model
import loss
from option import args
from trainer import Trainer

torch.manual_seed(args.seed)
checkpoint = utility.checkpoint(args)

### [y]
import os
import sys
code_root_dp = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  ## src
sys.path.append(os.path.join(code_root_dp, "model"))
sys.path.append(os.path.join(code_root_dp, "data"))
from torchsummary import summary

def main():
    global model
    if args.data_test == ['video']:
        from videotester import VideoTester
        model = model.Model(args, checkpoint)
        t = VideoTester(args, model, checkpoint)
        t.test()
    else:
        if checkpoint.ok:
            loader = data.Data(args)
            _model = model.Model(args, checkpoint)
            ###
            summary(_model.model, (1, 2048, 1280, 3))
            exit(1)
            ###
            _loss = loss.Loss(args, checkpoint) if not args.test_only else None
            t = Trainer(args, loader, _model, _loss, checkpoint)
            while not t.terminate():
                ### [y]
                print("[y] going to call t.train()")
                t.train()
                
                ### [y]
                print("[y] going to call t.test()")
                t.test()

            checkpoint.done()

if __name__ == '__main__':
    main()
