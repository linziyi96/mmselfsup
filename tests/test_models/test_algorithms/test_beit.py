# Copyright (c) OpenMMLab. All rights reserved.
import platform

import pytest
import torch
from mmengine.data import InstanceData

from mmselfsup.models.algorithms import BEiT
from mmselfsup.structures import SelfSupDataSample

# model settings
backbone = dict(
    type='BEiTViT', arch='deit-b', beit_style=True, layer_scale_init_value=0.1)
neck = dict(
    type='BEiTNeck',
    num_classes=8192,
    embed_dims=768,
)
head = dict(
    type='BEiTHead',
    tokenizer_path='beit_ckpt/encoder_stat_dict.pth',
    loss=dict(type='BEiTLoss'))

data_preprocessor = dict(
    type='mmselfsup.CAEDataPreprocessor',
    mean=[124, 117, 104],
    std=[59, 58, 58],
    bgr_to_rgb=True)


@pytest.mark.skipif(platform.system() == 'Windows', reason='Windows mem limit')
def test_beit():
    model = BEiT(
        backbone=backbone,
        neck=neck,
        head=head,
        data_preprocessor=data_preprocessor)
    # model.init_weights()

    fake_img = torch.rand((3, 224, 224))
    fake_target_img = torch.rand((3, 112, 112))
    fake_mask = torch.zeros((196)).bool()
    fake_mask[75:150] = 1
    fake_data_sample = SelfSupDataSample()
    fake_mask = InstanceData(value=fake_mask)
    fake_data_sample.mask = fake_mask

    fake_data = [{
        'inputs': [fake_img, fake_target_img],
        'data_sample': fake_data_sample
    } for _ in range(2)]

    fake_batch_inputs, fake_data_samples = model.data_preprocessor(fake_data)
    fake_outputs = model(fake_batch_inputs, fake_data_samples, mode='loss')
    assert isinstance(fake_outputs['loss'].item(), float)