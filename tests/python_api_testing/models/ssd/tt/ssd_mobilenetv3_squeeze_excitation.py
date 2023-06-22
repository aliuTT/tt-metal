import torch
from torch import nn, Tensor
import tt_lib
from tt_lib.fallback_ops import fallback_ops
from python_api_testing.models.utility_functions_new import (
    torch_to_tt_tensor_rm,
    tt_to_torch_tensor,
)


class TtSqueezeExcitation(torch.nn.Module):
    def __init__(
        self,
        config,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 0,
        dilation: int = 1,
        state_dict=None,
        base_address="",
        device=None,
        host=None,
    ) -> None:
        super().__init__()
        self.device = device
        self.host = host

        self.avgpool = fallback_ops.AdaptiveAvgPool2d(1)
        weight_fc1 = torch_to_tt_tensor_rm(
            state_dict[f"{base_address}.fc1.weight"], device, put_on_device=False
        )
        bias_fc1 = torch_to_tt_tensor_rm(
            state_dict[f"{base_address}.fc1.bias"], device, put_on_device=False
        )
        self.fc1 = fallback_ops.Conv2d(
            weights=weight_fc1,
            biases=bias_fc1,
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
        )
        weight_fc2 = torch_to_tt_tensor_rm(
            state_dict[f"{base_address}.fc2.weight"], device, put_on_device=False
        )
        bias_fc2 = torch_to_tt_tensor_rm(
            state_dict[f"{base_address}.fc2.bias"], device, put_on_device=False
        )
        self.fc2 = fallback_ops.Conv2d(
            weights=weight_fc2,
            biases=bias_fc2,
            in_channels=out_channels,
            out_channels=in_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
        )
        self.activation = tt_lib.tensor.relu
        self.scale_activation = torch.nn.Hardsigmoid()

    def forward(self, input: tt_lib.tensor.Tensor) -> tt_lib.tensor.Tensor:
        scale = self.avgpool(input)
        scale = self.fc1(scale)
        scale = self.activation(scale)
        scale = self.fc2(scale)
        scale = tt_to_torch_tensor(scale, self.host)
        scale = self.scale_activation(scale)
        scale = torch_to_tt_tensor_rm(scale, self.host)
        final_out = tt_lib.tensor.bcast(
            input, scale, tt_lib.tensor.BcastOpMath.MUL, tt_lib.tensor.BcastOpDim.HW
        )
        return final_out
