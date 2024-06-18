# train building
#python train_vast.py -s datasets/Mill_19/building --exp_name building --manhattan --pos -62.527942657471 0.000000000000 -15.786898612976 --rot 0.932374119759 0.000000000000 0.361494839191 0.000000000000 1.000000000000 0.000000000000 -0.361494839191 0.000000000000 0.932374119759

# train rubble
# command="python train_multigpu.py -s ../datasets/Mill19/rubble --exp_name rubble --manhattan --pos 25.607364654541 0.000000000000 -12.012700080872 --rot 0.923032462597 0.000000000000 0.384722054005 0.000000000000 1.000000000000 0.000000000000 -0.384722054005 0.000000000000 0.923032462597 --num_gpus 2"

# train train
command="python train_multigpu.py -s ../datasets/tandt/train --exp_name train --manhattan --pos -7.70662571 4.45195873 0.51466437 --rot 0.86119716 0.03436749 0.50710779 0.03316087 0.99414171 -0.1028718 -0.50768368 0.10611482 0.85498364 --num_gpus 1"








nohup $command > log-6.13 2>&1 & echo $! > run.pid