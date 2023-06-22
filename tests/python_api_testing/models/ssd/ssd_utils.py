from tt_lib.fallback_ops import fallback_ops
from python_api_testing.models.utility_functions_new import torch_to_tt_tensor_rm


def create_batchnorm(out_ch, state_dict, base_address: str, device=None):
    weight = torch_to_tt_tensor_rm(
        state_dict[f"{base_address}.weight"], device, put_on_device=False
    )
    bias = torch_to_tt_tensor_rm(
        state_dict[f"{base_address}.bias"], device, put_on_device=False
    )
    running_mean = torch_to_tt_tensor_rm(
        state_dict[f"{base_address}.running_mean"], device, put_on_device=False
    )
    running_variance = torch_to_tt_tensor_rm(
        state_dict[f"{base_address}.running_var"], device, put_on_device=False
    )
    num_batches_tracked = torch_to_tt_tensor_rm(
        state_dict[f"{base_address}.num_batches_tracked"], device, put_on_device=False
    )
    norm = fallback_ops.BatchNorm2d(
        weight,
        bias,
        running_mean,
        running_variance,
        num_batches_tracked,
        out_ch,
        eps=0.001,
        momentum=0.01,
        affine=True,
        track_running_stats=True,
    )
    return norm
