import torch
import tt_lib as ttl
from tests.python_api_testing.models.utility_functions_new import (
    comp_allclose_and_pcc,
    comp_pcc,
)
from loguru import logger
import pytest


@pytest.mark.parametrize(
    "input_shape, kernel_size, stride, padding, dilation, return_indices, ceil_mode, on_device",
    (
        (torch.Size([1, 2, 6, 8]), (2, 4), None, 0, 1, False, False, False),
        (torch.Size([1, 2, 6, 8]), (2, 4), None, 0, 1, False, False, True),
        (torch.Size([2, 1, 32, 64]), 6, None, 0, 1, False, False, False),
        (torch.Size([2, 1, 32, 64]), 6, None, 0, 1, False, False, False),
    ),
)
def test_MaxPool2d_fallback(
    input_shape,
    kernel_size,
    stride,
    padding,
    dilation,
    return_indices,
    ceil_mode,
    on_device,
):
    torch.manual_seed(1234)
    host = ttl.device.GetHost()
    device = ttl.device.CreateDevice(ttl.device.Arch.GRAYSKULL, 0)
    ttl.device.InitializeDevice(device)

    x = torch.randn(input_shape).bfloat16().float()
    pt_nn = torch.nn.MaxPool2d(
        kernel_size, stride, padding, dilation, return_indices, ceil_mode
    )
    pt_out = pt_nn(x)

    # Test on host RM
    t0 = ttl.tensor.Tensor(
        x.reshape(-1).tolist(),
        x.shape,
        ttl.tensor.DataType.BFLOAT16,
        ttl.tensor.Layout.ROW_MAJOR,
    )
    if on_device:
        t0 = t0.to(device)

    tt_nn = ttl.fallback_ops.MaxPool2d(
        kernel_size,
        stride,
        padding,
        dilation,
        return_indices,
        ceil_mode,
    )
    t1 = tt_nn(t0)

    output = torch.Tensor(t1.to(host).to(ttl.tensor.Layout.ROW_MAJOR).data()).reshape(
        t1.shape()
    )
    comp_pass, _ = comp_pcc(pt_out, output, 0.9999)
    _, comp_out = comp_allclose_and_pcc(pt_out, output)
    logger.info(comp_out)
    assert comp_pass

    del t1

    ttl.device.CloseDevice(device)
